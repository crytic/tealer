from pathlib import Path
from typing import List, Optional
import html

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Instruction


class Teal:
    def __init__(self, instructions: List[Instruction], bbs: List[BasicBlock]):
        self._instructions = instructions
        self._bbs = bbs

    @staticmethod
    def render_instruction(i: Instruction) -> str:
        ins_str = html.escape(str(i), quote=True)
        comment_str = "no comment for this line" if i.comment == "" else i.comment
        comment_str = html.escape(comment_str, quote=True)
        # the 'href' attribute is set to bogus because graphviz wants it in SVG
        tooltip = f'TOOLTIP="{comment_str}" HREF="bogus"'
        cell_i = f'<TD {tooltip} ALIGN="LEFT" PORT="{i.line}">{i.line}. {ins_str}</TD>'
        return f"<TR>{cell_i}</TR>\n"

    @staticmethod
    def render_bb(idx: int, bb: BasicBlock) -> str:
        table_prefix = '<<TABLE ALIGN="LEFT">\n'
        table_suffix = "</TABLE>> labelloc=top shape=plain\n"
        table_rows = ""
        graph_edges = ""
        for i in bb.instructions:
            table_rows += Teal.render_instruction(i)
        for next_bb in bb.next:
            exit_loc = bb.exit_instr.line
            entry_loc = next_bb.entry_instr.line
            graph_edges += f"{id(bb)}:{exit_loc}:s -> {id(next_bb)}:{entry_loc}:n;\n"
        table = table_prefix + table_rows + table_suffix
        return f"{id(bb)}[label={table} xlabel={idx}]" + graph_edges

    def render_cfg(self, filename: Path) -> None:
        dot_output = "digraph g{\n ranksep = 1 \n overlap = scale \n"

        for idx, bb in enumerate(self._bbs):
            dot_output += Teal.render_bb(idx, bb)

        dot_output += "}"

        with open(filename, "w") as f:
            f.write(dot_output)

    def instructions_to_dot(self, filename: Path) -> None:
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

    def bbs_to_dot(self, filename: Path, highlited: Optional[List[BasicBlock]] = None) -> None:
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
