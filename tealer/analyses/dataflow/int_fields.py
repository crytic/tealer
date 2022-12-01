from typing import TYPE_CHECKING, List, Set, Tuple, Dict, Type

from tealer.analyses.dataflow.generic import DataflowTransactionContext
from tealer.teal.instructions.instructions import (
    Global,
    Eq,
    Neq,
    Greater,
    GreaterE,
    Less,
    LessE,
    Txn,
    Gtxn,
    Not,
)
from tealer.teal.global_field import GroupSize
from tealer.teal.instructions.transaction_field import (
    GroupIndex,
    ApplicationID,
    TypeEnum,
    OnCompletion,
)
from tealer.utils.teal_enums import TealerTransactionType
from tealer.utils.teal_enums import (
    ALL_TRANSACTION_TYPES,
    APPLICATION_TRANSACTION_TYPES,
    TYPEENUM_TRANSACTION_TYPES,
)
from tealer.utils.teal_enums import oncompletion_to_tealer_type, transaction_type_to_tealer_type
from tealer.utils.analyses import is_int_push_ins

if TYPE_CHECKING:
    from tealer.teal.instructions.instructions import Instruction
    from tealer.teal.instructions.transaction_field import TransactionField

MAX_GROUP_SIZE = 16

group_size_key = "GroupSize"
group_index_key = "GroupIndex"
transaction_type_key = "TransactionType"
analysis_keys = [group_size_key, group_index_key, transaction_type_key]
analysis_keys += [f"GTXN_{i:02d}_{transaction_type_key}" for i in range(MAX_GROUP_SIZE)]
universal_sets: Dict[str, List] = {
    f"GTXN_{i:02d}_{transaction_type_key}": list(ALL_TRANSACTION_TYPES)
    for i in range(MAX_GROUP_SIZE)
}
universal_sets[group_size_key] = list(range(1, MAX_GROUP_SIZE + 1))
universal_sets[group_index_key] = list(range(0, MAX_GROUP_SIZE))
universal_sets[transaction_type_key] = list(ALL_TRANSACTION_TYPES)


