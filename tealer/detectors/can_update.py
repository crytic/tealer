"""Detector for finding execution paths missing UpdateApplication."""

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
from tealer.utils.analyses import is_oncompletion_check

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput


def _is_update(ins1: Instruction, ins2: Instruction) -> bool:
    """Util function to check if given instructions form UpdateApplication check.

    Args:
        ins1: First instruction of the execution sequence that is supposed
            to form a comparison check for UpdateApplication.
        ins2: Second instruction in the execution sequence, will be executed
            right after :ins1:.

    Returns:
        True if the given instructions :ins1:, :ins2: form a UpdateApplication
        check i.e True if :ins1: is int UpdateApplication and :ins2: is
        txn OnCompletion.
    """

    if isinstance(ins1, Int) and ins1.value == "UpdateApplication":
        return isinstance(ins2, Txn) and isinstance(ins2.field, OnCompletion)
    return False


CHECKED_VALUES = [
    "DeleteApplication",
    "NoOp",
    "OptIn",
    "CloseOut",
]


def _is_application_creation_check(ins1: Instruction, ins2: Instruction) -> bool:
    """Check if the instructions form application creation check.

    ApplicationID will be 0 at the time of creation as a result the condition
    txn ApplicationID == int 0 is generally used to do intialization operations
    at the time of application creation. Updating or Deleting application isn't
    possible if the transaction is a application creation check. Using this check
    allows the UpdateApplication, DeleteApplication detector to not explore(pruning)
    paths where this check is true.

    Args:
        ins1: First instruction of the execution sequence that is supposed
            to form a comparison check for application creation.
        ins2: Second instruction in the execution sequence, will be executed
            right after :ins1:.

    Returns:
        True if the given instructions :ins1:, :ins2: form a application creation
        check i.e True if :ins1: is txn ApplicationID and :ins2: is
        int 0.
    """

    if isinstance(ins1, Txn) and isinstance(ins1.field, ApplicationID):
        return isinstance(ins2, Int) and ins2.value == 0
    return False


class CanUpdate(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find execution paths missing UpdateApplication check.

    Stateful smart contracts(application) can be updated with the new code
    in algorand. If the application transaction of type UpdateApplication is
    approved by the contract then the application's approval, clear programs
    will be replaced by the ones sent along with the transaction. Contracts
    can check the application transaction type using OnCompletion field.

    This detector tries to find execution paths that approve the application
    transactions("return 1") and doesn't check the OnCompletion field against
    UpdateApplication value. Execution paths that only execute if the application
    transaction is not UpdateApplication are excluded.
    """

    NAME = "canUpdate"
    DESCRIPTION = "Detect paths that can update the application"
    TYPE = DetectorType.STATEFULL

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_TITLE = "Can Update Application"
    WIKI_DESCRIPTION = "Detect paths that can update the application"
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

One of the application transaction type is UpdateApplication which
```
After executing the ApprovalProgram, replace the ApprovalProgram and ClearStateProgram associated with this application ID with the programs specified in this transaction.
```

Ability to execute UpdateApplication transaction will give complete control of application code, which controls all the assets held by the application.

Attacker sends a UpdateApplication transaction with the new approval program which transfers all the application assets to attacker's address using inner transaction.
"""

    WIKI_RECOMMENDATION = """
Teal stores type of application transaction in `OnCompletion` transaction field, which can be accessed using `txn OnCompletion`.
Check if `txn OnCompletion == int UpdateApplication` and do appropriate actions based on the need.
"""

    def _check_delete(
        self,
        bb: BasicBlock,
        current_path: List[BasicBlock],
        paths_without_check: List[List[BasicBlock]],
    ) -> None:
        """Find execution paths with missing UpdateApplication check.

        This function recursively explores the Control Flow Graph(CFG) of the
        contract and reports execution paths with missing UpdateApplication
        check. Paths that will only execute if the application transaction
        is not UpdateApplication transaction are excluded.

        This function is "in place", modifies arguments with the data it is
        supposed to return.

        Args:
            bb: Current basic block being checked(whose execution is simulated.)
            current_path: Current execution path being explored.
            paths_without_check:
                Execution paths with missing UpdateApplication check. This is a
                "in place" argument. Vulnerable paths found by this function are
                appended to this list.
        """

        # check for loops
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
                if _is_update(one, two) or _is_update(two, one):
                    return
                if is_oncompletion_check(one, two, CHECKED_VALUES) or is_oncompletion_check(
                    two, one, CHECKED_VALUES
                ):
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
        """Detect execution paths with missing UpdateApplication check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        paths_without_check: List[List[BasicBlock]] = []
        self._check_delete(self.teal.bbs[0], [], paths_without_check)

        description = "Lack of txn OnCompletion == int UpdateApplication check allows to"
        description += " update the application's approval and clear programs."

        filename = "can_update"
        return self.generate_result(paths_without_check, description, filename)
