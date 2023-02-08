"""Detector for finding execution paths missing Fee check."""

from typing import List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import (
    Instruction,
    Int,
    Txn,
)
from tealer.teal.instructions.transaction_field import Fee
from tealer.detectors.utils import detect_missing_tx_field_validations
from tealer.utils.algorand_constants import MAX_TRANSACTION_COST

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput
    from tealer.teal.context.block_transaction_context import BlockTransactionContext


def _is_fee_check(ins1: Instruction, ins2: Instruction) -> bool:
    """Util function to check if given instructions form Fee check.

    Args:
        ins1: First instruction of the execution sequence that is supposed
            to form a comparison check for Fee transaction field.
        ins2: Second instruction in the execution sequence, will be executed
            right after :ins1:.

    Returns:
        True if the given instructions :ins1:, :ins2: form a Fee check
        i.e True if :ins1: is txn Fee and :ins2: is int .. .
    """

    if isinstance(ins1, Txn) and isinstance(ins1.field, Fee):
        return isinstance(ins2, Int)
    return False


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

    def detect(self) -> "SupportedOutput":
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

        paths_without_check: List[List[BasicBlock]] = detect_missing_tx_field_validations(
            self.teal.bbs[0], checks_field
        )

        description = "Lack of fee check allows draining the funds of sender account,"
        description += "contract account or signer of delegate contract."
        filename = "missing_fee_check"

        return self.generate_result(paths_without_check, description, filename)