class IntFields(DataflowTransactionContext):  # pylint: disable=too-few-public-methods

    GROUP_SIZE_KEY = group_size_key
    GROUP_INDEX_KEY = group_index_key
    TRANSACTION_TYPE_KEY = transaction_type_key
    KEYS = analysis_keys
    UNIVERSAL_SETS: Dict[str, List] = universal_sets

    def _universal_set(self, key: str) -> Set:  # pylint: disable=no-self-use
        return set(self.UNIVERSAL_SETS[key])

    def _null_set(self, key: str) -> Set:  # pylint: disable=no-self-use
        return set()

    def _union(self, key: str, a: Set, b: Set) -> Set:  # pylint: disable=no-self-use
        return a | b

    def _intersection(self, key: str, a: Set, b: Set) -> Set:  # pylint: disable=no-self-use
        return a & b

    def _get_asserted_int_values(  # pylint: disable=no-self-use
        self, comparison_ins: "Instruction", compared_int: int, universal_set: List[int]
    ) -> List[int]:
        """return list of ints from universal set(U) that will satisfy the comparison.

        if the given condition uses ==, return compared int list.
        if the condition uses != then return {U - compared_int}
        if the given condition uses <, return U[ : U.index(compared_int)]
        if the given condition uses <=, return U[ : U.index(compared_int) + 1]
        if the given condition uses >, return U[U.index(compared_int) + 1:]
        if the given condition uses >=, return U[U.index(compared_int): ]

        Args:
            comparison_ins: comparison instruction used. can be [==, !=, <, <=, >, >=]
            compared_int: integer value compared.
            universal_set: list of all possible integer values for the field.

        Returns:
            list of ints that will satisfy the comparison
        """
        U = universal_set

        if isinstance(comparison_ins, Eq):  # pylint: disable=no-else-return
            return [compared_int]
        elif isinstance(comparison_ins, Neq):
            if compared_int in U:
                U.remove(compared_int)
            return U
        elif isinstance(comparison_ins, Less):
            return [i for i in U if i < compared_int]
        elif isinstance(comparison_ins, LessE):
            return [i for i in U if i <= compared_int]
        elif isinstance(comparison_ins, Greater):
            return [i for i in U if i > compared_int]
        elif isinstance(comparison_ins, GreaterE):
            return [i for i in U if i >= compared_int]
        else:
            return U

    def _get_asserted_groupsizes(self, ins_stack: List["Instruction"]) -> Tuple[Set[int], Set[int]]:
        """return set of values for groupsize that will make the comparison true and false

        checks for instruction sequence and returns group size values that will make the comparison true.

        [ Global GroupSize | (int | pushint)]
        [ (int | pushint) | Global GroupSize]
        [ == | != | < | <= | > | >=]

        Args:
            ins_stack: list of instructions that are executed up until the comparison instruction (including the comparison instruction).

        Returns:
            set of groupsize values that will make the comparison true, set of groupsize values that will make the comparison false.
        """
        U = list(self.UNIVERSAL_SETS[self.GROUP_SIZE_KEY])
        if len(ins_stack) < 3:
            return set(U), set(U)

        if isinstance(ins_stack[-1], (Eq, Neq, Less, LessE, Greater, GreaterE)):
            ins1 = ins_stack[-2]
            ins2 = ins_stack[-3]
            compared_value = None

            if isinstance(ins1, Global) and isinstance(ins1.field, GroupSize):
                is_int, value = is_int_push_ins(ins2)
                if is_int:
                    compared_value = value
            elif isinstance(ins2, Global) and isinstance(ins2.field, GroupSize):
                is_int, value = is_int_push_ins(ins1)
                if is_int:
                    compared_value = value

            if compared_value is None or not isinstance(compared_value, int):
                # if the comparison does not check groupsize, return U as values that make the comparison false
                return set(U), set(U)

            ins = ins_stack[-1]
            asserted_values = self._get_asserted_int_values(ins, compared_value, U)
            return set(asserted_values), set(U) - set(asserted_values)
        return set(U), set(U)

    def _get_asserted_groupindices(
        self, ins_stack: List["Instruction"]
    ) -> Tuple[Set[int], Set[int]]:
        """return list of values for group index that will make the comparison true and false

        checks for instruction sequence and returns group index values that will make the comparison true.

        [ txn GroupIndex | (int | pushint)]
        [ (int | pushint) | txn GroupIndex]
        [ == | != | < | <= | > | >=]

        Args:
            ins_stack: list of instructions that are executed up until the comparison instruction (including the comparison instruction).

        Returns:
            List of groupindex values that will make the comparison true.
        """
        U = list(self.UNIVERSAL_SETS[self.GROUP_INDEX_KEY])
        true_group_sizes, false_group_sizes = self._get_asserted_groupsizes(ins_stack)
        # group index must be less than maximum possible group size.
        # true_group_sizes -> possible values for group size that will return true_value.
        # false_group_sizes -> possible values for group size that will return false_value.
        true_group_indices, false_group_indices = set(
            range(0, max(true_group_sizes, default=0))
        ), set(range(0, max(false_group_sizes, default=0)))

        if len(ins_stack) < 3:
            # U intersection A = A, where U is universal set
            # set(U) & true_group_indices = true_group_indices, same for false_group_indices
            return true_group_indices, false_group_indices

        if isinstance(ins_stack[-1], (Eq, Neq, Less, LessE, Greater, GreaterE)):
            ins1 = ins_stack[-2]
            ins2 = ins_stack[-3]
            compared_value = None

            if isinstance(ins1, Txn) and isinstance(ins1.field, GroupIndex):
                is_int, value = is_int_push_ins(ins2)
                if is_int:
                    compared_value = value
            elif isinstance(ins2, Txn) and isinstance(ins2.field, GroupIndex):
                is_int, value = is_int_push_ins(ins1)
                if is_int:
                    compared_value = value

            if compared_value is None or not isinstance(compared_value, int):
                # set(U) & true_group_indices = true_group_indices, same for false_group_indices
                return true_group_indices, false_group_indices

            ins = ins_stack[-1]
            asserted_values = self._get_asserted_int_values(ins, compared_value, U)
            return (
                set(asserted_values) & true_group_indices,
                (set(U) - set(asserted_values)) & false_group_indices,
            )
        # set(U) & true_group_indices = true_group_indices, same for false_group_indices
        return true_group_indices, false_group_indices

    def _is_ins_tx_field(  # pylint: disable=no-self-use
        self, key: str, ins: "Instruction", field: Type["TransactionField"]
    ) -> bool:
        """return True if ins is "txn {field}" or ins is gtxn {idx} field"""
        if key.startswith("GTXN_"):
            idx = int(key[len("GTXN_") :][:2])
            return isinstance(ins, Gtxn) and ins.idx == idx and isinstance(ins.field, field)
        return isinstance(ins, Txn) and isinstance(ins.field, field)

    def _get_asserted_transaction_types(  # pylint: disable=too-many-branches
        self, key: str, ins_stack: List["Instruction"]
    ) -> Tuple[Set["TealerTransactionType"], Set["TealerTransactionType"]]:
        """return set of transaction type that make the comparison true and a set that make false.

        considered instruction patterns:
        [g]txn [idx] ApplicationID
        bz/bnz

        [g]txn [idx] ApplicationID
        !
        bz/bnz

        [g]txn [idx] ApplicationID
        int 0
        ( == | != )
        bz/bnz

        [g]txn [idx] TypeEnum
        int [pay | acfg | axfer | appl ..]
        ( == | != )
        bz/bnz

        [g]txn [idx] OnCompletion
        int [UpdateApplication | DeleteApplication | ...]
        ( == | != )
        bz/bnz
        """
        U = set(self.UNIVERSAL_SETS[self.TRANSACTION_TYPE_KEY])
        if len(ins_stack) == 0:
            return set(U), set(U)

        ins1 = ins_stack[-1]
        if self._is_ins_tx_field(key, ins1, ApplicationID):
            # txn ApplicationID pushes 0 if this Application creation transaction elses pushes nonzero
            return set(APPLICATION_TRANSACTION_TYPES) - set(
                [TealerTransactionType.ApplCreation]
            ), set([TealerTransactionType.ApplCreation])

        if len(ins_stack) > 1:
            ins2 = ins_stack[-2]
            if isinstance(ins1, Not) and self._is_ins_tx_field(key, ins2, ApplicationID):
                # txn ApplicationID
                # !
                # return
                return set([TealerTransactionType.ApplCreation]), set(
                    APPLICATION_TRANSACTION_TYPES
                ) - set([TealerTransactionType.ApplCreation])

        if len(ins_stack) < 3:
            return set(U), set(U)

        if isinstance(ins1, (Eq, Neq)):
            ins2 = ins_stack[-2]
            ins3 = ins_stack[-3]

            is_int_ins2, value_2 = is_int_push_ins(ins2)
            is_int_ins3, value_3 = is_int_push_ins(ins3)

            if (is_int_ins2 and is_int_ins3) or ((not is_int_ins2) and (not is_int_ins3)):
                # if both are ints or both are not ints
                return set(U), set(U)

            true_values, false_values = None, None
            if self._is_ins_tx_field(key, ins2, ApplicationID):
                true_values, false_values = set([TealerTransactionType.ApplCreation]), set(
                    APPLICATION_TRANSACTION_TYPES
                ) - set([TealerTransactionType.ApplCreation])
            elif self._is_ins_tx_field(key, ins3, ApplicationID):
                true_values, false_values = set([TealerTransactionType.ApplCreation]), set(
                    APPLICATION_TRANSACTION_TYPES
                ) - set([TealerTransactionType.ApplCreation])

            if self._is_ins_tx_field(key, ins2, TypeEnum) and value_3 is not None:
                compared_type = transaction_type_to_tealer_type(value_3)
                true_values, false_values = set([compared_type]), set(
                    TYPEENUM_TRANSACTION_TYPES
                ) - set([compared_type])
            elif self._is_ins_tx_field(key, ins3, TypeEnum) and value_2 is not None:
                compared_type = transaction_type_to_tealer_type(value_2)
                true_values, false_values = set([compared_type]), set(
                    TYPEENUM_TRANSACTION_TYPES
                ) - set([compared_type])

            if self._is_ins_tx_field(key, ins2, OnCompletion) and value_3 is not None:
                compared_on_completion = oncompletion_to_tealer_type(value_3)
                true_values, false_values = set([compared_on_completion]), set(
                    APPLICATION_TRANSACTION_TYPES
                ) - set([compared_on_completion])
            elif self._is_ins_tx_field(key, ins3, OnCompletion) and value_2 is not None:
                compared_on_completion = oncompletion_to_tealer_type(value_2)
                true_values, false_values = set([compared_on_completion]), set(
                    APPLICATION_TRANSACTION_TYPES
                ) - set([compared_on_completion])

            if true_values is not None and false_values is not None:
                if isinstance(ins1, Eq):
                    return true_values, false_values
                return false_values, true_values

        return set(U), set(U)

    def _get_asserted(self, key: str, ins_stack: List["Instruction"]) -> Tuple[Set, Set]:
        if key == self.GROUP_SIZE_KEY:  # pylint: disable=no-else-return
            return self._get_asserted_groupsizes(ins_stack)
        elif key == self.GROUP_INDEX_KEY:
            return self._get_asserted_groupindices(ins_stack)
        return self._get_asserted_transaction_types(key, ins_stack)

    def _store_results(self) -> None:
        group_size_block_context = self._block_contexts[self.GROUP_SIZE_KEY]
        for block in self._teal.bbs:
            block.transaction_context.group_sizes = list(group_size_block_context[block])

        group_index_block_context = self._block_contexts[self.GROUP_INDEX_KEY]
        for block in self._teal.bbs:
            block.transaction_context.group_indices = list(group_index_block_context[block])

        transaction_type_context = self._block_contexts[self.TRANSACTION_TYPE_KEY]
        for block in self._teal.bbs:
            block.transaction_context.transaction_types = list(transaction_type_context[block])

            for idx in range(16):
                values = self._block_contexts[self._gtx_key(idx, self.TRANSACTION_TYPE_KEY)][block]
                block.transaction_context.gtxn_context(idx).transaction_types = values
