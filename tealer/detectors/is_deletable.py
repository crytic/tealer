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


class IsDeletable(AbstractDetector):  # pylint: disable=too-few-public-methods
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

    NAME = "is-deletable"
    DESCRIPTION = "Deletable Applications"
    TYPE = DetectorType.STATEFULL

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_URL = "https://github.com/crytic/tealer/wiki/Detector-Documentation#deletable-application"
    WIKI_TITLE = "Deletable Application"
    WIKI_DESCRIPTION = (
        "Application can be deleted by sending an `DeleteApplication` type application call. "
    )
    WIKI_EXPLOIT_SCENARIO = """
```py
@router.method(delete_application=CallConfig.CALL)
def delete_application() -> Expr:
    return Assert(Txn.sender() == Global.creator_address())
```

Eve steals application creator's private key and deletes the application. Application's assets are permanently lost.
"""

    WIKI_RECOMMENDATION = """
Do not approve `DeleteApplication` type application calls.
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
        filename = "is_deletable"

        return self.generate_result(paths_without_check, description, filename)
