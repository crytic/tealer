from typing import TYPE_CHECKING, List, Set, Tuple

from tealer.analyses.dataflow.generic import DataflowTransactionContext
from tealer.teal.instructions.instructions import (
    Eq,
    Neq,
    Addr,
    Global,
    Gtxn,
    Txn,
)
from tealer.teal.instructions.parse_transaction_field import TX_FIELD_TXT_TO_OBJECT
from tealer.teal.global_field import ZeroAddress
from tealer.exceptions import TealerException


if TYPE_CHECKING:
    from tealer.teal.instructions.instructions import Instruction
    from tealer.teal.context.block_transaction_context import BlockTransactionContext


def gen_keys(tx_fields: List[str]) -> List[str]:
    for f in tx_fields:
        if f not in TX_FIELD_TXT_TO_OBJECT:
            # use field string as in TX_FIELD_TXT_TO_OBJECT
            raise TealerException("Use field string as in TX_FIELD_TXT_TO_OBJECT")

    # use format "Gtxn_{dd}_{field}" for gtxn fields
    keys = list(tx_fields)
    for field in tx_fields:
        for idx in range(16):
            keys.append(f"GTXN_{idx:02d}_{field}")

    return keys


# Add str of transaction field to find constraints on that field
TX_FIELDS = [
    "RekeyTo",
    "CloseRemainderTo",
    "AssetCloseTo",
]

TX_KEYS = gen_keys(TX_FIELDS)

ZERO_ADDRESS = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEVAL4QAJS7JHB4"

# used to represent universal address set
ANY_ADDRESS = "ANY_ADDRESS"
# used to represent null address set
NO_ADDRESS = "NO_ADDRESS"


class AddrFields(DataflowTransactionContext):  # pylint: disable=too-few-public-methods

    KEYS = TX_KEYS

    def _universal_set(self, key: str = "") -> Set:
        return set([ANY_ADDRESS])

    def _null_set(self, key: str = "") -> Set:
        return set([NO_ADDRESS])

    def _union(self, key: str, a: Set, b: Set) -> Set:
        """A union U = U, A union NullSet = A"""
        if ANY_ADDRESS in a or ANY_ADDRESS in b:
            return self._universal_set()

        if NO_ADDRESS in a and NO_ADDRESS in b:
            return self._null_set()
        if NO_ADDRESS in a:
            return b
        if NO_ADDRESS in b:
            return a

        return a | b

    def _intersection(self, key: str, a: Set, b: Set) -> Set:
        """A intersection NullSet = NullSet, A intersection U = A"""
        if NO_ADDRESS in a or NO_ADDRESS in b:
            return self._null_set()

        if ANY_ADDRESS in a and ANY_ADDRESS in b:
            return self._universal_set()
        if ANY_ADDRESS in a:
            return set(b)
        if ANY_ADDRESS in b:
            return set(a)

        return a & b

    def _get_asserted_address(self, ins: "Instruction") -> Set[str]:
        """return set of address which are represented by the ins

        ZeroAddress is considered to be null set.
        """
        if isinstance(ins, Global) and isinstance(ins.field, ZeroAddress):
            # ZeroAddress
            return self._null_set()
        if isinstance(ins, Addr):
            if ins.addr == ZERO_ADDRESS:
                return self._null_set()
            return set([ins.addr])
        return self._universal_set()

    @staticmethod
    def _is_txn_or_gtxn(key: str, ins: "Instruction") -> bool:
        if key.startswith("GTXN_"):
            idx = int(key[len("GTXN_") :][:2])
            field = key[len("GTXN_") + 2 + 1 :]
            return (
                isinstance(ins, Gtxn)
                and ins.idx == idx
                and isinstance(ins.field, TX_FIELD_TXT_TO_OBJECT[field])
            )
        return isinstance(ins, Txn) and isinstance(ins.field, TX_FIELD_TXT_TO_OBJECT[key])

    def _get_asserted_txn_gtxn(
        self, key: str, ins_stack: List["Instruction"]
    ) -> Tuple[Set[str], Set[str]]:
        if len(ins_stack) < 3 or not isinstance(ins_stack[-1], (Eq, Neq)):
            return self._universal_set(), self._universal_set()

        ins1 = ins_stack[-1]
        ins2 = ins_stack[-2]
        ins3 = ins_stack[-3]

        asserted_addresses = None
        if self._is_txn_or_gtxn(key, ins2):
            asserted_addresses = self._get_asserted_address(ins3)
        elif self._is_txn_or_gtxn(key, ins3):
            asserted_addresses = self._get_asserted_address(ins2)

        if asserted_addresses is None:
            return self._universal_set(), self._universal_set()

        if isinstance(ins1, Eq):
            return asserted_addresses, self._universal_set()
        return self._universal_set(), asserted_addresses

    def _get_asserted(self, key: str, ins_stack: List["Instruction"]) -> Tuple[Set, Set]:
        return self._get_asserted_txn_gtxn(key, ins_stack)

    @staticmethod
    def _set_rekeyto_values(ctx: "BlockTransactionContext", addr_values: Set[str]) -> None:
        ctx.any_rekeyto = ANY_ADDRESS in addr_values
        ctx.none_rekeyto = NO_ADDRESS in addr_values
        ctx.rekeyto = list(addr_values - set([ANY_ADDRESS, NO_ADDRESS]))

    @staticmethod
    def _set_closeto_values(ctx: "BlockTransactionContext", addr_values: Set[str]) -> None:
        ctx.any_closeto = ANY_ADDRESS in addr_values
        ctx.none_closeto = NO_ADDRESS in addr_values
        ctx.closeto = list(addr_values - set([ANY_ADDRESS, NO_ADDRESS]))

    @staticmethod
    def _set_assetcloseto_values(ctx: "BlockTransactionContext", addr_values: Set[str]) -> None:
        ctx.any_assetcloseto = ANY_ADDRESS in addr_values
        ctx.none_assetcloseto = NO_ADDRESS in addr_values
        ctx.assetcloseto = list(addr_values - set([ANY_ADDRESS, NO_ADDRESS]))

    def _store_results(self) -> None:
        rekeyto_key = "RekeyTo"
        for b in self._teal.bbs:
            self._set_rekeyto_values(b.transaction_context, self._block_contexts[rekeyto_key][b])

            for idx in range(16):
                addr_values = self._block_contexts[self._gtx_key(idx, rekeyto_key)][b]
                self._set_rekeyto_values(b.transaction_context.gtxn_context(idx), addr_values)

        closeto_key = "CloseRemainderTo"
        for b in self._teal.bbs:
            self._set_closeto_values(b.transaction_context, self._block_contexts[closeto_key][b])

            for idx in range(16):
                addr_values = self._block_contexts[self._gtx_key(idx, closeto_key)][b]
                self._set_closeto_values(b.transaction_context.gtxn_context(idx), addr_values)

        assetcloseto_key = "AssetCloseTo"
        for b in self._teal.bbs:
            self._set_assetcloseto_values(
                b.transaction_context, self._block_contexts[assetcloseto_key][b]
            )

            for idx in range(16):
                addr_values = self._block_contexts[self._gtx_key(idx, assetcloseto_key)][b]
                self._set_assetcloseto_values(b.transaction_context.gtxn_context(idx), addr_values)
