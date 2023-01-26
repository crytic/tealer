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

from tealer.teal.instructions.instructions import BZ, BNZ, Callsub, Retsub

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.instructions.instructions import Instruction


def _instruction_to_dot(ins: "Instruction", set_port: bool = True) -> str:
    """Return dot representation of Teal instruction.

    string representation of the instruction is represented as
    a table cell(row) in dot.

    Args:
        ins: teal instruction to represent in dot format.

    Returns:
        string containing the dot representation of the given
        instruction.

    ---------------
    // tealer comments
    //
    // source code comments
    // ...
    // instruction
    ---------------
    """

    # ins.source_code stores the indentation and whitespace. strip them
    ins_str = html.escape(ins.source_code.strip(), quote=True)
    # make callsub and retsub bold and italic
    if isinstance(ins, (Callsub, Retsub)):
        ins_str = f"<B><I>{ins_str}</I></B>"
    tealer_comments = ""
    if ins.tealer_comments:
        tealer_comments = "<BR/>".join(
            f"// {html.escape(comment.strip(), quote=True)}" for comment in ins.tealer_comments
        )
        tealer_comments = f"<B>{tealer_comments}</B><BR/>"  # make them bold
    source_code_comments = ""
    if ins.comments_before_ins:
        source_code_comments = "<BR/>".join(
            f"{html.escape(comment.strip(), quote=True)}" for comment in ins.comments_before_ins
        )
        source_code_comments += "<BR/>"
    port = ""
    if set_port:
        # port is used as a link destination.
        port = f'PORT="{ins.line}"'
    cell_i_contents = f"{tealer_comments}{source_code_comments}{ins.line}. {ins_str}"
    cell_i = f'<TD ALIGN="LEFT" BALIGN="LEFT" {port} COLOR="BLACK">{cell_i_contents}</TD>'
    return f"<TR>{cell_i}</TR>\n"


def _bb_to_dot(  # pylint: disable=too-many-locals
    bb: "BasicBlock", border_color: str = "BLACK", color_edges: bool = True
) -> str:
    """Return dot representation of basic block.

    Basic Blocks are represented in the form of a tabel in dot.
    Each instruction in the basic block is represented as a row.

    Args:
        bb: basic block to represent in dot format.

    Returns:
        string containing the dot representation of the given
        basic block.
    """

    table_prefix = f'<<TABLE ALIGN="LEFT" COLOR="{border_color}">\n'
    table_suffix = "</TABLE>> labelloc=top shape=plain\n"
    comments_cell = ""
    table_rows = ""
    graph_edges = ""

    if bb.tealer_comments:
        # Increase the border size to differentiate the comments cell/row.
        comments_cell_border_size = 2
        tealer_comments = "<BR/>".join(
            f"// {html.escape(comment.strip(), quote=True)}" for comment in bb.tealer_comments
        )
        tealer_comments = f"<B>{tealer_comments}</B><BR/>"  # make them bold
        comments_cell = f'<TR><TD COLOR="BLACK" ALIGN="LEFT" BALIGN="LEFT" PORT="{bb.entry_instr.line}" BORDER="{comments_cell_border_size}">{tealer_comments}</TD></TR>\n'

        table_rows += comments_cell
        # if there's a comments_cell then don't add port(link) to the first instruction cell.
        table_rows += _instruction_to_dot(bb.entry_instr, set_port=False)
    else:
        table_rows += _instruction_to_dot(bb.entry_instr)

    for ins in bb.instructions[1:]:
        table_rows += _instruction_to_dot(ins)

    jump_branch_color = ""
    default_branch_color = ""
    callsub_edge_color = ""
    remaining_edges_color = ""
    if color_edges:
        jump_branch_color = "#36d899"  # "green"
        default_branch_color = "#e0182b"  # "red"
        callsub_edge_color = "#ff8c00"  # "orange"
        # remaining_edges_color = ""  # "#1155ff"

    if isinstance(bb.exit_instr, (BZ, BNZ)):
        # color graph edges if exit instruction is BZ or BNZ.
        if len(bb.next) == 1:
            # happens when bz/bnz is the last instruction in the contract and there is no default branch
            default_branch = None
            jump_branch = bb.next[0]
        else:
            default_branch = bb.next[0]
            jump_branch = bb.next[1]

        exit_loc = bb.exit_instr.line
        if default_branch is not None:
            default_entry_loc = default_branch.entry_instr.line
            graph_edges += f'{bb.idx}:{exit_loc}:s -> {default_branch.idx}:{default_entry_loc}:n [color="{default_branch_color}"];\n'

        jump_entry_loc = jump_branch.entry_instr.line
        graph_edges += f'{bb.idx}:{exit_loc}:s -> {jump_branch.idx}:{jump_entry_loc}:n [color="{jump_branch_color}"];\n'
    elif isinstance(bb.exit_instr, Callsub):
        # make callsub instruction -> subroutine edge orange.
        callsub_branch = bb.next[0]
        exit_loc = bb.exit_instr.line
        subroutine_loc = callsub_branch.entry_instr.line
        graph_edges += f'{bb.idx}:{exit_loc}:s -> {callsub_branch.idx}:{subroutine_loc}:n [color="{callsub_edge_color}"];\n'
    else:
        for next_bb in bb.next:
            exit_loc = bb.exit_instr.line
            entry_loc = next_bb.entry_instr.line
            graph_edges += f'{bb.idx}:{exit_loc}:s -> {next_bb.idx}:{entry_loc}:n [color="{remaining_edges_color}"];\n'
    table = table_prefix + table_rows + table_suffix
    return f"{bb.idx}[label={table}]" + graph_edges


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
    teal = bbs[0].teal
    assert teal is not None
    subroutine_block_idx = set(
        bb.idx for subroutine_bbs in teal.subroutines for bb in subroutine_bbs
    )
    subroutine_blocks_border_color = "#ff6600"
    for bb in bbs:
        # TODO: have different color for each subroutine. Yellow for subroutine 1, orange for 2,...??
        if bb.idx in subroutine_block_idx:
            dot_output += _bb_to_dot(bb, subroutine_blocks_border_color)
        else:
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

    dot_output = "digraph g{\n ranksep = 1 \n overlap = scale \n"

    for bb in cfg:
        if bb in path:
            dot_output += _bb_to_dot(bb, border_color="RED", color_edges=False)
        else:
            dot_output += _bb_to_dot(bb, color_edges=False)

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
