import html
from pathlib import Path
from typing import List, TYPE_CHECKING, Dict

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
    bb_xlabel = f'"cost = {bb.cost}; {bb.idx}"'
    return f"{bb.idx}[label={table} xlabel={bb_xlabel}]" + graph_edges


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


class ExecutionPaths:  # pylint: disable=too-many-instance-attributes
    """Detector output class to store list of vulnerable paths"""

    def __init__(self, cfg: List["BasicBlock"], description: str, filename: str):
        self._cfg = cfg
        self._description = description
        self._filename = filename
        self._paths: List[List["BasicBlock"]] = []
        self._check: str = ""
        # self._impact: str = ""
        # self._confidence: str = ""
        self._help: str = ""

    def add_path(self, path: List["BasicBlock"]) -> None:
        self._paths.append(path)

    @property
    def paths(self) -> List[List["BasicBlock"]]:
        return self._paths

    @property
    def cfg(self) -> List["BasicBlock"]:
        return self._cfg

    @property
    def description(self) -> str:
        return self._description

    @property
    def check(self) -> str:
        return self._check

    @check.setter
    def check(self, c: str) -> None:
        self._check = c

    # @property
    # def impact(self) -> str:
    #     return self._impact

    # @impact.setter
    # def impact(self, i: str) -> None:
    #     self._impact = i

    # @property
    # def confidence(self) -> str:
    #     return self._confidence

    # @confidence.setter
    # def confidence(self, c: str) -> None:
    #     self._confidence = c

    @property
    def help(self) -> str:
        return self._help

    @help.setter
    def help(self, h: str) -> None:
        self._help = h

    def write_to_files(self, dest: Path, all_paths_in_one: bool = False) -> None:
        # print(f"\ncheck: {self.check}, impact: {self.impact}, confidence: {self.confidence}")
        print(f"\ncheck: {self.check}")
        print(self.description)
        if len(self.paths) == 0:
            print("\tdetector didn't find any vulnerable paths.")
            return

        print("\tfollowing are the vulnerable paths found")
        if not all_paths_in_one:

            for idx, path in enumerate(self._paths, start=1):

                short = " -> ".join(map(str, [bb.idx for bb in path]))
                print(f"\n\t\t path: {short}")

                filename = dest / Path(f"{self._filename}_{idx}.dot")
                print(f"\t\t check file: {filename}")

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(execution_path_to_dot(self.cfg, path))
        else:
            bbs_to_highlight = []

            for path in self._paths:
                short = " -> ".join(map(str, [bb.idx for bb in path]))
                print(f"\t\t path: {short}")
                for bb in path:
                    if bb not in bbs_to_highlight:
                        bbs_to_highlight.append(bb)

            filename = dest / Path(f"{self._filename}.dot")
            print(f"\t\t check file: {filename}")

            with open(filename, "w", encoding="utf-8") as f:
                f.write(execution_path_to_dot(self.cfg, bbs_to_highlight))

    def to_json(self) -> Dict:
        result = {
            "type": "ExecutionPaths",
            "count": len(self.paths),
            "description": self.description,
            "check": self.check,
            # "impact": self.impact,
            # "confidence": self.confidence,
            "help": self.help,
        }
        paths = []
        for path in self.paths:
            short = " -> ".join(map(str, [bb.idx for bb in path]))
            blocks = []
            for bb in path:
                block = []
                for ins in bb.instructions:
                    block.append(f"{ins.line}: {ins}")
                blocks.append(block)

            paths.append({"short": short, "blocks": blocks})

        result["paths"] = paths
        return result


SupportedOutput = ExecutionPaths
