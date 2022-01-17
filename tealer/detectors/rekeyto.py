from collections import defaultdict
from copy import copy
from typing import Dict, Set, List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Gtxn, Return, Int, Txn, Global, Addr, Eq, Neq
from tealer.teal.instructions.transaction_field import RekeyTo
from tealer.teal.global_field import ZeroAddress

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput
    from tealer.teal.instructions.instructions import Instruction


def _is_rekey_check(ins1: "Instruction", ins2: "Instruction") -> bool:
    """check if ins1 is txn RekeyTo and ins2 is global ZeroAddress or addr ..."""
    if isinstance(ins1, Txn) and isinstance(ins1.field, RekeyTo):
        if isinstance(ins2, Global) and isinstance(ins2.field, ZeroAddress):
            return True
        if isinstance(ins2, Addr):
            return True
    return False


class MissingRekeyTo(AbstractDetector):

    NAME = "rekeyTo"
    DESCRIPTION = "Detect paths with a missing RekeyTo check"
    TYPE = DetectorType.STATEFULLGROUP

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

    def _check_rekey_to_contract(
        self,
        bb: "BasicBlock",
        current_path: List["BasicBlock"],
        paths_without_check: List[List["BasicBlock"]],
    ) -> None:
        """find execution paths with missing `txn RekeyTo (== | !=) (global ZeroAddress | Addr ..)`

        This function checks for rekeying of this contract i.e whether the contract is checking for
        rekeying of itself.

        """
        # check for loops
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
            self._check_rekey_to_contract(next_bb, current_path, paths_without_check)

    def check_rekey_to_group(  # pylint: disable=too-many-arguments
        self,
        bb: BasicBlock,
        group_tx: Dict[int, Set[BasicBlock]],
        idx_fitlered: Set[int],
        current_path: List[BasicBlock],
        paths_without_check: List[List[BasicBlock]],
    ) -> None:
        """find execution paths with missing rekey checks of other transactions in the group.

        This check finds paths which doesn't check RekeyTo field of other transactions in the group.
        Information about index of other transactions in the group is calculated using Gtxn instruction.
        Suppose, if there's an instruction `Gtxn 2 Sender`, then 2 is the index of other transaction
        in the group and function checks for instruction `Gtxn 2 RekeyTo` and reports execution paths
        missing that check. This is repeated for all indexes of group transactions found.

        """
        # check for loops
        if bb in current_path:
            return

        current_path = current_path + [bb]

        group_tx = copy(group_tx)
        for ins in bb.instructions:
            if isinstance(ins, Gtxn):
                if ins.idx not in idx_fitlered:
                    assert ins.bb
                    group_tx[ins.idx].add(ins.bb)

                if isinstance(ins.field, RekeyTo):
                    del group_tx[ins.idx]
                    idx_fitlered = set(idx_fitlered)
                    idx_fitlered.add(ins.idx)

            if isinstance(ins, Return) and group_tx:
                if len(ins.prev) == 1:
                    prev = ins.prev[0]
                    if isinstance(prev, Int) and prev.value == 0:
                        return

                paths_without_check.append(current_path)

        for next_bb in bb.next:
            self.check_rekey_to_group(
                next_bb, group_tx, idx_fitlered, current_path, paths_without_check
            )

    def detect(self) -> "SupportedOutput":

        paths_without_check: List[List[BasicBlock]] = []
        self.check_rekey_to_group(
            self.teal.bbs[0], defaultdict(set), set(), [], paths_without_check
        )

        self._check_rekey_to_contract(self.teal.bbs[0], [], paths_without_check)

        # paths might repeat as cfg traversed twice, once for each check
        paths_without_check_unique = []
        added_paths = []
        for path in paths_without_check:
            short = " -> ".join(map(str, [bb.idx for bb in path]))
            if short in added_paths:
                continue
            paths_without_check_unique.append(path)
            added_paths.append(short)

        description = "Lack of txn RekeyTo check allows rekeying the account to"
        description += " attacker controlled address and control the account directly."
        description += "\nExecution paths with missing rekeyTo check of the current transaction and"
        description += "missing rekeyTo check of other transactions in the group."
        filename = "missing_rekeyto_check"

        return self.generate_result(paths_without_check_unique, description, filename)
