from pathlib import Path
from typing import List

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
from tealer.utils.output import execution_path_to_dot


def _is_close_remainder_check(ins1: Instruction, ins2: Instruction) -> bool:
    if isinstance(ins1, Txn) and isinstance(ins1.field, CloseRemainderTo):
        if isinstance(ins2, Global) and isinstance(ins2.field, ZeroAddress):
            return True
        if isinstance(ins2, Addr):
            return True
    return False


class CanCloseAccount(AbstractDetector):  # pylint: disable=too-few-public-methods
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

    def detect(self) -> List[str]:

        paths_without_check: List[List[BasicBlock]] = []
        self._check_close_account(self.teal.bbs[0], [], paths_without_check)

        all_results_txt: List[str] = []
        idx = 1
        for path in paths_without_check:
            filename = Path(f"can_close_account_{idx}.dot")
            idx += 1
            description = "Lack of CloseRemainderTo check allows to close the account"
            description += " and transfer all the funds to their controlled account."
            description += f"\n\tCheck the path in {filename}\n"
            all_results_txt.append(description)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(execution_path_to_dot(self.teal.bbs, path))

        return all_results_txt
