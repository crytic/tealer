"""Detector for finding execution paths missing Fee check."""

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
from tealer.utils.algorand_constants import MAX_TRANSACTION_COST
from tealer.utils.output import ExecutionPaths

if TYPE_CHECKING:
    from tealer.utils.output import ListOutput
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.context.block_transaction_context import BlockTransactionContext
    from tealer.teal.teal import Teal


class MissingFeeCheck(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find execution paths missing Fee check.

    The fee for stateless contract transactions will be deducted
    from the contract account or the LogicSig signer account. An
    attacker could set the fee to high value and drain the account
    funds in form of fees.

    This detector tries to find execution paths that approve the algorand
    transaction("return 1") and doesn't check the Fee field.
    """

    NAME = "missing-fee-check"
    DESCRIPTION = "Missing Fee Field Validation"
    TYPE = DetectorType.STATELESS

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_URL = (
        "https://github.com/crytic/tealer/wiki/Detector-Documentation#missing-fee-field-validation"
    )
    WIKI_TITLE = "Missing Fee Field Validation"
    WIKI_DESCRIPTION = (
        "LogicSig does not validate `Fee` field."
        " Attacker can submit a transaction with `Fee` field set to large value and drain the account balance."
        " More at [building-secure-contracts/not-so-smart-contracts/algorand/unchecked_transaction_fee]"
        "(https://github.com/crytic/building-secure-contracts/tree/master/not-so-smart-contracts/algorand/unchecked_transaction_fee)"
    )
    WIKI_EXPLOIT_SCENARIO = """
```py
def withdraw(...) -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Txn.type_enum() == TxnType.Payment,
                    Txn.first_valid() % period == Int(0),
                    Txn.last_valid() == Txn.first_valid() + duration,
                    Txn.receiver() == receiver,
                    Txn.amount() == amount,
                    Txn.first_valid() < timeout,
                )
            ),
            Approve(),
        ]
    )
```

Alice signs the logic-sig to allow recurring payments to Bob.\
 Eve uses the logic-sig and submits a valid transaction with `Fee` set to 1 million ALGOs.\
 Alice loses 1 million ALGOs.
"""

    WIKI_RECOMMENDATION = """
Validate `Fee` field in the LogicSig.
"""

    def detect(self) -> "ListOutput":
        """Detect execution paths with missing Fee check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        def checks_field(block_ctx: "BlockTransactionContext") -> bool:
            # returns True if fee is bounded by some unknown value
            # or is bounded by some known value less than maximum transaction cost.
            return block_ctx.max_fee_unknown or block_ctx.max_fee <= MAX_TRANSACTION_COST

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
