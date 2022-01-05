from collections import defaultdict
from copy import copy
from typing import Dict, Set, List, TYPE_CHECKING

from tealer.detectors.abstract_detector import AbstractDetector, DetectorType
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Gtxn, Return, Int
from tealer.teal.instructions.transaction_field import RekeyTo

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput


class MissingRekeyTo(AbstractDetector):

    NAME = "rekeyTo"
    DESCRIPTION = "Detect paths with a missing RekeyTo check"
    TYPE = DetectorType.STATEFULLGROUP

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

    def check_rekey_to(  # pylint: disable=too-many-arguments
        self,
        bb: BasicBlock,
        group_tx: Dict[int, Set[BasicBlock]],
        idx_fitlered: Set[int],
        current_path: List[BasicBlock],
        paths_without_check: List[List[BasicBlock]],
    ) -> None:
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
            self.check_rekey_to(next_bb, group_tx, idx_fitlered, current_path, paths_without_check)

    def detect(self) -> "SupportedOutput":

        paths_without_check: List[List[BasicBlock]] = []
        self.check_rekey_to(self.teal.bbs[0], defaultdict(set), set(), [], paths_without_check)

        description = "Lack of txn RekeyTo check allows rekeying the account to"
        description += " attacker controlled address and control the account directly"
        filename = "missing_rekeyto_check"

        return self.generate_result(paths_without_check, description, filename)
