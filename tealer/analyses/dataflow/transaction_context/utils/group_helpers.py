from typing import TYPE_CHECKING, Tuple, Optional
from dataclasses import dataclass

from tealer.teal.instructions.instructions import (
    Txn,  # self, normal field
    Gtxn,  # txn index is part of the instruction, normal field
    # Txna,   # self, array field, array index in the instruction
    # Gtxna,  # txn index is part of the instruction, array field, array index in the instruction
    Gtxns,  # txn index is taken from stack, normal field
    # Gtxnsa, # txn index is taken from stack, normal field, array index in the instruction
    # Txnas,  # self, array field, array index from stack
    # Gtxnas, # txn index is part of the instruction, array field, array index from stack
    # Gtxnsas, # txn index from stack, array field, array index from stack.
    Sub,
    Add,
)
from tealer.utils.comparable_enum import ComparableEnum
from tealer.analyses.utils.stack_ast_builder import KnownStackValue, UnknownStackValue
from tealer.teal.instructions.transaction_field import GroupIndex
from tealer.utils.analyses import is_int_push_ins

if TYPE_CHECKING:
    from tealer.teal.instructions.transaction_field import TransactionField


class IndexType(ComparableEnum):
    Self = 0
    Absolute = 1
    Relative = 2

    Unknown = 777


@dataclass
class TransactionIndex:
    index_type: IndexType
    # value should be ignored for Self and Unknown index types.
    value: int


def get_index_and_field(
    value: KnownStackValue,
) -> Tuple[bool, Optional["TransactionIndex"], Optional["TransactionField"]]:
    """Given a stack value, check if the value pushed is a transaction field. if so, return transaction index and the field.

    Args:
        value: The stack value.

    Returns:
        bool: True if the pushed value is a transaction field else False
        TransactionIndex: Index of the transaction
        TransactionField: The transaction field that will be pushed.
    """
    # TODO: probably could cache
    # our analysis does not concern array fields, so ignoring those instructions for now.
    if not isinstance(value.instruction, (Txn, Gtxn, Gtxns)):
        return False, None, None

    field = value.instruction.field
    if isinstance(value.instruction, Txn):
        return True, TransactionIndex(IndexType.Self, 0), field

    if isinstance(value.instruction, Gtxn):
        return True, TransactionIndex(IndexType.Absolute, value.instruction.idx), field

    # Gtxns instruction
    index_stack_value = value.args[0]
    # happens when the Gtxns instruction is the first instruction of the block.
    if isinstance(index_stack_value, UnknownStackValue):
        return True, TransactionIndex(IndexType.Unknown, 0), field

    index = _get_index(index_stack_value)
    return True, index, field


def _get_index(index_stack_value: KnownStackValue) -> "TransactionIndex":
    # index patterns
    # Txn.group_index() -> Self
    # Int(n) -> Absolute index
    # Txn.group_index() +/- Int(n) -> Relative / Unknown

    # TODO: if there was some kind of analysis to calculate index implemented, call that function to fetch the index directly.
    # There is no need for such analysis. below patterns cover most of the contracts.
    # Txn.group_index() -> txn GroupIndex
    if isinstance(index_stack_value.instruction, Txn) and isinstance(
        index_stack_value.instruction.field, GroupIndex
    ):
        # Self
        return TransactionIndex(IndexType.Self, 0)

    pushes_int, int_value = is_int_push_ins(index_stack_value.instruction)
    if pushes_int and isinstance(int_value, int):
        # index_stack_value is an integer and the index is known to the tool
        return TransactionIndex(IndexType.Absolute, int_value)

    if pushes_int and not isinstance(int_value, int):
        # pushes an integer but we don't its value. Unknown index.
        return TransactionIndex(IndexType.Unknown, 0)

    # does not push an literal int value.
    # check for relative index patterns.
    # Txn.group_index() - Int(n)
    if isinstance(index_stack_value.instruction, Sub):
        arg1, arg2 = index_stack_value.args[0], index_stack_value.args[1]
        # index value is arg1 - arg2.
        if isinstance(arg1, UnknownStackValue) or isinstance(arg2, UnknownStackValue):
            return TransactionIndex(IndexType.Unknown, 0)
        if not (
            isinstance(arg1.instruction, Txn) and isinstance(arg1.instruction.field, GroupIndex)
        ):
            return TransactionIndex(IndexType.Unknown, 0)

        # first argument is Txn.group_index()
        is_int, int_value = is_int_push_ins(arg2.instruction)
        if is_int and isinstance(int_value, int):
            offset = -int_value  # pylint: disable=invalid-unary-operand-type
            return TransactionIndex(IndexType.Relative, offset)
        return TransactionIndex(IndexType.Unknown, 0)

    # Txn.group_index() + Int(n)
    if isinstance(index_stack_value.instruction, Add):
        arg1, arg2 = index_stack_value.args[0], index_stack_value.args[1]
        # index value is arg1 + arg2.
        if isinstance(arg1, UnknownStackValue) or isinstance(arg2, UnknownStackValue):
            return TransactionIndex(IndexType.Unknown, 0)
        offset_arg = arg2
        if not (
            isinstance(arg1.instruction, Txn) and isinstance(arg1.instruction.field, GroupIndex)
        ):
            if not (
                isinstance(arg2.instruction, Txn) and isinstance(arg2.instruction.field, GroupIndex)
            ):
                return TransactionIndex(IndexType.Unknown, 0)
            # Int(n) + Txn.group_index()
            offset_arg = arg1

        is_int, int_value = is_int_push_ins(offset_arg.instruction)
        if is_int and isinstance(int_value, int):
            offset = int_value
            return TransactionIndex(IndexType.Relative, offset)
        return TransactionIndex(IndexType.Unknown, 0)

    return TransactionIndex(IndexType.Unknown, 0)
