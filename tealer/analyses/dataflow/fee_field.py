from typing import TYPE_CHECKING, List, Tuple, Optional
from dataclasses import dataclass

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
from tealer.utils.algorand_constants import MAX_GROUP_SIZE, MAX_UINT64, MAX_TRANSACTION_COST
from tealer.analyses.utils.stack_ast_builder import KnownStackValue, UnknownStackValue

if TYPE_CHECKING:
    from tealer.teal.instructions.instructions import Instruction


# It's not always possible to know the integer value used to compare Fee.
# All the unknown values are represented using FeeValue(is_unknown=True).
# Tealer does not report paths if Fee is less than MAX_TRANSACTION_COST.
# UnknownBoundedInt is assumed to be a value between 0 and MAX_TRANSACTION_COST
# Tealer does not report paths if Fee is checked against some unknown value.

FEE_KEY = "Fee"


@dataclass
class FeeValue:
    is_unknown: bool = False  # max(unknown_value) == MAX_TRANSACTION_COST
    value: int = MAX_UINT64  # use value if and only if is_unknown is False.


# Note: if Fee field analysis is only used by the detector, it might be enough to represent unknown value with int(MAX_TRANSACTION_COST)
# However, if Fee field analysis is used by other components or tools(Fuzzer?), it is important to differentiate unknown and known values.


