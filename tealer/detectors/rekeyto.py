"""Detector for finding execution paths missing RekeyTo check."""

from typing import List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.detectors.utils import detect_missing_tx_field_validations
from tealer.utils.output import ExecutionPaths


if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput
    from tealer.teal.context.block_transaction_context import BlockTransactionContext


class MissingRekeyTo(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find execution paths missing RekeyTo check.

    TEAL, from version 2 onwards supports rekeying of accounts.
    An account can be rekeyed to a different address. Once rekeyed,
    rekeyed address has entire authority over the account. Contract
    Accounts can also be rekeyed. If RekeyTo field of the transaction
    is set to malicious actor's address, then they can control the account
    funds, assets directly bypassing the contract's restrictions.

    This detector tries to find execution paths that approve the algorand
    transaction("return 1") and doesn't check the RekeyTo transaction field.
    Additional to checking rekeying of it's own contract, detector also finds
    execution paths that doesn't check RekeyTo field of other transactions
    in the atomic group.
    """

    NAME = "rekey-to"
    DESCRIPTION = "Rekeyable Logic Signatures"
    TYPE = DetectorType.STATELESS

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_URL = "https://github.com/crytic/tealer/wiki/Detector-Documentation#rekeyable-logicsig"
    WIKI_TITLE = "Rekeyable LogicSig"
    WIKI_DESCRIPTION = (
        "Logic signature does not validate `RekeyTo` field."
        " Attacker can submit a transaction with `RekeyTo` field set to their address and take control over the account."
        " More at [building-secure-contracts/not-so-smart-contracts/algorand/rekeying]"
        "(https://github.com/crytic/building-secure-contracts/tree/master/not-so-smart-contracts/algorand/rekeying)"
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
 Eve uses the logic-sig and submits a valid transaction with `RekeyTo` field set to her address.\
 Eve takes over Alice's account.
"""

    WIKI_RECOMMENDATION = """
Validate `RekeyTo` field in the LogicSig.
"""

    def detect(self) -> "SupportedOutput":
        """Detect execution paths with missing CloseRemainderTo check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        def checks_field(block_ctx: "BlockTransactionContext") -> bool:
            # return False if RekeyTo field can have any address.
            # return True if RekeyTo should have some address or zero address
            return not block_ctx.rekeyto.any_addr

        paths_without_check: List[List[BasicBlock]] = detect_missing_tx_field_validations(
            self.teal, checks_field
        )

        return ExecutionPaths(self.teal, self, paths_without_check)
