from typing import Type as TypingType, List

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.global_field import ZeroAddress
from tealer.teal.instructions.instructions import (
    Txn,
    Global,
    Instruction,
    Addr,
    Int,
    Eq,
    Neq,
    Return,
)
from tealer.teal.instructions.transaction_field import TransactionField, OnCompletion


def check_if_txn_field_against_address(
    ins1: Instruction, ins2: Instruction, tx_field: TypingType[TransactionField]
) -> bool:
    """Check if the (ins1, ins2) is on the form
    TXN [tx_field]
    GLOBAL ZeroAddress | Addr

    Args:
        ins1: first instruction.
        ins2: second instruction,,
        tx_field: Type of transaction field that is checked against

    Returns:
        True if (ins1,ins2) is (TXN tx_field, Global ZeroAddress | Addr).
    """
    if isinstance(ins1, Txn) and isinstance(ins1.field, tx_field):
        if isinstance(ins2, Global) and isinstance(ins2.field, ZeroAddress):
            return True
        if isinstance(ins2, Addr):
            return True
    return False


def check_txn_field_address_equality(
    ins: Instruction, stack: List[Instruction], tx_field: TypingType[TransactionField]
) -> bool:
    """Check if the (ins1), [ins2, ins3] is on the form
    TXN [tx_field]
    GLOBAL ZeroAddress | Addr
    EQ|NEQ

    or
    GLOBAL ZeroAddress | Addr
    TXN [tx_field]
    EQ|NEQ

    Args:
        ins1: first instruction.
        stack: list of additional instruction,
        tx_field: Type of transaction field that is checked against

    Returns:
        True if (ins1), [ins2, ins3] follows the pattern.
        False if stack does not have +two elements, or if the pattern is not followed
    """
    if isinstance(ins, (Eq, Neq)) and len(stack) >= 2:
        one = stack[-1]
        two = stack[-2]
        if check_if_txn_field_against_address(
            one, two, tx_field
        ) or check_if_txn_field_against_address(two, one, tx_field):
            return True
    return False


def detect_missing_txn_check(
    tx_field: TypingType[TransactionField],
    bb: BasicBlock,
    current_path: List[BasicBlock],
    paths_without_check: List[List[BasicBlock]],
) -> None:
    """Find execution paths with missing txn check. The check is on the form

    TXN [tx_field]
    GLOBAL ZeroAddress | Addr
    EQ|NEQ

    or
    GLOBAL ZeroAddress | Addr
    TXN [tx_field]
    EQ|NEQ

    The function starts from bb, and iterate until analyzing all the paths.
    The results are saved in paths_without_check

    Args:
        bb: Current basic block being checked(whose execution is simulated.)
        current_path: Basic block already explored.
        paths_without_check:
            This is a
            "in place" argument. Vulnerable paths found by this function are
            appended to this list.
    """

    # check for loops
    if bb in current_path:
        return

    current_path = current_path + [bb]

    stack: List["Instruction"] = []

    for ins in bb.instructions:
        if isinstance(ins, Return):
            if len(ins.prev) == 1:
                prev = ins.prev[0]
                if isinstance(prev, Int) and prev.value == 0:
                    return

            paths_without_check.append(current_path)
            return

        if check_txn_field_address_equality(ins, stack, tx_field):
            return

        stack.append(ins)

    for next_bb in bb.next:
        detect_missing_txn_check(tx_field, next_bb, current_path, paths_without_check)


def is_oncompletion_check(ins1: Instruction, ins2: Instruction, checked_values: List[str]) -> bool:
    """Check if the instructions form OnCompletion check with value in the checked values.

    OnCompletion transaction field stores the type of the application transaction
    that invoked the contract execution.

    Args:
        ins1: First instruction of the execution sequence that is supposed
            to form this comparison check .
        ins2: Second instruction in the execution sequence, will be executed
            right after :ins1:.
        checked_values: List of values accepted on the on completion check

    Returns:
        True if the given instructions :ins1:, :ins2: form a OnCompletion check
        using the checked values. True if :ins1: is txn OnCompletion and
        :ins2: is int (checked_values).
    """

    if isinstance(ins1, Txn) and isinstance(ins1.field, OnCompletion):
        return isinstance(ins2, Int) and ins2.value in checked_values
    return False
