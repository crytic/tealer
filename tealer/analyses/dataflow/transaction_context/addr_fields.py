from typing import TYPE_CHECKING, List, Set, Tuple, Callable

from tealer.analyses.dataflow.transaction_context.generic import DataflowTransactionContext
from tealer.analyses.dataflow.transaction_context.utils.key_helpers import (
    get_gtxn_at_index_key,
    is_value_matches_key,
    get_absolute_index_key,
    get_relative_index_key,
)
from tealer.teal.instructions.instructions import (
    Eq,
    Neq,
    Addr,
    Global,
)
from tealer.teal.global_field import ZeroAddress, CreatorAddress
from tealer.utils.algorand_constants import ZERO_ADDRESS
from tealer.analyses.utils.stack_ast_builder import KnownStackValue, UnknownStackValue
from tealer.utils.algorand_constants import MAX_GROUP_SIZE

if TYPE_CHECKING:
    from tealer.teal.instructions.instructions import Instruction
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.context.block_transaction_context import (
        AddrFieldValue,
        BlockTransactionContext,
    )


# TODO: Change representation of address values to something similar to FeeValue
# - Store possible addresses and not possible address. Neq(Txn Sender, addr x). store Sender cannot be x
# - ...

# Add str of transaction field to find constraints on that field
# use field string as in TX_FIELD_TXT_TO_OBJECT
REKEY_TO_KEY = "RekeyTo"
CLOSE_REMAINDER_TO_KEY = "CloseRemainderTo"
ASSET_CLOSE_TO_KEY = "AssetCloseTo"
SENDER_KEY = "Sender"

TX_FIELDS = [
    REKEY_TO_KEY,
    CLOSE_REMAINDER_TO_KEY,
    ASSET_CLOSE_TO_KEY,
    SENDER_KEY,
]

# used to represent universal address set
ANY_ADDRESS = "ANY_ADDRESS"
# used to represent null address set
NO_ADDRESS = "NO_ADDRESS"
# used to represent single unknown address.
SOME_ADDRESS = "SOME_ADDRESS"
# used to represent application's creator address returned by `global CreatorAddress`
# distinguishing creator address will be helpful for the fuzzer (?)
CREATOR_ADDRESS = "CREATOR_ADDRESS"


class AddrFields(DataflowTransactionContext):  # pylint: disable=too-few-public-methods

    BASE_KEYS: List[str] = TX_FIELDS
    KEYS_WITH_GTXN: List[str] = TX_FIELDS

    def _universal_set(self, key: str = "") -> Set:
        return set([ANY_ADDRESS])

    def _null_set(self, key: str = "") -> Set:
        return set([NO_ADDRESS])

    def _union(self, key: str, a: Set, b: Set) -> Set:
        """A union U = U, A union NullSet = A

        Args:
            key: The analysis key. The values in set :a: and :b: are values for this key.
            a: Set 1.
            b: Set 2.

        Returns:
            Returns union of set a and b.
        """
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
        """A intersection NullSet = NullSet, A intersection U = A

        Args:
            key: The analysis key. The values in set :a: and :b: are values for this key.
            a: Set 1.
            b: Set 2.

        Returns:
            Returns union of set a and b.
        """
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

        Args:
            ins: An instruction. The function considers that executing :ins: pushes an
                "address" value onto the stack. Based on the instruction, the function
                returns list of possible values.

        Returns:
            Returns a list of possible address values for the field when that field value is
            asserted against the output of :ins:.
        """
        if isinstance(ins, Global) and isinstance(ins.field, ZeroAddress):
            # ZeroAddress
            return self._null_set()
        if isinstance(ins, Addr):
            if ins.addr == ZERO_ADDRESS:
                return self._null_set()
            return set([ins.addr])
        if isinstance(ins, Global) and isinstance(ins.field, CreatorAddress):
            return set([CREATOR_ADDRESS])
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
            if not isinstance(arg2, UnknownStackValue) and not is_value_matches_key(key, arg2):
                # arg1 is unknown and arg2 is not related to "key"
                return self._universal_set(), self._universal_set()
            # arg2 is related to "key" but arg1 is unknown
            asserted_addresses = set([SOME_ADDRESS])
        elif isinstance(arg2, UnknownStackValue):
            if not isinstance(arg1, UnknownStackValue) and not is_value_matches_key(key, arg1):
                # arg2 is unknown and arg1 is not related to "key"
                return self._universal_set(), self._universal_set()
            # arg1 is related to "key" but arg2 is unknown
            asserted_addresses = set([SOME_ADDRESS])
        elif is_value_matches_key(key, arg1):
            asserted_addresses = self._get_asserted_address(arg2.instruction)
        elif is_value_matches_key(key, arg2):
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
        key_and_addr_obj: List[
            Tuple[str, Callable[["BlockTransactionContext"], "AddrFieldValue"]]
        ] = [
            (REKEY_TO_KEY, lambda ctx: ctx.rekeyto),
            (CLOSE_REMAINDER_TO_KEY, lambda ctx: ctx.closeto),
            (ASSET_CLOSE_TO_KEY, lambda ctx: ctx.assetcloseto),
            (SENDER_KEY, lambda ctx: ctx.sender),
        ]
        for key, addr_field_obj in key_and_addr_obj:
            if key not in self.BASE_KEYS:
                continue
            for block in self._function.blocks:
                self._set_addr_values(
                    addr_field_obj(self._function.transaction_context(block)),
                    self._block_contexts[key][block],
                )
                for idx in range(16):
                    addr_values = self._block_contexts[get_gtxn_at_index_key(idx, key)][block]
                    self._set_addr_values(
                        addr_field_obj(self._function.transaction_context(block).gtxn_context(idx)),
                        addr_values,
                    )

                    abs_addr_values = self._block_contexts[get_absolute_index_key(idx, key)][block]
                    self._set_addr_values(
                        addr_field_obj(
                            self._function.transaction_context(block).absolute_context(idx)
                        ),
                        abs_addr_values,
                    )

                for offset in range(-(MAX_GROUP_SIZE - 1), MAX_GROUP_SIZE):
                    if offset == 0:
                        continue
                    rel_addr_values = self._block_contexts[get_relative_index_key(offset, key)][
                        block
                    ]
                    self._set_addr_values(
                        addr_field_obj(
                            self._function.transaction_context(block).relative_context(offset)
                        ),
                        rel_addr_values,
                    )
