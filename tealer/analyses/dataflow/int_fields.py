from typing import TYPE_CHECKING, List, Set, Tuple, Dict

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
)
from tealer.teal.global_field import GroupSize
from tealer.teal.instructions.transaction_field import GroupIndex
from tealer.utils.analyses import is_int_push_ins

if TYPE_CHECKING:
    from tealer.teal.instructions.instructions import Instruction

group_size_key = "GroupSize"
group_index_key = "GroupIndex"
analysis_keys = [group_size_key, group_index_key]
universal_sets = {}
universal_sets[group_size_key] = list(range(1, 17))
universal_sets[group_index_key] = list(range(0, 16))


class IntFields(DataflowTransactionContext):  # pylint: disable=too-few-public-methods

    GROUP_SIZE_KEY = group_size_key
    GROUP_INDEX_KEY = group_index_key
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
        if len(ins_stack) < 3:
            return set(U), set(U)

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
                return set(U), set(U)

            ins = ins_stack[-1]
            asserted_values = self._get_asserted_int_values(ins, compared_value, U)
            return set(asserted_values), set(U) - set(asserted_values)
        return set(U), set(U)

    def _get_asserted(self, key: str, ins_stack: List["Instruction"]) -> Tuple[Set, Set]:
        if key == self.GROUP_SIZE_KEY:
            return self._get_asserted_groupsizes(ins_stack)
        return self._get_asserted_groupindices(ins_stack)

    def _store_results(self) -> None:
        group_size_block_context = self._block_contexts[self.GROUP_SIZE_KEY]
        for block in self._teal.bbs:
            block.transaction_context.group_sizes = list(group_size_block_context[block])

        group_index_block_context = self._block_contexts[self.GROUP_INDEX_KEY]
        for block in self._teal.bbs:
            block.transaction_context.group_indices = list(group_index_block_context[block])
