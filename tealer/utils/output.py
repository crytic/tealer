"""Util functions to output dot files and detector results.

This modules contains functions, classes which are used to store
and display different types of output formats used by tealer detectors
and printers.

Functions:
    cfg_to_dot(bbs: List[BasicBlock], filename: Path) -> None:
        Exports dot representation of CFG represented by :bbs: in
        dot format to given filename.

    execution_path_to_dot(cfg: List[BasicBlock], path: List[BasicBlock]) -> str:
        Returns dot representation of the given control flow graph :cfg:
        with basic blocks present in :path: highlighted.

Classes:
    ExecutionPaths: Class to represent results of a detector, stores
        execution paths detected by the detector.

Types:
    SupportedOutput: Union of types used for representing detector results.
        For now, it is an alias for ExecutionPaths.

"""

import html
from pathlib import Path
from typing import List, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.instructions.instructions import Instruction


def _instruction_to_dot(ins: "Instruction") -> str:
    """Return dot representation of Teal instruction.

    string representation of the instruction is represented as
    a table cell(row) in dot.

    Args:
        ins: teal instruction to represent in dot format.

    Returns:
        string containing the dot representation of the given
        instruction.
    """

    ins_str = html.escape(str(ins), quote=True)
    comment_str = "no comment for this line" if ins.comment == "" else ins.comment
    comment_str = html.escape(comment_str, quote=True)
    # the 'href' attribute is set to bogus because graphviz wants it in SVG
    tooltip = f'TOOLTIP="{comment_str}" HREF="bogus"'
    cell_i = f'<TD {tooltip} ALIGN="LEFT" PORT="{ins.line}">{ins.line}. {ins_str}</TD>'
    return f"<TR>{cell_i}</TR>\n"


def _bb_to_dot(bb: "BasicBlock") -> str:
    """Return dot representation of basic block.

    Basic Blocks are represented in the form of a tabel in dot.
    Each instruction in the basic block is represented as a row.

    Args:
        bb: basic block to represent in dot format.

    Returns:
        string containing the dot representation of the given
        basic block.
    """

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
    """Export control flow graph to a dot file.

    The control flow graph is represented as a digraph in dot.
    basic blocks are represented as a table with it's instructions
    as rows.

    Args:
        bbs: list of basic blocks representing the control
            flow graph.
        filename: name of the file to save the dot representation
            of control flow graph in.
    """

    dot_output = "digraph g{\n ranksep = 1 \n overlap = scale \n"

    for bb in bbs:
        dot_output += _bb_to_dot(bb)

    dot_output += "}"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(dot_output)


def execution_path_to_dot(cfg: List["BasicBlock"], path: List["BasicBlock"]) -> str:
    """Return CFG with a execution path highlighted in dot format.

    The CFG is represented as a digraph in dot. nodes are basic blocks
    of the CFG. The execution path, which is a sequence of basic blocks
    are highlighted using a color in the dot representation.

    Args:
        cfg: Control Flow Graph of the contract.
        path: An execution path to highlight in the given CFG.

    Returns:
        string containg the dot representation of CFG where nodes
        corresponding to the given execution path are highlighted
        using red color.
    """

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
    """Detector output class to store list of execution paths.

    Args:
        cfg: Control Flow Graph of the teal contract.
        description: Description of the execution path detected by
            the detector.
        filename: The dot representation of execution paths will be
            saved in the filenames starting with :filename: prefix.
    """

    def __init__(self, cfg: List["BasicBlock"], description: str, filename: str):
        self._cfg = cfg
        self._description = description
        self._filename = filename
        self._paths: List[List["BasicBlock"]] = []
        self._check: str = ""
        self._impact: str = ""
        self._confidence: str = ""
        self._help: str = ""

    def add_path(self, path: List["BasicBlock"]) -> None:
        """Add given execution path to current list of execution paths.

        Args:
            path: new execution path detected by the detector which
                will be added to the list of execution paths.
        """

        self._paths.append(path)

    @property
    def paths(self) -> List[List["BasicBlock"]]:
        """List of execution paths stored in the result."""
        return self._paths

    @property
    def cfg(self) -> List["BasicBlock"]:
        """Control Flow of the teal contract."""
        return self._cfg

    @property
    def description(self) -> str:
        """Description of execution paths stored in this result"""
        return self._description

    @property
    def check(self) -> str:
        """Name of the detector whose result is being represented."""
        return self._check

    @check.setter
    def check(self, c: str) -> None:
        self._check = c

    @property
    def impact(self) -> str:
        """Impact of the detector whose result is being represented."""
        return self._impact

    @impact.setter
    def impact(self, i: str) -> None:
        self._impact = i

    @property
    def confidence(self) -> str:
        """Confidence of the detector whose result is being represented."""
        return self._confidence

    @confidence.setter
    def confidence(self, c: str) -> None:
        self._confidence = c

    @property
    def help(self) -> str:
        """Help message to remove detected issues from the contract."""
        return self._help

    @help.setter
    def help(self, h: str) -> None:
        self._help = h

    def write_to_files(self, dest: Path, all_paths_in_one: bool = False) -> None:
        """Export execution paths to dot files.

        The execution paths are highlighted in the dot representation
        of CFG. Each execution path is indexed based on the order they
        are added to the result and index will be used in the filename.

        Args:
            dest: The dot files will be saved in the given :dest: destination
                directory.
            all_paths_in_one: if this is set to True, all the execution
                paths will be highlighted in a single file. if this is
                False, each execution path is saved in a different file.
                Default False.
        """

        print(f"\ncheck: {self.check}, impact: {self.impact}, confidence: {self.confidence}")
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
        """Return json representation of detector result.

        The execution paths are represented as a list of basic blocks,
        which themselves are list of string representation of it's
        instructions.

        Returns:
            JSON encodable dictionary representing the detector result.
        """

        result = {
            "type": "ExecutionPaths",
            "count": len(self.paths),
            "description": self.description,
            "check": self.check,
            "impact": self.impact,
            "confidence": self.confidence,
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
