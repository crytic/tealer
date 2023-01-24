"""Detector for finding execution paths missing UpdateApplication."""

from typing import List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.detectors.utils import detect_missing_tx_field_validations
from tealer.utils.teal_enums import TealerTransactionType

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput
    from tealer.teal.context.block_transaction_context import BlockTransactionContext


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

        def checks_field(block_ctx: "BlockTransactionContext") -> bool:
            # return False if Txn Type can be UpdateApplication.
            # return True if Txn Type cannot be UpdateApplication.
            return not TealerTransactionType.ApplUpdateApplication in block_ctx.transaction_types

        paths_without_check: List[List[BasicBlock]] = detect_missing_tx_field_validations(
            self.teal.bbs[0], checks_field
        )

        description = "Lack of txn OnCompletion == int UpdateApplication check allows to"
        description += " update the application's approval and clear programs."

        filename = "can_update"
        return self.generate_result(paths_without_check, description, filename)
