from typing import Optional, Type as TypingType, List, Tuple, Union

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.global_field import ZeroAddress
from tealer.teal.instructions.instructions import (
    PushInt,
    Txn,
    Global,
    Instruction,
    Addr,
    Int,
    Eq,
    Neq,
    Return,
    BZ,
    BNZ,
    Assert,
    Byte,
    PushBytes,
    IntcInstruction,
    BytecInstruction,
)
from tealer.teal.instructions.transaction_field import TransactionField, OnCompletion, ApplicationID

from tealer.exceptions import TealerException


def is_int_push_ins(ins: Instruction) -> Tuple[bool, Optional[Union[int, str]]]:
    """Return true if :ins: pushes a int literal on to the stack"""
    if isinstance(ins, Int) or isinstance(  # pylint: disable=consider-merging-isinstance
        ins, PushInt
    ):
        return True, ins.value
    if isinstance(ins, IntcInstruction):
        if not ins.bb or not ins.bb.teal:
            # TODO: move the check to respective class property
            raise TealerException("Block or teal property is not set")
        teal = ins.bb.teal
        is_known, value = teal.get_int_constant(ins.index)
        if is_known:
            return True, value
        return True, None
    return False, None


def is_byte_push_ins(ins: Instruction) -> Tuple[bool, Optional[str]]:
    """Return true if :ins: pushes a byte literal on to the stack."""
    if isinstance(ins, (Byte, PushBytes)):
        return True, ins.value
    if isinstance(ins, BytecInstruction):
        if not ins.bb or not ins.bb.teal:
            # TODO: move the check to respective class property
            raise TealerException("Block or teal property is not set")
        teal = ins.bb.teal
        is_known, value = teal.get_byte_constant(ins.index)
        if is_known:
            return True, value
        return True, None
    return False, None


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
                is_int_push, value = is_int_push_ins(prev)
                if is_int_push and value == 0:
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
    # Adds integer values along with names for Named Integer Constants of txn OnCompletion
    ENUM_NAMES_TO_INT = {
        "NoOp": 0,
        "OptIn": 1,
        "CloseOut": 2,
        "ClearState": 3,
        "UpdateApplication": 4,
        "DeleteApplication": 5,
    }
    integer_checked_values: List[int] = []
    for named_constant in checked_values:
        if named_constant in ENUM_NAMES_TO_INT:
            integer_checked_values.append(ENUM_NAMES_TO_INT[named_constant])

    if isinstance(ins1, Txn) and isinstance(ins1.field, OnCompletion):
        is_int_push, value = is_int_push_ins(ins2)
        return is_int_push and (value in checked_values or value in integer_checked_values)
    return False


def is_application_creation_check(ins1: Instruction, ins2: Instruction) -> bool:
    """Check if the instructions form application creation check.

    ApplicationID will be 0 at the time of creation as a result the condition
    txn ApplicationID == int 0 is generally used to do intialization operations
    at the time of application creation. Updating or Deleting application isn't
    possible if the transaction is a application creation check. Using this check
    allows the UpdateApplication, DeleteApplication detector to not explore(pruning)
    paths where this check is true.

    Args:
        ins1: First instruction of the execution sequence that is supposed
            to form a comparison check for application creation.
        ins2: Second instruction in the execution sequence, will be executed
            right after :ins1:.

    Returns:
        True if the given instructions :ins1:, :ins2: form a application creation
        check i.e True if :ins1: is txn ApplicationID and :ins2: is
        int 0.
    """

    if isinstance(ins1, Txn) and isinstance(ins1.field, ApplicationID):
        is_int_push, value = is_int_push_ins(ins2)
        return is_int_push and value == 0
    return False


