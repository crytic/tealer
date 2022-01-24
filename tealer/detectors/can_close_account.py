"""Detector for finding execution paths missing CloseRemainderTo check."""

from typing import List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.global_field import ZeroAddress
from tealer.teal.instructions.instructions import (
    Addr,
    Eq,
    Global,
    Instruction,
    Int,
    Neq,
    Return,
    Txn,
)
from tealer.teal.instructions.transaction_field import CloseRemainderTo

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput


def _is_close_remainder_check(ins1: Instruction, ins2: Instruction) -> bool:
    """Util function to check if given instructions form CloseRemainderTo check.

    Args:
        ins1: First instruction of the execution sequence that is supposed
            to form a comparison check for CloseRemainderTo transaction field.
        ins2: Second instruction in the execution sequence, will be executed
            right after :ins1:.

    Returns:
        True if the given instructions :ins1:, :ins2: form a CloseRemainderTo
        check i.e True if :ins1: is txn CloseRemainderTo and :ins2: is
        global ZeroAddress or addr .. .
    """

    if isinstance(ins1, Txn) and isinstance(ins1.field, CloseRemainderTo):
        if isinstance(ins2, Global) and isinstance(ins2.field, ZeroAddress):
            return True
        if isinstance(ins2, Addr):
            return True
    return False


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

    def _check_close_account(
        self,
        bb: BasicBlock,
        current_path: List[BasicBlock],
        paths_without_check: List[List[BasicBlock]],
    ) -> None:
        """Find execution paths with missing CloseRemainderTo check.

        This function recursively explores the Control Flow Graph(CFG) of the
        contract and reports execution paths with missing CloseRemainderTo
        check.

        This function is "in place", modifies arguments with the data it is
        supposed to return.

        Args:
            bb: Current basic block being checked(whose execution is simulated.)
            current_path: Current execution path being explored.
            paths_without_check:
                Execution paths with missing CloseRemainderTo check. This is a
                "in place" argument. Vulnerable paths found by this function are
                appended to this list.
        """

        if bb in current_path:
            return

        current_path = current_path + [bb]

        stack: List[Instruction] = []

        for ins in bb.instructions:

            if isinstance(ins, Return):
                if len(ins.prev) == 1:
                    prev = ins.prev[0]
                    if isinstance(prev, Int) and prev.value == 0:
                        return

                paths_without_check.append(current_path)
                return

            if isinstance(ins, (Eq, Neq)) and len(stack) >= 2:
                one = stack[-1]
                two = stack[-2]
                if _is_close_remainder_check(one, two) or _is_close_remainder_check(two, one):
                    return

            stack.append(ins)

        for next_bb in bb.next:
            self._check_close_account(next_bb, current_path, paths_without_check)

    def detect(self) -> "SupportedOutput":
        """Detect execution paths with missing CloseRemainderTo check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        paths_without_check: List[List[BasicBlock]] = []
        self._check_close_account(self.teal.bbs[0], [], paths_without_check)

        description = "Lack of CloseRemainderTo check allows to close the account and"
        description += " transfer all the funds to attacker controlled address."

        filename = "can_close_account"

        return self.generate_result(paths_without_check, description, filename)
