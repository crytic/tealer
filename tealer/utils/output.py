import html
from pathlib import Path
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.instructions.instructions import Instruction


def _instruction_to_dot(ins: "Instruction") -> str:
    ins_str = html.escape(str(ins), quote=True)
    comment_str = "no comment for this line" if ins.comment == "" else ins.comment
    comment_str = html.escape(comment_str, quote=True)
    # the 'href' attribute is set to bogus because graphviz wants it in SVG
    tooltip = f'TOOLTIP="{comment_str}" HREF="bogus"'
    cell_i = f'<TD {tooltip} ALIGN="LEFT" PORT="{ins.line}">{ins.line}. {ins_str}</TD>'
    return f"<TR>{cell_i}</TR>\n"


def _bb_to_dot(bb: "BasicBlock") -> str:
    table_prefix = '<<TABLE ALIGN="LEFT">\n'
    table_suffix = "</TABLE>> labelloc=top shape=plain\n"
    table_rows = ""
    graph_edges = ""
    for ins in bb.instructions:
        table_rows += _instruction_to_dot(ins)
    for next_bb in bb.next:
        exit_loc = bb.exit_instr.line
        entry_loc = next_bb.entry_instr.line
        graph_edges += f"{bb.idx}:{exit_loc}:s -> {next_bb.idx}:{entry_loc}:n;\n"
    table = table_prefix + table_rows + table_suffix
    return f"{bb.idx}[label={table} xlabel={bb.idx}]" + graph_edges


def cfg_to_dot(bbs: List["BasicBlock"], filename: Path) -> None:
    dot_output = "digraph g{\n ranksep = 1 \n overlap = scale \n"

    for bb in bbs:
        dot_output += _bb_to_dot(bb)

    dot_output += "}"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(dot_output)


def execution_path_to_dot(cfg: List["BasicBlock"], path: List["BasicBlock"]) -> str:
    dot_output = "digraph g{\n"

    for bb in cfg:
        label = str(bb)
        label = html.escape(label, quote=True)
        if bb in path:
            dot_output += f'{bb.idx}[label="{label}", shape=box, color=red];\n'
        else:
            dot_output += f'{bb.idx}[label="{label}", shape=box];\n'

        for next_bb in bb.next:
            dot_output += f"{bb.idx} -> {next_bb.idx};\n"

    dot_output += "}"

    return dot_output
