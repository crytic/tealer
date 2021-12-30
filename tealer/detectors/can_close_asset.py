from pathlib import Path
from typing import List

from tealer.detectors.abstract_detector import AbstractDetector, DetectorType
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
from tealer.teal.instructions.transaction_field import AssetCloseTo


def _is_asset_close_check(ins1: Instruction, ins2: Instruction) -> bool:
    if isinstance(ins1, Txn) and isinstance(ins1.field, AssetCloseTo):
        if isinstance(ins2, Global) and isinstance(ins2.field, ZeroAddress):
            return True
        if isinstance(ins2, Addr):
            return True
    return False


class CanCloseAsset(AbstractDetector):  # pylint: disable=too-few-public-methods
    NAME = "canCloseAsset"
    DESCRIPTION = "Detect paths that can close the asset holdings of the sender"
    TYPE = DetectorType.STATELESS

    WIKI_TITLE = "Can Close Asset"
    WIKI_DESCRIPTION = "Detect paths that can close the asset holdings of the sender"
    WIKI_EXPLOIT_SCENARIO = """
```
#pragma version 2
txn Receiver
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
txn AssetAmount
int 10
==
&&
...
```

receiver sets the AssetCloseTo transaction field of a Asset Transfer Transaction with above contract account as Sender which will result in removal of asset holding from the contract's account and sending the asset's to AssetCloseTo address.
"""

    WIKI_RECOMMENDATION = """
Always check that AssetCloseTo transaction field is set to a ZeroAddress or intended address if needed.
"""

    def _check_close_asset(
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
                if _is_asset_close_check(one, two) or _is_asset_close_check(two, one):
                    return

            stack.append(ins)

        for next_bb in bb.next:
            self._check_close_asset(next_bb, current_path, paths_without_check)

    def detect(self) -> List[str]:

        paths_without_check: List[List[BasicBlock]] = []
        self._check_close_asset(self.teal.bbs[0], [], paths_without_check)

        all_results_txt: List[str] = []
        idx = 1
        for path in paths_without_check:
            filename = Path(f"can_close_asset_{idx}.dot")
            idx += 1
            description = "Lack of AssetCloseTo check allows to close the asset"
            description += " holdings of the account."
            description += f"\n\tCheck the path in {filename}\n"
            all_results_txt.append(description)
            self.teal.bbs_to_dot(filename, path)

        return all_results_txt
