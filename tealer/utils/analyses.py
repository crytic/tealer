from typing import Optional, List, Tuple, Union, TYPE_CHECKING

from tealer.teal.instructions.instructions import (
    PushInt,
    Instruction,
    Int,
    Byte,
    PushBytes,
    IntcInstruction,
    BytecInstruction,
)

from tealer.exceptions import TealerException

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.functions import Function


def is_int_push_ins(ins: Instruction) -> Tuple[bool, Optional[Union[int, str]]]:
    """Return true if :ins: pushes a int literal on to the stack

    Args:
        ins: An instruction.

    Returns:
        Returns "pushes_int" and "value".

        pushes_int is True if the instruction pushes an uint64 value during execution.
        Otherwise, it is False.

        value is always None if pushes_int is False.
        value is None when pushes_int is True but the Tealer cannot compute the pushed value.
        value will be not None if Tealer can compute it.

        value will be a string if it is a named constant. The named constants are converted to
        integers by the assembler. Tealer directly returns the string instead of finding the compiled
        integer.

        value will be an int if the value is an integer in the Teal code.

    Raises:
        TealerException: Raises error if ins.bb or ins.bb.teal are not initialized properly.
    """
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
    """Return true if :ins: pushes a byte literal on to the stack.

    Args:
        ins: An instruction.

    Returns:
        Returns "pushes_byte_value" and "value".

        pushes_byte_value is True if the instruction pushes an uint64 value during execution.
        Otherwise, it is False.

        value is always None if pushes_byte_value is False.
        value is None when pushes_byte_value is True but the Tealer cannot compute the pushed value.
        value will be the string if Tealer can compute it.

    Raises:
        TealerException: Raises error if ins.bb or ins.bb.teal are not initialized properly.
    """
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


def next_blocks_global(function: "Function", block: "BasicBlock") -> List["BasicBlock"]:
    """Return basic blocks next to this block in the global CFG.

    global CFG is the single CFG representing the entire contract with callsub blocks connected
    to the subroutine entry blocks and retsub blocks of the subroutine connected to return point block.

    Args:
        function: The function
        block: A basic block.

    Returns:
        Returns the next basic blocks of :block: in the global CFG. The global CFG is the CFG where
        callsub_blocks are connected to the subroutine entry blocks.
    """
    if block.is_retsub_block:
        return function.return_point_blocks(block.subroutine)
    if block.is_callsub_block:
        return [block.called_subroutine.entry]
    return block.next


def prev_blocks_global(function: "Function", block: "BasicBlock") -> List["BasicBlock"]:
    """Return basic blocks previous to this block in the global CFG.

    global CFG is the single CFG representing the entire contract with callsub blocks connected
    to the subroutine entry blocks and retsub blocks of the subroutine connected to return point block.

    Args:
        function: The function
        block: A basic block.

    Returns:
        Returns the previous basic blocks of :block: in the global CFG. The global CFG is the CFG where
        callsub_blocks are connected to the subroutine entry blocks.
    """
    assert block.teal is not None
    if block == block.subroutine.entry:
        # if the block is the entry of the subroutine, return all blocks calling the subroutine
        if block.subroutine != function.main:
            return function.caller_blocks(block.subroutine)
        # the block is the main entry block of the contract
        return []
    if block.is_sub_return_point:
        # if the block is the return point of the subroutine, return all retsub blocks of the subroutine
        return block.callsub_block.called_subroutine.retsub_blocks
    # if its a normal block return previous blocks in the CFG.
    return block.prev


# TODO: Rename this to is_leaf_block_global
def leaf_block_global(block: "BasicBlock") -> bool:
    """Return True if block is a leaf block in the global CFG.

    global CFG is the single CFG representing the entire contract with callsub blocks connected
    to the subroutine entry blocks and retsub blocks of the subroutine connected to return point block.

    Args:
        block: A basic block.

    Returns:
        Returns True if :block: is a leaf block in the global CFG. otherwise, False.
    """
    # Retsub blocks will not have any next blocks but are not considered as leaf blocks in global CFG.
    # Callsub block will have a next block, which is executed after executing the subroutine. However, when
    # Callsub block is the last block in the source code and the subroutine exits the program using return instruction,
    # Then callsub block will not have a next block but it is not considered a leaf block in global CFG.
    return len(block.next) == 0 and not block.is_retsub_block and not block.is_callsub_block