class FeeField(DataflowTransactionContext):

    BASE_KEYS: List[str] = [FEE_KEY]
    KEYS_WITH_GTXN: List[str] = [FEE_KEY]

    def _universal_set(self, key: str) -> FeeValue:
        # MAX possible value for the Fee field
        return FeeValue()

    def _null_set(self, key: str) -> FeeValue:
        return FeeValue(value=0)

    # def _union(self, key: str, a: Union[int, str], b: Union[int, str]) -> Union[int, str]:
    def _union(self, key: str, a: FeeValue, b: FeeValue) -> FeeValue:
        if a.is_unknown and b.is_unknown:
            # Both are unknown values between 0 < x <= MAX_TRANSACTION_COST
            return a
        if a.is_unknown:
            # a is a unknown bounded value and b is known value
            # a: 0 < x < MAX_TRANSACTION_COST
            if b.value > MAX_TRANSACTION_COST:
                return b
            return a  # a is less than MAX_TRANSACTION_COST
        if b.is_unknown:
            # b is a unknown bounded value and a is known value
            # b: 0 < x < MAX_TRANSACTION_COST
            if a.value > MAX_TRANSACTION_COST:
                return a  # b is less than MAX_TRANSACTION_COST
            return b
        # both are known values
        return a if a.value > b.value else b

    def _intersection(self, key: str, a: FeeValue, b: FeeValue) -> FeeValue:
        if a.is_unknown and b.is_unknown:
            # Both are unknown values between 0 < x < MAX_TRANSACTION_COST
            return a
        if a.is_unknown:
            # a is a unknown bounded value and b is int
            # a: 0 < x < MAX_TRANSACTION_COST
            if b.value > MAX_TRANSACTION_COST:
                return a  # a is less than MAX_TRANSACTION_COST
            return b
        if b.is_unknown:
            # b is a unknown bounded value and a is int
            # b: 0 < x < MAX_TRANSACTION_COST
            if a.value > MAX_TRANSACTION_COST:
                return b  # b is less than MAX_TRANSACTION_COST
            return a
        # both are known values
        return a if a.value < b.value else b

    @staticmethod
    def _get_asserted_max_value(
        comparison_ins: "Instruction", compared_value: FeeValue
    ) -> Tuple[FeeValue, FeeValue]:
        """Return maximum possible value that will make the comparison True and maximum
        possible value that will make the comparison False. Both values are upper bounded
        by arg "max_possible_value".

        Args:
            comparison_ins: Comparison operator.
            compared_value: fee value being compared with.
        Returns:
            Tuple[int, int]: Max possible value that will make the comparison instruction return True and
                Max possible value that will make the comparison False.
        """
        # U = max_possible_value  # universal set
        if isinstance(comparison_ins, Eq):
            # x == i => i, U
            return compared_value, FeeValue()
        if isinstance(comparison_ins, Neq):
            # x != i => U, i
            return FeeValue(), compared_value
        if isinstance(comparison_ins, Less):
            # x < i => (i - 1), U
            if compared_value.is_unknown:
                return compared_value, FeeValue()
            return FeeValue(value=max(0, compared_value.value - 1)), FeeValue()
        if isinstance(comparison_ins, LessE):
            # x <= i => i, U
            return compared_value, FeeValue()
        if isinstance(comparison_ins, Greater):
            # x > i => U, i
            return FeeValue(), compared_value
        if isinstance(comparison_ins, GreaterE):
            # x >= i => U, (i - 1)
            if compared_value.is_unknown:
                return FeeValue(), compared_value
            return FeeValue(), FeeValue(value=max(0, compared_value.value - 1))
        return FeeValue(), FeeValue()

    def _get_asserted_fee(  # pylint: disable=too-many-branches
        self, key: str, ins_stack_value: KnownStackValue
    ) -> Tuple[FeeValue, FeeValue]:

        if isinstance(ins_stack_value.instruction, (Eq, Neq, Less, LessE, Greater, GreaterE)):
            arg1 = ins_stack_value.args[0]
            arg2 = ins_stack_value.args[1]
            compared_value: Optional[FeeValue] = None

            if isinstance(arg1, UnknownStackValue) and isinstance(arg2, UnknownStackValue):
                # Both the args are unknown
                # return U, U
                return FeeValue(), FeeValue()

            if isinstance(arg1, UnknownStackValue):
                if not isinstance(arg2, UnknownStackValue) and not self._is_txn_or_gtxn(
                    key, arg2.instruction
                ):
                    # arg1 is unknown and arg2 is not related to "key"
                    return FeeValue(), FeeValue()
                # arg2 is related to key and arg1 is some unknown value
                compared_value = FeeValue(is_unknown=True)
            elif isinstance(arg2, UnknownStackValue):
                if not isinstance(arg1, UnknownStackValue) and not self._is_txn_or_gtxn(
                    key, arg1.instruction
                ):
                    # arg2 is unknown and arg1 is not related to "key"
                    return FeeValue(), FeeValue()
                # arg1 is related to "key" and arg2 is some unknown int value
                compared_value = FeeValue(is_unknown=True)
            elif self._is_txn_or_gtxn(key, arg1.instruction):
                is_int, value = is_int_push_ins(arg2.instruction)
                if is_int and isinstance(value, int):
                    compared_value = FeeValue(value=value)
                else:
                    compared_value = FeeValue(is_unknown=True)

            elif self._is_txn_or_gtxn(key, arg2.instruction):
                is_int, value = is_int_push_ins(arg1.instruction)
                if is_int and isinstance(value, int):
                    compared_value = FeeValue(value=value)
                else:
                    compared_value = FeeValue(is_unknown=True)

            if compared_value is None:
                # compared_value is not int.
                return FeeValue(), FeeValue()

            ins = ins_stack_value.instruction
            return self._get_asserted_max_value(ins, compared_value)
        return FeeValue(), FeeValue()

    def _get_asserted_single(
        self, key: str, ins_stack_value: KnownStackValue
    ) -> Tuple[FeeValue, FeeValue]:
        res = self._get_asserted_fee(key, ins_stack_value)
        return res

    def _store_results(self) -> None:
        for b in self._teal.bbs:
            max_fee = self._block_contexts[FEE_KEY][b]
            assert isinstance(max_fee, FeeValue)
            if max_fee.is_unknown:
                b.transaction_context.max_fee_unknown = True
            else:
                b.transaction_context.max_fee = max_fee.value
            for idx in range(MAX_GROUP_SIZE):
                max_fee = self._block_contexts[self.gtx_key(idx, FEE_KEY)][b]
                assert isinstance(max_fee, FeeValue)
                if max_fee.is_unknown:
                    b.transaction_context.gtxn_context(idx).max_fee_unknown = True
                else:
                    b.transaction_context.gtxn_context(idx).max_fee = max_fee.value
