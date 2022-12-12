"""Detector for finding execution paths missing CloseRemainderTo check."""

from typing import List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.detectors.utils import detect_missing_tx_field_validations


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

    NAME = "canCloseAccount"
    DESCRIPTION = "Detect paths that can close out the sender account"
    TYPE = DetectorType.STATELESS

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_TITLE = "Can Close Account"
    WIKI_DESCRIPTION = "Detect paths that can close out the sender account"
    WIKI_EXPLOIT_SCENARIO = """
```
#pragma version 2
txn Receiver
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
txn Receiver
addr GDN6PPITDEXNCQ2BS2DUKVDPJZM7K6LKO6QBWP2US555NUE4Q5TY7HAVSQ
==
||
txn Amount
int 1000000
==
&&
...
```

if one of the receiver turns out to be malicious, they could set the CloseRemainderTo field to their address, which when the transaction is successful will result in transfer of all remaining funds of sender to the CloseRemainderTo address.
"""

    WIKI_RECOMMENDATION = """
Always check that CloseRemainderTo transaction field is set to a ZeroAddress or intended address if needed. 
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
            return not block_ctx.closeto.any_addr

        paths_without_check: List[List[BasicBlock]] = detect_missing_tx_field_validations(
            self.teal.bbs[0], checks_field
        )

        description = "Lack of CloseRemainderTo check allows to close the account and"
        description += " transfer all the funds to attacker controlled address."

        filename = "can_close_account"

        return self.generate_result(paths_without_check, description, filename)
