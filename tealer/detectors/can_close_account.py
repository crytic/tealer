"""Detector for finding execution paths missing CloseRemainderTo check."""

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


class CanCloseAccount(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find execution paths missing CloseRemainderTo check.

    In algorand, A transaction can close out the contract account and
    transfer all it's balance to the specified address. If the CloseRemainderTo
    field of a transaction is set to an address and that transaction is approved
    by the contract then the entire contract balance will be transferred to the
    address specified in CloseRemainderTo field.

    This detector tries to find execution paths that approve the algorand
    transaction("return 1") and doesn't check the CloseRemainderTo field.
    """

    NAME = "can-close-account"
    DESCRIPTION = "Missing CloseRemainderTo field Validation"
    TYPE = DetectorType.STATELESS

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_URL = "https://github.com/crytic/tealer/wiki/Detector-Documentation#missing-closeremainderto-field-validation"
    WIKI_TITLE = "Missing CloseRemainderTo Field Validation"
    WIKI_DESCRIPTION = (
        "LogicSig does not validate `CloseRemainderTo` field."
        " Attacker can submit a transaction with `CloseRemainderTo` field set to their address and steal all of account's ALGOs."
        " More at [building-secure-contracts/not-so-smart-contracts/algorand/closing_account]"
        "(https://github.com/crytic/building-secure-contracts/tree/master/not-so-smart-contracts/algorand/closing_account)"
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
 Eve uses the logic-sig and submits a valid transaction with `CloseRemainderTo` field set to her address.\
 Eve steals Alice's ALGO balance.
"""

    WIKI_RECOMMENDATION = """
Validate `CloseRemainderTo` field in the LogicSig.
"""

    def detect(self) -> "SupportedOutput":
        """Detect execution paths with missing CloseRemainderTo check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        def checks_field(block_ctx: "BlockTransactionContext") -> bool:
            # return False if CloseRemainderTo field can have any address.
            # return True if CloseRemainderTo should have some address or zero address
            # CloseRemainderTo field can only be set for Payment type transactions.
            return not (
                block_ctx.closeto.any_addr
                and TealerTransactionType.Pay in block_ctx.transaction_types
            )

        paths_without_check: List[List[BasicBlock]] = detect_missing_tx_field_validations(
            self.teal.bbs[0], checks_field
        )

        description = "Lack of CloseRemainderTo check allows to close the account and"
        description += " transfer all the funds to attacker controlled address."

        filename = "can_close_account"

        return self.generate_result(paths_without_check, description, filename)
