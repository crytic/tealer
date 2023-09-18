from typing import List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.global_field import ZeroAddress
from tealer.teal.instructions.instructions import Addr, Eq, Global, Int, Neq, Return, Txn
from tealer.teal.instructions.transaction_field import RekeyTo
from tealer.utils.output import ExecutionPaths

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.instructions.instructions import Instruction
    from tealer.utils.output import SupportedOutput


def _is_rekey_check(ins1: "Instruction", ins2: "Instruction") -> bool:
    """check if ins1 is txn RekeyTo and ins2 is global ZeroAddress or addr ...

    Args:
        ins1: First instruction.
        ins2: Second instruction.

    Returns:
        Returns True is :ins1: is "txn RekeyTo" and ins2 pushes an address value onto the stack.
        Otherwise, returns False.
    """
    if isinstance(ins1, Txn) and isinstance(ins1.field, RekeyTo):
        if isinstance(ins2, Global) and isinstance(ins2.field, ZeroAddress):
            return True
        if isinstance(ins2, Addr):
            return True
    return False


class CanRekey(AbstractDetector):  # pylint: disable=too-few-public-methods

    NAME = "rekeyTo-stateless"
    DESCRIPTION = "Detect paths with a missing RekeyTo check"
    TYPE = DetectorType.STATELESS

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_TITLE = "Can Rekey Contract"
    WIKI_DESCRIPTION = "Detect paths with a missing RekeyTo check"
    WIKI_EXPLOIT_SCENARIO = """
Rekeying is an Algorand feature which enables an account holder to give authorization of their account to different address, whereby users can maintain a single static public address while updating the key controlling the assets.
Rekeying is done by using *rekey-to* transaction which is a payment transaction with `rekey-to` parameter set to new authorized address.

if a stateless contract, approves a payment transaction without checking the `rekey-to` parameter then one can set the authorization address to the contract account and withdraw funds directly bypassing all the checks.

Attacker creates a payment transaction using the contract with `rekey-to` set to their address. After rekeying, attacker transfer's the assets using their private key bypassing the conditions defined in the contract.
"""

    WIKI_RECOMMENDATION = """
Add a check in the contract code verifying that `RekeyTo` property of any transaction is set to `ZeroAddress`.
"""

    def _check_rekey_to(
        self,
        bb: "BasicBlock",
        current_path: List["BasicBlock"],
        paths_without_check: List[List["BasicBlock"]],
    ) -> None:
        if bb in current_path:
            return

        current_path = current_path + [bb]

        stack: List["Instruction"] = []

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
                if _is_rekey_check(one, two) or _is_rekey_check(two, one):
                    return

            stack.append(ins)

        for next_bb in bb.next:
            self._check_rekey_to(next_bb, current_path, paths_without_check)

    def detect(self) -> "SupportedOutput":

        paths_without_check: List[List["BasicBlock"]] = []
        self._check_rekey_to(self.teal.bbs[0], [], paths_without_check)

        return ExecutionPaths(self.teal, self, paths_without_check)
