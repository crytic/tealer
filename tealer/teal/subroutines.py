from typing import Set

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import (
    Err,
    Return,
    Retsub,
)


class Subroutine:
    def __init__(self, entry_block: BasicBlock) -> None:
        self._blocks: Set[BasicBlock] = set()
        self._entry_block: BasicBlock = entry_block
        self._exit_blocks: Set[BasicBlock] = set()
        self._add_block(entry_block)

    def _add_block(self, block: BasicBlock) -> None:
        if(block in self._blocks):
            return
        
        self._blocks.add(block)
        if isinstance(block.exit_instr, (Return, Retsub, Err)):
            self._exit_blocks.add(block)
            return
        
        for successor in block.next:
            self._add_block(successor)

    @property
    def blocks(self) -> Set[BasicBlock]:
        return self._blocks

    @property
    def exit_blocks(self) -> Set[BasicBlock]:
        return self._exit_blocks

    @property
    def entry_block(self) -> BasicBlock:
        return self._entry_block
