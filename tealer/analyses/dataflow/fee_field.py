from typing import TYPE_CHECKING, List, Tuple, Union, Optional

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
from tealer.analyses.utils.stack_emulator import KnownStackValue, UnknownStackValue

if TYPE_CHECKING:
    from tealer.teal.instructions.instructions import Instruction

FEE_KEY = "Fee"

SOME_INT = "UnknownBoundedInt"  # Represent a value that is between 0 < x < MAX_UINT64


class FeeField(DataflowTransactionContext):

    BASE_KEYS: List[str] = [FEE_KEY]
    KEYS_WITH_GTXN: List[str] = [FEE_KEY]

    def _universal_set(self, key: str) -> int:
        # MAX possible value for the Fee field
        return MAX_UINT64

    def _null_set(self, key: str) -> int:
        return 0

    def _union(self, key: str, a: Union[int, str], b: Union[int, str]) -> Union[int, str]:
        if isinstance(a, str) and isinstance(b, str):
            # Both are unknown values between 0 < x < MAX_UINT64
            return a
        if isinstance(a, str):
            # a is a unknown bounded value and b is int
            # a: 0 < x < MAX_UINT64
            if b == self._universal_set(key):
                return b  # a is less than MAX_UINT64
            return a
        if isinstance(b, str):
            # b is a unknown bounded value and a is int
            # b: 0 < x < MAX_UINT64
            if a == self._universal_set(key):
                return a  # b is less than MAX_UINT64
            return b
        # both are ints
        return max(a, b)

    def _intersection(self, key: str, a: Union[int, str], b: Union[int, str]) -> Union[int, str]:
        if isinstance(a, str) and isinstance(b, str):
            # Both are unknown values between 0 < x < MAX_UINT64
            return a
        if isinstance(a, str):
            # a is a unknown bounded value and b is int
            # a: 0 < x < MAX_UINT64
            if b == self._universal_set(key):
                return a  # a is less than MAX_UINT64
            return b
        if isinstance(b, str):
            # b is a unknown bounded value and a is int
            # b: 0 < x < MAX_UINT64
            if a == self._universal_set(key):
                return b  # b is less than MAX_UINT64
            return a
        # both are ints
        return min(a, b)

    @staticmethod
    def _get_asserted_max_value(
        comparison_ins: "Instruction", compared_int: Union[int, str], max_possible_value: int
    ) -> Tuple[Union[int, str], Union[int, str]]:
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
            if isinstance(compared_int, str):
                return compared_int, U
            return max(0, compared_int - 1), U
        if isinstance(comparison_ins, LessE):
            # x <= i => i, U
            return compared_int, U
        if isinstance(comparison_ins, Greater):
            # x > i => U, i
            return U, compared_int
        if isinstance(comparison_ins, GreaterE):
            # x >= i => U, (i - 1)
            if isinstance(compared_int, str):
                return U, compared_int
            return U, max(0, compared_int - 1)
        return U, U

    def _get_asserted_fee(  # pylint: disable=too-many-branches
        self, key: str, ins_stack_value: KnownStackValue
    ) -> Tuple[Union[int, str], Union[int, str]]:
        U = self._universal_set(key)  # max value for the field

        if isinstance(ins_stack_value.instruction, (Eq, Neq, Less, LessE, Greater, GreaterE)):
            arg1 = ins_stack_value.args[0]
            arg2 = ins_stack_value.args[1]
            compared_value: Optional[Union[int, str]] = None

            if isinstance(arg1, UnknownStackValue) and isinstance(arg2, UnknownStackValue):
                # Both the args are unknown
                return U, U

            if isinstance(arg1, UnknownStackValue):
                if not isinstance(arg2, UnknownStackValue) and not self._is_txn_or_gtxn(
                    key, arg2.instruction
                ):
                    # arg1 is unknown and arg2 is not related to "key"
                    return U, U
                # arg2 is related to key and arg1 is some unknown value
                compared_value = SOME_INT
            elif isinstance(arg2, UnknownStackValue):
                if not isinstance(arg1, UnknownStackValue) and not self._is_txn_or_gtxn(
                    key, arg1.instruction
                ):
                    # arg2 is unknown and arg1 is not related to "key"
                    return self._universal_set(key), self._universal_set(key)
                # arg1 is related to "key" and arg2 is some unknown int value
                compared_value = SOME_INT
            elif self._is_txn_or_gtxn(key, arg1.instruction):
                is_int, value = is_int_push_ins(arg2.instruction)
                if is_int:
                    compared_value = value
                else:
                    compared_value = SOME_INT

            elif self._is_txn_or_gtxn(key, arg2.instruction):
                is_int, value = is_int_push_ins(arg1.instruction)
                if is_int:
                    compared_value = value
                else:
                    compared_value = SOME_INT

            if compared_value is None:
                # compared_value is not int.
                return U, U

            ins = ins_stack_value.instruction
            return self._get_asserted_max_value(ins, compared_value, U)
        return U, U

    def _get_asserted_single(
        self, key: str, ins_stack_value: KnownStackValue
    ) -> Tuple[Union[int, str], Union[int, str]]:
        res = self._get_asserted_fee(key, ins_stack_value)
        return res

    def _store_results(self) -> None:
        for b in self._teal.bbs:
            max_fee = self._block_contexts[FEE_KEY][b]
            if isinstance(max_fee, str):
                b.transaction_context.max_fee_unknown = True
            else:
                b.transaction_context.max_fee = max_fee
            for idx in range(MAX_GROUP_SIZE):
                max_fee = self._block_contexts[self.gtx_key(idx, FEE_KEY)][b]
                if isinstance(max_fee, str):
                    b.transaction_context.gtxn_context(idx).max_fee_unknown = True
                else:
                    b.transaction_context.gtxn_context(idx).max_fee = max_fee
