"""Defines class to represent basic blocks of teal contract.

Tealer works on Control Flow Graph(CFG) of the contract for
analysis. CFG is represented as a list of basic blocks in tealer.
This module defines the BasicBlock class for representing basic blocks,
parts of contract code that have only single entry and exit point of
execution. BasicBlock class contains methods, properties used to store,
retrieve previous and next basic blocks. This previous and next basic blocks
of a basic block represent edges coming into and coming out of it
i.e they represents edges in the Control Flow Graph(CFG).

Classes:
    BasicBlock: Class to represent basic blocks of teal contract.
"""

from typing import List, Optional, TYPE_CHECKING

from tealer.teal.instructions.instructions import Instruction
from tealer.teal.context.block_transaction_context import BlockTransactionContext


if TYPE_CHECKING:
    from tealer.teal.teal import Teal


class BasicBlock:  # pylint: disable=too-many-instance-attributes
    """Class to represent basic blocks of the teal contract.

    A basic block is a sequence of instructions with a single entry
    and single exit point. The instructions in a basic block always execute
    in the same sequence from the entry point to the exit point if at all
    executed. This class is used to store instructions that belong to
    a single BasicBlock in teal contracts.
    """

    def __init__(self) -> None:
        self._instructions: List[Instruction] = []
        self._prev: List[BasicBlock] = []
        self._next: List[BasicBlock] = []
        self._idx: int = 0
        self._teal: Optional["Teal"] = None
        self._transaction_context = BlockTransactionContext()
        self._callsub_block: Optional[BasicBlock] = None
        self._sub_return_point: Optional[BasicBlock] = None

    def add_instruction(self, instruction: Instruction) -> None:
        """Append instruction to this basic block.

        Args:
            instruction: intruction to add to the basic block.
        """

        self._instructions.append(instruction)

    @property
    def instructions(self) -> List[Instruction]:
        """List of instructions part of this basic block."""
        return self._instructions

    @property
    def entry_instr(self) -> Instruction:
        """Entry(first) instruction of this basic block."""
        return self._instructions[0]

    @property
    def exit_instr(self) -> Instruction:
        """Exit(Last) instruction of this basic block."""
        return self._instructions[-1]

    def add_prev(self, prev_bb: "BasicBlock") -> None:
        """Add basic block that may execute just before this basic block.

        Executing a basic block means that the execution is passed to
        the entry instruction of the basic block. Previous basic blocks are
        basic blocks whose exit instruction might execute before the entry
        instruction of this basic block i.e exit instruction of previous
        basic block is previous instruction of entry instruction of this
        basic block.

        Args:
            prev_bb: basic block to add to the list of previous
                basic blocks of this basic block.
        """

        self._prev.append(prev_bb)

    def add_next(self, next_bb: "BasicBlock") -> None:
        """Add basic block that may execute right after this instruction.

        A basic block is considered as next basic block if the execution may be
        passed from this basic block to that basic block. All the basic blocks
        whose entry instruction is next instruction of exit instruction of this
        basic block are next basic blocks.

        Args:
            next_bb: basic block to add to the list of next basic blocks
                of this basic block.
        """

        self._next.append(next_bb)

    @property
    def prev(self) -> List["BasicBlock"]:
        """List of previous basic blocks to this basic block."""
        return self._prev

    @property
    def next(self) -> List["BasicBlock"]:
        """List of next basic blocks to this basic block."""
        return self._next

    @property
    def idx(self) -> int:
        """Index of this basic block when ordered by line number of entry instruction."""
        return self._idx

    @idx.setter
    def idx(self, i: int) -> None:
        self._idx = i

    @property
    def callsub_block(self) -> Optional["BasicBlock"]:
        """If this block is the return point of a subroutine, `callsub_block` is the block
        that called the subroutine.
        """
        return self._callsub_block

    @callsub_block.setter
    def callsub_block(self, b: "BasicBlock") -> None:
        self._callsub_block = b

    @property
    def sub_return_point(self) -> Optional["BasicBlock"]:
        """If a subroutine is executed after this block i.e exit instruction is callsub.
        then, sub_return_point will be basic block that will be executed after the subroutine.
        """
        return self._sub_return_point

    @sub_return_point.setter
    def sub_return_point(self, b: "BasicBlock") -> None:
        self._sub_return_point = b

    @property
    def cost(self) -> int:
        """cost of executing all instructions in this basic block"""
        return sum(ins.cost for ins in self.instructions)

    @property
    def teal(self) -> Optional["Teal"]:
        """Teal instance of the contract this basic block belongs to."""
        return self._teal

    @teal.setter
    def teal(self, teal_instance: "Teal") -> None:
        self._teal = teal_instance

    @property
    def transaction_context(self) -> "BlockTransactionContext":
        return self._transaction_context

    def __str__(self) -> str:
        ret = ""
        for ins in self._instructions:
            ret += f"{ins.line}: {ins}\n"
        return ret

    def __repr__(self) -> str:
        return f"B{self.idx}"
