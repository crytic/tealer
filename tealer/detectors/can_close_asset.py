"""Detector for finding execution paths missing AssetCloseTo check."""

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
from tealer.utils.teal_enums import TransactionType

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.utils.output import ListOutput
    from tealer.teal.context.block_transaction_context import BlockTransactionContext
    from tealer.teal.teal import Teal


class CanCloseAsset(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find execution paths missing AssetCloseTo check.

    In algorand, A transaction can close out the asset balance of a contract
    account and transfer all asset balance to the specified address. If the
    AssetCloseTo field of a transaction is set to an address and that transaction
    is approved by the contract then all the contract asset balance will be
    transferred to address in AssetCloseTo field.

    This detector tries to find execution paths that approve the algorand
    transaction("return 1") and doesn't check the AssetCloseTo field.
    """

    NAME = "can-close-asset"
    DESCRIPTION = "Missing AssetCloseTo Field Validation"
    TYPE = DetectorType.STATELESS

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_URL = "https://github.com/crytic/tealer/wiki/Detector-Documentation#missing-assetcloseto-field-validation"
    WIKI_TITLE = "Missing AssetCloseTo Field Validation"
    WIKI_DESCRIPTION = (
        "LogicSig does not validate `AssetCloseTo` field."
        " Attacker can submit a transaction with `AssetCloseTo` field set to their address and steal account's assets."
        " More at [building-secure-contracts/not-so-smart-contracts/algorand/closing_asset]"
        "(https://github.com/crytic/building-secure-contracts/tree/master/not-so-smart-contracts/algorand/closing_asset)"
    )
    WIKI_EXPLOIT_SCENARIO = """
```py
def withdraw(...) -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Txn.type_enum() == TxnType.AssetTransfer,
                    Txn.first_valid() % period == Int(0),
                    Txn.last_valid() == Txn.first_valid() + duration,
                    Txn.asset_receiver() == receiver,
                    Txn.asset_amount() == amount,
                    Txn.first_valid() < timeout,
                )
            ),
            Approve(),
        ]
    )
```

Alice signs the logic-sig to allow recurring payments to Bob in USDC.\
 Eve uses the logic-sig and submits a valid transaction with `AssetCloseTo` field set to her address.\
 Eve steals Alice's USDC balance.
"""

    WIKI_RECOMMENDATION = """
Validate `AssetCloseTo` field in the LogicSig.
"""

    def detect(self) -> "ListOutput":
        """Detect execution paths with missing AssetCloseTo check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        def checks_field(block_ctx: "BlockTransactionContext") -> bool:
            # return False if AssetCloseTo field can have any address.
            # return True if AssetCloseTo should have some address or zero address
            # AssetCloseTo field can only be set for Asset Transafer type transactions.
            return not (
                block_ctx.assetcloseto.any_addr
                and TealerTransactionType.Axfer in block_ctx.transaction_types
            )

        # there should be a better to decide which function to call ??
        if self.tealer.output_group:
            # mypy complains if the value is returned directly. Uesd the second suggestion mentioned here:
            # https://mypy.readthedocs.io/en/stable/common_issues.html#variance
            return list(
                detect_missing_tx_field_validations_group_complete(
                    self.tealer,
                    self,
                    checks_field,
                    [TransactionType.Any, TransactionType.Unknown, TransactionType.Axfer],
                )
            )

        output: List[
            Tuple["Teal", List[List["BasicBlock"]]]
        ] = detect_missing_tx_field_validations_group(self.tealer, checks_field)
        detector_output: "ListOutput" = []
        for contract, vulnerable_paths in output:
            detector_output.append(ExecutionPaths(contract, self, vulnerable_paths))

        return detector_output
