"""Detector for finding execution paths missing RekeyTo check."""

from collections import defaultdict
from copy import copy
from typing import Dict, Set, List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Gtxn, Return, Int
from tealer.teal.instructions.transaction_field import RekeyTo
from tealer.utils.analyses import detect_missing_txn_check

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput


class MissingRekeyTo(AbstractDetector):
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

    def check_rekey_to_group(  # pylint: disable=too-many-arguments
        self,
        bb: BasicBlock,
        group_tx: Dict[int, Set[BasicBlock]],
        idx_filtered: Set[int],
        current_path: List[BasicBlock],
        paths_without_check: List[List[BasicBlock]],
    ) -> None:
        """Find execution paths with missing rekey checks of other transactions in the group.

        This check finds paths which doesn't check RekeyTo field of other transactions in the group.
        Information about index of other transactions in the group is calculated using Gtxn instruction.
        Suppose, if there's an instruction `Gtxn 2 Sender`, then 2 is the index of other transaction
        in the group and function checks for instruction `Gtxn 2 RekeyTo` and reports execution paths
        missing that check. This is repeated for all indexes of group transactions found.

        This function is "in place", modifies arguments with the data it is
        supposed to return.

        Args:
            bb: Current basic block being checked(whose execution is simulated.)
            group_tx: Map from transaction index to the related basic blocks.
            idx_filtered: Indexes of transaction whose RekeyTo property is already checked.
            current_path: Current execution path being explored.
            paths_without_check:
                Execution paths with missing RekeyTo check. This is a
                "in place" argument. Vulnerable paths found by this function are
                appended to this list.
        """

        # check for loops
        if bb in current_path:
            return

        current_path = current_path + [bb]

        group_tx = copy(group_tx)
        for ins in bb.instructions:
            if isinstance(ins, Gtxn):
                if ins.idx not in idx_filtered:
                    assert ins.bb
                    group_tx[ins.idx].add(ins.bb)

                if isinstance(ins.field, RekeyTo):
                    del group_tx[ins.idx]
                    idx_filtered = set(idx_filtered)
                    idx_filtered.add(ins.idx)

            if isinstance(ins, Return) and group_tx:
                if len(ins.prev) == 1:
                    prev = ins.prev[0]
                    if isinstance(prev, Int) and prev.value == 0:
                        return

                paths_without_check.append(current_path)

        for next_bb in bb.next:
            self.check_rekey_to_group(
                next_bb, group_tx, idx_filtered, current_path, paths_without_check
            )

    def detect(self) -> "SupportedOutput":
        """Detect execution paths with missing CloseRemainderTo check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        paths_without_check: List[List[BasicBlock]] = []
        self.check_rekey_to_group(
            self.teal.bbs[0], defaultdict(set), set(), [], paths_without_check
        )

        detect_missing_txn_check(RekeyTo, self.teal.bbs[0], [], paths_without_check)

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