def detect_missing_on_completion(  # pylint: disable=too-many-branches, too-many-locals
    bb: BasicBlock,
    current_path: List[BasicBlock],
    paths_without_check: List[List[BasicBlock]],
    on_completion_check_to_have: str,
    on_completion_checks_to_follow: List[str],
) -> None:
    """Find execution paths with missing on completion check.

    This function recursively explores the Control Flow Graph(CFG) of the
    contract and reports execution paths with missing on completion
    check. All paths must have some forms of

    txn OnCompletion
    int [on_completion_check_to_have]

    If there are txn OnCompletion, where the associated int is from

    This function is "in place", modifies arguments with the data it is on_completion_checks_to_follow,
    We follow only one branch (based on the BZ/BNZ)

    Args:
        bb: Current basic block being checked(whose execution is simulated.)
        current_path: Current execution path being explored.
        paths_without_check:
            Execution paths with missing UpdateApplication check. This is a
            "in place" argument. Vulnerable paths found by this function are
            appended to this list.
        on_completion_check_to_have: completion check to have
        on_completion_checks_to_follow: completion checks to follow
    """

    # check for loops
    if bb in current_path:
        return

    current_path = current_path + [bb]

    # prev_was_oncompletion = False
    # prev_was_int = False
    prev_was_equal = False
    prev_was_txn_application_id = False
    skip_false = False
    skip_true = False
    stack: List[Instruction] = []

    for ins in bb.instructions:

        if isinstance(ins, Return):
            if len(ins.prev) == 1:
                prev = ins.prev[0]
                is_int_push, value = is_int_push_ins(prev)
                if is_int_push and value == 0:
                    return

            paths_without_check.append(current_path)
            return

        # return if a mutually exclusive condition is asserted
        # i.e txn OnCompletion is asserted against one of the other possible value or
        # if application creation check is asserted
        if isinstance(ins, Assert) and prev_was_equal:
            return

        skip_false = isinstance(ins, BNZ) and prev_was_equal
        skip_true = isinstance(ins, BZ) and prev_was_equal
        prev_was_equal = False

        # detect the following pattern of application creation check and prune branches
        # where the application creation check is true
        # txn ApplicationID
        # [bz | bnz] LABEL
        skip_false = skip_false or (isinstance(ins, BZ) and prev_was_txn_application_id)
        skip_true = skip_true or (isinstance(ins, BNZ) and prev_was_txn_application_id)
        prev_was_txn_application_id = False

        if isinstance(ins, Txn) and isinstance(ins.field, ApplicationID):
            prev_was_txn_application_id = True

        if isinstance(ins, Eq) and len(stack) >= 2:
            one = stack[-1]
            two = stack[-2]
            if is_oncompletion_check(
                one, two, [on_completion_check_to_have]
            ) or is_oncompletion_check(two, one, [on_completion_check_to_have]):
                return
            # TODO: evaluate if we really need to following, or just consider
            # Any check where on_completion_check_to_have is not present
            if is_oncompletion_check(
                one, two, on_completion_checks_to_follow
            ) or is_oncompletion_check(two, one, on_completion_checks_to_follow):
                prev_was_equal = True
            if is_application_creation_check(one, two) or is_application_creation_check(two, one):
                prev_was_equal = True

        stack.append(ins)

    if skip_false:
        detect_missing_on_completion(
            bb.next[0],
            current_path,
            paths_without_check,
            on_completion_check_to_have,
            on_completion_checks_to_follow,
        )
        return
    if skip_true:
        detect_missing_on_completion(
            bb.next[1],
            current_path,
            paths_without_check,
            on_completion_check_to_have,
            on_completion_checks_to_follow,
        )
        return
    for next_bb in bb.next:
        detect_missing_on_completion(
            next_bb,
            current_path,
            paths_without_check,
            on_completion_check_to_have,
            on_completion_checks_to_follow,
        )


def next_blocks_global(block: "BasicBlock") -> List["BasicBlock"]:
    """Return basic blocks next to this block in the global CFG.

    global CFG is the single CFG representing the entire contract with callsub blocks connected
    to the subroutine entry blocks and retsub blocks of the subroutine connected to return point block.
    """
    if block.is_retsub_block_NEW:
        return block.subroutine_NEW.return_point_blocks
    if block.is_callsub_block_NEW:
        return [block.called_subroutine_NEW.entry]
    return block.next


def prev_blocks_global(block: "BasicBlock") -> List["BasicBlock"]:
    """Return basic blocks previous to this block in the global CFG.

    global CFG is the single CFG representing the entire contract with callsub blocks connected
    to the subroutine entry blocks and retsub blocks of the subroutine connected to return point block.
    """
    assert block.teal is not None
    if block == block.subroutine_NEW.entry:
        # if the block is the entry of the subroutine, return all blocks calling the subroutine
        if block.subroutine_NEW != block.teal._main_NEW:
            return block.subroutine_NEW.caller_blocks
        # the block is the main entry block of the contract
        return []
    if block.is_sub_return_point_NEW:
        # if the block is the return point of the subroutine, return all retsub blocks of the subroutine
        return block.callsub_block_NEW.called_subroutine_NEW.retsub_blocks
    # if its a normal block return previous blocks in the CFG.
    return block.prev


def leaf_block_global(block: "BasicBlock") -> bool:
    """Return True if block is a leaf block in the global CFG.

    global CFG is the single CFG representing the entire contract with callsub blocks connected
    to the subroutine entry blocks and retsub blocks of the subroutine connected to return point block.
    """
    # Retsub blocks will not have any next blocks but are not considered as leaf blocks in global CFG.
    # Callsub block will have a next block, which is executed after executing the subroutine. However, when
    # Callsub block is the last block in the source code and the subroutine exits the program using return instruction,
    # Then callsub block will not have a next block but it is not considered a leaf block in global CFG.
    return len(block.next) == 0 and not block.is_retsub_block_NEW and not block.is_callsub_block_NEW
