from typing import List

from tealer.teal.instructions.instructions import Instruction


class BasicBlock:
    def __init__(self) -> None:
        self._instructions: List[Instruction] = []
        self._prev: List[BasicBlock] = []
        self._next: List[BasicBlock] = []

    def add_instruction(self, instruction: Instruction) -> None:
        self._instructions.append(instruction)

    @property
    def instructions(self) -> List[Instruction]:
        return self._instructions

    @property
    def entry_instr(self) -> Instruction:
        return self._instructions[0]

    @property
    def exit_instr(self) -> Instruction:
        return self._instructions[-1]

    def add_prev(self, p: "BasicBlock") -> None:
        self._prev.append(p)

    def add_next(self, n: "BasicBlock") -> None:
        self._next.append(n)

    @property
    def prev(self) -> List["BasicBlock"]:
        return self._prev

    @property
    def next(self) -> List["BasicBlock"]:
        return self._next

    def __str__(self) -> str:
        ret = ""
        for ins in self._instructions:
            ret += f"{ins.line}: {ins}\n"
        return ret
