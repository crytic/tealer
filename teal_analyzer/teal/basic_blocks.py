from typing import List

from teal_analyzer.teal.instructions import Instruction


class BasicBlock:
    def __init__(self):
        self._instructions: List[Instruction] = []
        self._prev: List[BasicBlock] = []
        self._next: List[BasicBlock] = []

    def add_instruction(self, instruction: Instruction):
        self._instructions.append(instruction)

    @property
    def instructions(self) -> List[Instruction]:
        return self._instructions

    def add_prev(self, p):
        self._prev.append(p)

    def add_next(self, n):
        self._next.append(n)

    @property
    def prev(self) -> List["BasicBlock"]:
        return self._prev

    @property
    def next(self) -> List["BasicBlock"]:
        return self._next

    def __str__(self):
        ret = ""
        for ins in self._instructions:
            ret += f"{ins.line}: {ins}\n"
        return ret
