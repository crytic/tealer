from typing import TYPE_CHECKING, List, Tuple

from tealer.analyses.dataflow.generic import DataflowTransactionContext
from tealer.teal.instructions.instructions import (
    Eq,
    Neq,
    Greater,
    GreaterE,
    Less,
    LessE,
)
from tealer.utils.analyses import is_int_push_ins
from tealer.utils.algorand_constants import MAX_GROUP_SIZE, MAX_UINT64

if TYPE_CHECKING:
    from tealer.teal.instructions.instructions import Instruction

FEE_KEY = "Fee"


class FeeField(DataflowTransactionContext):

    BASE_KEYS: List[str] = [FEE_KEY]
    KEYS_WITH_GTXN: List[str] = [FEE_KEY]

    def _universal_set(self, key: str) -> int:
        # MAX possible value for the Fee field
        return MAX_UINT64

    def _null_set(self, key: str) -> int:
        return 0

    def _union(self, key: str, a: int, b: int) -> int:
        return max(a, b)

    def _intersection(self, key: str, a: int, b: int) -> int:
        return min(a, b)

    @staticmethod
    def _get_asserted_max_value(
        comparison_ins: "Instruction", compared_int: int, max_possible_value: int
    ) -> Tuple[int, int]:
        """Return maximum possible value that will make the comparison True and maximum
        possible value that will make the comparison False. Both values are upper bounded
        by arg "max_possible_value".

        Args:
            comparison_ins: Comparison operator.
            compared_int: int value being compared with.
            max_possible_value: Maximum possible value for the compared field.
        Returns:
            Tuple[int, int]: Max possible value that will make the comparison instruction return True and
                Max possible value that will make the comparison False.
        """
        U = max_possible_value  # universal set
        if isinstance(comparison_ins, Eq):
            # x == i => i, U
            return compared_int, U
        if isinstance(comparison_ins, Neq):
            # x != i => U, i
            return U, compared_int
        if isinstance(comparison_ins, Less):
            # x < i => (i - 1), U
            return max(0, compared_int - 1), U
        if isinstance(comparison_ins, LessE):
            # x <= i => i, U
            return compared_int, U
        if isinstance(comparison_ins, Greater):
            # x > i => U, i
            return U, compared_int
        if isinstance(comparison_ins, GreaterE):
            # x >= i => U, (i - 1)
            return U, max(0, compared_int - 1)
        return U, U

    def _get_asserted_fee(self, key: str, ins_stack: List["Instruction"]) -> Tuple[int, int]:
        U = self._universal_set(key)  # max value for the field
        if len(ins_stack) < 3:
            return U, U

        if isinstance(ins_stack[-1], (Eq, Neq, Less, LessE, Greater, GreaterE)):
            ins1 = ins_stack[-2]
            ins2 = ins_stack[-3]
            compared_value = None

            if self._is_txn_or_gtxn(key, ins1):
                is_int, value = is_int_push_ins(ins2)
                if is_int:
                    compared_value = value
            elif self._is_txn_or_gtxn(key, ins2):
                is_int, value = is_int_push_ins(ins1)
                if is_int:
                    compared_value = value

            if compared_value is None or not isinstance(compared_value, int):
                # compared_value is not int.
                return U, U

            ins = ins_stack[-1]
            return self._get_asserted_max_value(ins, compared_value, U)
        return U, U

    def _get_asserted(self, key: str, ins_stack: List["Instruction"]) -> Tuple[int, int]:
        res = self._get_asserted_fee(key, ins_stack)
        return res

    def _store_results(self) -> None:
        for b in self._teal.bbs:
            b.transaction_context.max_fee = self._block_contexts[FEE_KEY][b]
            for idx in range(MAX_GROUP_SIZE):
                b.transaction_context.gtxn_context(idx).max_fee = self._block_contexts[
                    self.gtx_key(idx, FEE_KEY)
                ][b]
