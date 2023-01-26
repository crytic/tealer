"""Detector for finding execution paths missing RekeyTo check."""

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

    def detect(self) -> "SupportedOutput":
        """Detect execution paths with missing CloseRemainderTo check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        paths_without_check: List[List[BasicBlock]] = []

        def checks_field(block_ctx: "BlockTransactionContext") -> bool:
            # return False if RekeyTo field can have any address.
            # return True if RekeyTo should have some address or zero address
            return not block_ctx.rekeyto.any_addr

        paths_without_check += detect_missing_tx_field_validations(self.teal.bbs[0], checks_field)

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
