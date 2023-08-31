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
from tealer.utils.output import ExecutionPaths

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput
    from tealer.teal.context.block_transaction_context import BlockTransactionContext


class IsUpdatable(AbstractDetector):  # pylint: disable=too-few-public-methods
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

    NAME = "is-updatable"
    DESCRIPTION = "Upgradable Applications"
    TYPE = DetectorType.STATEFULL

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_URL = "https://github.com/crytic/tealer/wiki/Detector-Documentation#upgradable-application"
    WIKI_TITLE = "Upgradable Application"
    WIKI_DESCRIPTION = (
        "Application can be updated by sending an `UpdateApplication` type application call."
    )
    WIKI_EXPLOIT_SCENARIO = """
```py
@router.method(update_application=CallConfig.CALL)
def update_application() -> Expr:
    return Assert(Txn.sender() == Global.creator_address())
```

Creator updates the application and steals all of its assets.
"""

    WIKI_RECOMMENDATION = """
Do not approve `UpdateApplication` type application calls.
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
            self.teal, checks_field
        )

        return ExecutionPaths(self.teal, self, paths_without_check)
