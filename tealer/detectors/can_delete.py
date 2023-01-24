"""Detector for finding execution paths missing DeleteApplication check."""

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


class CanDelete(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find execution paths missing DeleteApplication check.

    Stateful smart contracts(application) can be deleted in algorand. If the
    application transaction of type DeleteApplication is approved by the application,
    then the application will be deleted. Contracts can check the application
    transaction type using OnCompletion field.

    This detector tries to find execution paths that approve the application
    transaction("return 1") and doesn't check the OnCompletion field against
    DeleteApplication value. Execution paths that only execute if the application
    transaction is not DeleteApplication are excluded.
    """

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

    def detect(self) -> "SupportedOutput":
        """Detect execution paths with missing DeleteApplication check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        def checks_field(block_ctx: "BlockTransactionContext") -> bool:
            # return False if Txn Type can be DeleteApplication.
            # return True if Txn Type cannot be DeleteApplication.
            return not TealerTransactionType.ApplDeleteApplication in block_ctx.transaction_types

        paths_without_check: List[List[BasicBlock]] = detect_missing_tx_field_validations(
            self.teal.bbs[0], checks_field
        )

        description = "Lack of txn OnCompletion == int DeleteApplication check allows to"
        description += " delete the application."
        filename = "can_delete"

        return self.generate_result(paths_without_check, description, filename)
