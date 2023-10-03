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

from tealer.teal.instructions.instructions import Instruction, Callsub, Retsub
from tealer.exceptions import TealerException

if TYPE_CHECKING:
    from tealer.teal.teal import Teal
    from tealer.teal.subroutine import Subroutine


class BasicBlock:  # pylint: disable=too-many-instance-attributes,too-many-public-methods
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
        self._tealer_comments: List[str] = []
        self._subroutine: Optional["Subroutine"] = None

    def add_instruction(self, instruction: Instruction) -> None:
        """Append instruction to this basic block.

        Args:
            instruction: intruction to add to the basic block.
        """

        self._instructions.append(instruction)

    @property
    def instructions(self) -> List[Instruction]:
        """List of instructions part of this basic block.

        Returns:
            list of basic block instructions.
        """
        return self._instructions

    @property
    def entry_instr(self) -> Instruction:
        """Entry(first) instruction of this basic block.

        Returns:
            The entry instruction of the basic block.
        """
        return self._instructions[0]

    @property
    def exit_instr(self) -> Instruction:
        """Exit(Last) instruction of this basic block.

        Returns:
            The exit instruction of the basic block.
        """
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
        """List of previous basic blocks to this basic block.

        Returns:
            list of previous instructions that might have been executed before this block.
        """
        return self._prev

    @property
    def next(self) -> List["BasicBlock"]:
        """List of next basic blocks to this basic block.

        Returns:
            list of next basic blocks that might be executed after this block.
        """
        return self._next

    @property
    def idx(self) -> int:
        """Index of this basic block when ordered by line number of entry instruction.

        Returns:
            index of this basic block in list of all basic blocks.
        """
        return self._idx

    @idx.setter
    def idx(self, i: int) -> None:
        self._idx = i

    @property
    def cost(self) -> int:
        """cost of executing all instructions in this basic block

        Returns:
            Returns the OpcodeCost of executing all instructions in the block.
        """
        return sum(ins.cost for ins in self.instructions)

    @property
    def teal(self) -> Optional["Teal"]:
        """Teal instance of the contract this basic block belongs to.

        Returns:
            Returns the contract of this basic block.
        """
        return self._teal

    @teal.setter
    def teal(self, teal_instance: "Teal") -> None:
        self._teal = teal_instance

    @property
    def subroutine(self) -> "Subroutine":
        """Subroutine instrance of the subroutine this basic block belongs to.

        Returns:
            Returns the subroutine this block belongs to.

        Raises:
            TealerException: raises error if subroutine is not set during parsing.
        """
        if self._subroutine is None:
            raise TealerException(f"subroutine of B{self._idx} is not initialized")
        return self._subroutine

    @subroutine.setter
    def subroutine(self, subroutine_instance: "Subroutine") -> None:
        self._subroutine = subroutine_instance

    @property
    def is_callsub_block(self) -> bool:
        """Return True if the block calls a subroutine.

        Returns:
            Returns True if this block has a callsub instruction.
        """
        return isinstance(self.exit_instr, Callsub)

    @property
    def called_subroutine(self) -> "Subroutine":
        """Return the subroutine called by this subroutine.

        Returns:
            Returns the subroutine called by the callsub instruction in this block.

        Raises:
            TealerException: if this block is not a callsub_block.
        """
        if not isinstance(self.exit_instr, Callsub):
            raise TealerException("called subroutine of a non callsub block is accessed")
        return self.exit_instr.called_subroutine

    @property
    def sub_return_point(self) -> Optional["BasicBlock"]:
        """Return the return point block of this block.

        Returns:
            The subroutine return_point block of this(callsub) block.
            Returns None if this callsub block does not have a return point block. This happens when
            callsub instruction is the last instruction in the contract and The called subroutine always exits
            the program.

        Raises:
            TealerException: if this block is not a callsub_block.
        """
        if not self.is_callsub_block:
            raise TealerException("sub_return_point block of a non callsub block is accessed")
        return self.next[0] if self.next else None

    @property
    def is_sub_return_point(self) -> bool:
        """Return True if this block is executed after the subroutine i.e next block of callsub_block

        Returns:
            Returns True if this block is executed a subroutine: The next block of a block with callsub
            instruction. Otherwise, returns False.
        """
        for bi in self.prev:
            if bi.is_callsub_block:
                return True
        return False

    @property
    def callsub_block(self) -> "BasicBlock":
        """Return the callsub_block which calls the subroutine. This block is the return point block.

        Returns:
            Return the callsub_block which calls the subroutine that returns the execution to this
            basic block.

        Raises:
            TealerException: if this block is not a sub_return_point block.
        """
        for bi in self.prev:
            if bi.is_callsub_block:
                return bi
        raise TealerException("callsub_block of a non sub_return_point block is accessed")

    @property
    def is_retsub_block(self) -> bool:
        return isinstance(self.exit_instr, Retsub)

    @property
    def tealer_comments(self) -> List[str]:
        """Additional comments added by tealer for each basic block in the output CFG.

        Returns:
            Returns the additional comments added by tealer for this basic block.
        """
        return self._tealer_comments

    @tealer_comments.setter
    def tealer_comments(self, comments: List[str]) -> None:
        self._tealer_comments = comments

    def __str__(self) -> str:
        ret = ""
        for ins in self._instructions:
            ret += f"{ins.line}: {ins}\n"
        return ret

    def __repr__(self) -> str:
        return f"B{self.idx}"
