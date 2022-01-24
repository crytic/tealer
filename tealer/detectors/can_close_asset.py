"""Detector for finding execution paths missing AssetCloseTo check."""

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
from tealer.teal.instructions.transaction_field import AssetCloseTo

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput


def _is_asset_close_check(ins1: Instruction, ins2: Instruction) -> bool:
    """Util function to check if given instructions form AssetCloseTo check.

    Args:
        ins1: First instruction of the execution sequence that is supposed
            to form a comparison check for AssetCloseTo transaction field.
        ins2: Second instruction in the execution sequence, will be executed
            right after :ins1:.

    Returns:
        True if the given instructions :ins1:, :ins2: form a AssetCloseTo
        check i.e True if :ins1: is txn AssetCloseTo and :ins2: is
        global ZeroAddress or addr.
    """

    if isinstance(ins1, Txn) and isinstance(ins1.field, AssetCloseTo):
        if isinstance(ins2, Global) and isinstance(ins2.field, ZeroAddress):
            return True
        if isinstance(ins2, Addr):
            return True
    return False


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

    NAME = "canCloseAsset"
    DESCRIPTION = "Detect paths that can close the asset holdings of the sender"
    TYPE = DetectorType.STATELESS

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

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
        """Find execution paths with missing AssetCloseTo check.

        This function recursively explores the Control Flow Graph(CFG) of the
        contract and reports execution paths with missing AssetCloseTo
        check.

        This function is "in place", modifies arguments with the data it is
        supposed to return.

        Args:
            bb: Current basic block being checked(whose execution is simulated.)
            current_path: Current execution path being explored.
            paths_without_check:
                Execution paths with missing AssetCloseTo check. This is a
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
                if _is_asset_close_check(one, two) or _is_asset_close_check(two, one):
                    return

            stack.append(ins)

        for next_bb in bb.next:
            self._check_close_asset(next_bb, current_path, paths_without_check)

    def detect(self) -> "SupportedOutput":
        """Detect execution paths with missing AssetCloseTo check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        paths_without_check: List[List[BasicBlock]] = []
        self._check_close_asset(self.teal.bbs[0], [], paths_without_check)

        description = "Lack of AssetCloseTo check allows to close the asset holdings"
        description += " of the account."
        filename = "can_close_asset"

        return self.generate_result(paths_without_check, description, filename)
