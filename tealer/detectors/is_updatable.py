"""Detector for finding execution paths missing UpdateApplication."""

from typing import List, TYPE_CHECKING, Tuple

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.detectors.utils import (
    detect_missing_tx_field_validations_group,
    detect_missing_tx_field_validations_group_complete,
)
from tealer.utils.teal_enums import TealerTransactionType
from tealer.utils.output import ExecutionPaths

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.utils.output import ListOutput
    from tealer.teal.context.block_transaction_context import BlockTransactionContext
    from tealer.teal.teal import Teal


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

    def detect(self) -> "ListOutput":
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

        # there should be a better to decide which function to call ??
        if self.tealer.output_group:
            # mypy complains if the value is returned directly. Uesd the second suggestion mentioned here:
            # https://mypy.readthedocs.io/en/stable/common_issues.html#variance
            return list(
                detect_missing_tx_field_validations_group_complete(self.tealer, self, checks_field)
            )

        # paths_without_check: List[List[BasicBlock]] = detect_missing_tx_field_validations(
        #     self.teal, checks_field
        # )

        # return ExecutionPaths(self.teal, self, paths_without_check)
        output: List[
            Tuple["Teal", List[List["BasicBlock"]]]
        ] = detect_missing_tx_field_validations_group(self.tealer, checks_field)
        detector_output: "ListOutput" = []
        for contract, vulnerable_paths in output:
            detector_output.append(ExecutionPaths(contract, self, vulnerable_paths))

        return detector_output
