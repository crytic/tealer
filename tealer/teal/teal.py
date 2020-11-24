from pathlib import Path
from typing import List, Optional

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions import Instruction


class Teal:
    def __init__(self, instructions: List[Instruction], bbs: List[BasicBlock]):
        self._instructions = instructions
        self._bbs = bbs

    def instructions_to_dot(self, filename: Path):
        dot_output = "digraph g{\n"

        for ins in self._instructions:
            label = str(ins)
            label = label.replace('"', '\\"')  # because of byte "A"
            label = f"{ins.line}: {label}"
            dot_output += f'{id(ins)}[label="{label}", shape=box];\n'
            for next_ins in ins.next:
                dot_output += f"{id(ins)} -> {id(next_ins)};\n"

        dot_output += "}"

        with open(filename, "w") as f:
            f.write(dot_output)

    def bbs_to_dot(self, filename: Path, highlited: Optional[List[BasicBlock]] = None):
        dot_output = "digraph g{\n"

        for bb in self._bbs:
            label = str(bb)
            label = label.replace('"', '\\"')  # because of byte "A"
            if highlited and bb in highlited:
                dot_output += f'{id(bb)}[label="{label}", shape=box,color=red];\n'
            else:
                dot_output += f'{id(bb)}[label="{label}", shape=box];\n'
            for next_bb in bb.next:
                dot_output += f"{id(bb)} -> {id(next_bb)};\n"

        dot_output += "}"

        with open(filename, "w") as f:
            f.write(dot_output)

    @property
    def instructions(self) -> List[Instruction]:
        return self._instructions

    @property
    def bbs(self) -> List[BasicBlock]:
        return self._bbs
