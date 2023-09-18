"""Detect paths missing validations on sender field AND allows to update the application."""

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


class AnyoneCanUpdate(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find execution paths missing validations on sender field AND allows to update the application.

    Stateful smart contracts(application) can be updated in algorand. If the
    application transaction of type UpdateApplication is approved by the application,
    then the application's code will be updated with the new code.

    This detector tries to find execution paths for which
        - OnCompletion can be UpdateApplication And
        - Transaction sender can be any address.
    """

    NAME = "unprotected-updatable"
    DESCRIPTION = "Unprotected Upgradable Applications"
    TYPE = DetectorType.STATEFULL

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_URL = "https://github.com/crytic/tealer/wiki/Detector-Documentation#unprotected-updatable-application"
    WIKI_TITLE = "Unprotected Upgradable Application"
    WIKI_DESCRIPTION = (
        "Application can be updated by anyone. "
        "More at [building-secure-contracts/not-so-smart-contracts/algorand/access_controls]"
        "(https://github.com/crytic/building-secure-contracts/tree/master/not-so-smart-contracts/algorand/access_controls)."
    )
    WIKI_EXPLOIT_SCENARIO = """
```py
@router.method(update_application=CallConfig.CALL)
def update_application() -> Expr:
    return Approve()
```

Eve updates the application by calling `update_application` method and steals all of its assets.
"""

    WIKI_RECOMMENDATION = """
- Avoid upgradable applications.
- Add access controls to the vulnerable method.
"""

    def detect(self) -> "SupportedOutput":
        """Detect paths missing validations on sender field AND allows to update the application.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        def checks_field(block_ctx: "BlockTransactionContext") -> bool:
            # return False if Txn Type can be UpdateApplication AND sender can be any address.
            # return True otherwise.
            return not (
                TealerTransactionType.ApplUpdateApplication in block_ctx.transaction_types
                and block_ctx.sender.any_addr
            )

        paths_without_check: List[List[BasicBlock]] = detect_missing_tx_field_validations(
            self.teal, checks_field
        )

        return ExecutionPaths(self.teal, self, paths_without_check)
