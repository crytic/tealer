from typing import TYPE_CHECKING, List, Set, Tuple

from tealer.analyses.dataflow.generic import DataflowTransactionContext
from tealer.teal.instructions.instructions import (
    Eq,
    Neq,
    Addr,
    Global,
)
from tealer.teal.global_field import ZeroAddress
from tealer.utils.algorand_constants import ZERO_ADDRESS
from tealer.analyses.utils.stack_emulator import KnownStackValue, UnknownStackValue

if TYPE_CHECKING:
    from tealer.teal.instructions.instructions import Instruction
    from tealer.teal.context.block_transaction_context import AddrFieldValue


# Add str of transaction field to find constraints on that field
# use field string as in TX_FIELD_TXT_TO_OBJECT
REKEY_TO_KEY = "RekeyTo"
CLOSE_REMAINDER_TO_KEY = "CloseRemainderTo"
ASSET_CLOSE_TO_KEY = "AssetCloseTo"

TX_FIELDS = [
    REKEY_TO_KEY,
    CLOSE_REMAINDER_TO_KEY,
    ASSET_CLOSE_TO_KEY,
]

# used to represent universal address set
ANY_ADDRESS = "ANY_ADDRESS"
# used to represent null address set
NO_ADDRESS = "NO_ADDRESS"
# used to represent single unknown address.
SOME_ADDRESS = "SOME_ADDRESS"


class AddrFields(DataflowTransactionContext):  # pylint: disable=too-few-public-methods

    BASE_KEYS: List[str] = TX_FIELDS
    KEYS_WITH_GTXN: List[str] = TX_FIELDS

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
        # return SOME_ADDRESS here
        # we don't know the address this particular instruction will return.
        # But it will only return a single address even though we don't know what it is.
        return set([f"{SOME_ADDRESS}_{ins}"])

    def _get_asserted_txn_gtxn(
        self, key: str, ins_stack_value: KnownStackValue
    ) -> Tuple[Set[str], Set[str]]:
        if not isinstance(ins_stack_value.instruction, (Eq, Neq)):
            return self._universal_set(), self._universal_set()

        arg1 = ins_stack_value.args[0]
        arg2 = ins_stack_value.args[1]

        asserted_addresses = None
        if isinstance(arg1, UnknownStackValue) and isinstance(arg2, UnknownStackValue):
            # arg1 and arg2 are unknown value.
            return self._universal_set(), self._universal_set()

        if isinstance(arg1, UnknownStackValue):
            if not isinstance(arg2, UnknownStackValue) and not self._is_txn_or_gtxn(
                key, arg2.instruction
            ):
                # arg1 is unknown and arg2 is not related to "key"
                return self._universal_set(), self._universal_set()
            # arg2 is related to "key" but arg1 is unknown
            asserted_addresses = set([SOME_ADDRESS])
        elif isinstance(arg2, UnknownStackValue):
            if not isinstance(arg1, UnknownStackValue) and not self._is_txn_or_gtxn(
                key, arg1.instruction
            ):
                # arg2 is unknown and arg1 is not related to "key"
                return self._universal_set(), self._universal_set()
            # arg1 is related to "key" but arg2 is unknown
            asserted_addresses = set([SOME_ADDRESS])
        elif self._is_txn_or_gtxn(key, arg1.instruction):
            asserted_addresses = self._get_asserted_address(arg2.instruction)
        elif self._is_txn_or_gtxn(key, arg2.instruction):
            asserted_addresses = self._get_asserted_address(arg1.instruction)

        if asserted_addresses is None:
            return self._universal_set(), self._universal_set()

        if isinstance(ins_stack_value.instruction, Eq):
            return asserted_addresses, self._universal_set()
        return self._universal_set(), asserted_addresses

    def _get_asserted_single(self, key: str, ins_stack_value: KnownStackValue) -> Tuple[Set, Set]:
        return self._get_asserted_txn_gtxn(key, ins_stack_value)

    @staticmethod
    def _set_addr_values(ctx_addr_value: "AddrFieldValue", addr_values: Set[str]) -> None:
        ctx_addr_value.any_addr = ANY_ADDRESS in addr_values
        ctx_addr_value.no_addr = NO_ADDRESS in addr_values
        ctx_addr_value.possible_addr = list(addr_values - set([ANY_ADDRESS, NO_ADDRESS]))

    def _store_results(self) -> None:
        rekeyto_key = "RekeyTo"
        for b in self._teal.bbs:
            self._set_addr_values(
                b.transaction_context.rekeyto, self._block_contexts[rekeyto_key][b]
            )

            for idx in range(16):
                addr_values = self._block_contexts[self.gtx_key(idx, rekeyto_key)][b]
                self._set_addr_values(b.transaction_context.gtxn_context(idx).rekeyto, addr_values)

        closeto_key = "CloseRemainderTo"
        for b in self._teal.bbs:
            self._set_addr_values(
                b.transaction_context.closeto, self._block_contexts[closeto_key][b]
            )

            for idx in range(16):
                addr_values = self._block_contexts[self.gtx_key(idx, closeto_key)][b]
                self._set_addr_values(b.transaction_context.gtxn_context(idx).closeto, addr_values)

        assetcloseto_key = "AssetCloseTo"
        for b in self._teal.bbs:
            self._set_addr_values(
                b.transaction_context.assetcloseto, self._block_contexts[assetcloseto_key][b]
            )

            for idx in range(16):
                addr_values = self._block_contexts[self.gtx_key(idx, assetcloseto_key)][b]
                self._set_addr_values(
                    b.transaction_context.gtxn_context(idx).assetcloseto, addr_values
                )
