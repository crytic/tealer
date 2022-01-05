from typing import List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import BZ, Instruction
from tealer.teal.instructions.instructions import Return, Int, Txn, Eq, BNZ
from tealer.teal.instructions.transaction_field import OnCompletion, ApplicationID

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput


def _is_delete(ins1: Instruction, ins2: Instruction) -> bool:
    if isinstance(ins1, Int) and ins1.value == "DeleteApplication":
        return isinstance(ins2, Txn) and isinstance(ins2.field, OnCompletion)
    return False


def _is_oncompletion_check(ins1: Instruction, ins2: Instruction) -> bool:
    if isinstance(ins1, Txn) and isinstance(ins1.field, OnCompletion):
        return isinstance(ins2, Int) and ins2.value in [
            "UpdateApplication",
            "NoOp",
            "OptIn",
            "CloseOut",
        ]
    return False


def _is_application_creation_check(ins1: Instruction, ins2: Instruction) -> bool:
    """check if the instructions are application creation check.

    ApplicationID will be 0 at the time of creation as a result the condition
    txn ApplicationID == int 0 is generally used to do intialisation operations
    at the time of application creation.
    """
    if isinstance(ins1, Txn) and isinstance(ins1.field, ApplicationID):
        return isinstance(ins2, Int) and ins2.value == 0
    return False


class CanDelete(AbstractDetector):  # pylint: disable=too-few-public-methods
    NAME = "canDelete"
    DESCRIPTION = "Detect paths that can delete the application"
    TYPE = DetectorType.STATEFULL

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_TITLE = "Can Delete Application"
    WIKI_DESCRIPTION = "Detect paths that can delete the application"
    WIKI_EXPLOIT_SCENARIO = """
```
#pragma version 5
...
int NoOp
txn OnCompletion
==
bnz handle_noop
return 1 // return sucess for all other transaction types
handle_noop:
    ...
```

Algorand supports multiple types of application transactions. All types of application transactions execute the application
and fail if the execution fails. Additional to application execution, each application transaction type will result in different
operations before or after the application execution. This operations will be reverted if the approval program execution fails.

One of the application transaction type is DeleteApplication which
```
After executing the ApprovalProgram, delete the application parameters from the account data of the application's creator.
```

Ability to execute DeleteApplication transaction will give the ability to make application assets permanently inaccesible to anyone.

Attacker sends a DeleteApplication transaction and make assets inaccessible to everyone.
"""

    WIKI_RECOMMENDATION = """
Teal stores type of application transaction in `OnCompletion` transaction field, which can be accessed using `txn OnCompletion`.
Check if `txn OnCompletion == int DeleteApplication` and do appropriate actions based on the need.
"""

    def _check_delete(
        self,
        bb: BasicBlock,
        current_path: List[BasicBlock],
        paths_without_check: List[List[BasicBlock]],
    ) -> None:
        if bb in current_path:
            return

        current_path = current_path + [bb]

        # prev_was_oncompletion = False
        # prev_was_int = False
        prev_was_equal = False
        skip_false = False
        skip_true = False
        stack: List[Instruction] = []

        for ins in bb.instructions:

            if isinstance(ins, Return):
                if len(ins.prev) == 1:
                    prev = ins.prev[0]
                    if isinstance(prev, Int) and prev.value == 0:
                        return

                paths_without_check.append(current_path)
                return

            skip_false = isinstance(ins, BNZ) and prev_was_equal

            skip_true = isinstance(ins, BZ) and prev_was_equal

            prev_was_equal = False
            if isinstance(ins, Eq) and len(stack) >= 2:
                one = stack[-1]
                two = stack[-2]
                if _is_delete(one, two) or _is_delete(two, one):
                    return
                if _is_oncompletion_check(one, two) or _is_oncompletion_check(two, one):
                    prev_was_equal = True
                if _is_application_creation_check(one, two) or _is_application_creation_check(
                    two, one
                ):
                    prev_was_equal = True

            stack.append(ins)

        if skip_false:
            self._check_delete(bb.next[0], current_path, paths_without_check)
            return
        if skip_true:
            self._check_delete(bb.next[1], current_path, paths_without_check)
            return
        for next_bb in bb.next:
            self._check_delete(next_bb, current_path, paths_without_check)

    def detect(self) -> "SupportedOutput":

        paths_without_check: List[List[BasicBlock]] = []
        self._check_delete(self.teal.bbs[0], [], paths_without_check)

        description = "Lack of txn OnCompletion == int DeleteApplication check allows to"
        description += " delete the application."
        filename = "can_delete"

        return self.generate_result(paths_without_check, description, filename)
