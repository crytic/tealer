"""Detect paths missing validations on sender field AND allows to update the application."""

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

    def detect(self) -> "ListOutput":
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

        # there should be a better to decide which function to call ??
        if self.tealer.output_group:
            # mypy complains if the value is returned directly. Uesd the second suggestion mentioned here:
            # https://mypy.readthedocs.io/en/stable/common_issues.html#variance
            return list(
                detect_missing_tx_field_validations_group_complete(self.tealer, self, checks_field)
            )

        output: List[
            Tuple["Teal", List[List["BasicBlock"]]]
        ] = detect_missing_tx_field_validations_group(self.tealer, checks_field)
        detector_output: "ListOutput" = []
        for contract, vulnerable_paths in output:
            detector_output.append(ExecutionPaths(contract, self, vulnerable_paths))

        return detector_output
