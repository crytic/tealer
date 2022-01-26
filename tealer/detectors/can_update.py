"""Detector for finding execution paths missing UpdateApplication."""

from typing import List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Instruction
from tealer.teal.instructions.instructions import Int, Txn
from tealer.teal.instructions.transaction_field import ApplicationID
from tealer.utils.analyses import detect_missing_on_completion

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput


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

    def detect(self) -> "SupportedOutput":
        """Detect execution paths with missing UpdateApplication check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        paths_without_check: List[List[BasicBlock]] = []
        detect_missing_on_completion(
            self.teal.bbs[0],
            [],
            paths_without_check,
            "UpdateApplication",
            [
                "DeleteApplication",
                "NoOp",
                "OptIn",
                "CloseOut",
            ],
        )

        description = "Lack of txn OnCompletion == int UpdateApplication check allows to"
        description += " update the application's approval and clear programs."

        filename = "can_update"
        return self.generate_result(paths_without_check, description, filename)
