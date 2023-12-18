"""Util functions to output dot files and detector results.

This modules contains functions, classes which are used to store
and display different types of output formats used by tealer detectors
and printers.

Functions:
    full_cfg_to_dot(teal: "Teal", config: Optional[CFGDotConfig]=None, filename: Optional[Path]=None) -> None:
        Exports dot representation of CFG represented by :bbs: in
        dot format to given filename.

Classes:
    ExecutionPaths: Class to represent results of a detector, stores
        execution paths detected by the detector.

Types:
    SupportedOutput: Union of types used for representing detector results.
        For now, it is an alias for ExecutionPaths.

"""
import abc
import html
import re
import os
from pathlib import Path
from typing import List, TYPE_CHECKING, Dict, Callable, Optional
from dataclasses import dataclass, field

from tealer.teal.instructions.instructions import BZ, BNZ, Callsub, Retsub

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.subroutine import Subroutine
    from tealer.teal.functions import Function
    from tealer.teal.teal import Teal
    from tealer.teal.instructions.instructions import Instruction
    from tealer.detectors.abstract_detector import AbstractDetector
    from tealer.execution_context.transactions import GroupTransaction, Transaction


ROOT_OUTPUT_DIRECTORY = Path(os.getenv("TEALER_ROOT_OUTPUT_DIR", "tealer-export"))


@dataclass
class CFGDotConfig:  # pylint: disable=too-many-instance-attributes
    ins_additional_comments: Callable[["Instruction"], List[str]] = lambda _x: []
    # include additional tealer comments at the top of the block.
    bb_additional_comments: Callable[["BasicBlock"], List[str]] = lambda _x: []
    # don't include edge bi -> bj in dot output?
    ignore_edge: Callable[["BasicBlock", "BasicBlock"], bool] = lambda _bi, _bj: False
    # Apply colors to different types of edges?
    color_edges: bool = True
    jump_branch_color: str = "#36d899"  # "green"
    default_branch_color: str = "#e0182b"  # "red"
    callsub_edge_color: str = "#ff8c00"  # "orange"
    remaining_edges_color: str = "BLACK"
    comments_cell_border_size: int = 2  # size of basic block comments cell
    bb_border_color: Callable[["BasicBlock"], str] = lambda _x: "BLACK"
    custom_background_color: Dict["Instruction", str] = field(default_factory=dict)


def _instruction_to_dot(ins: "Instruction", config: CFGDotConfig) -> str:
    """Return dot representation of Teal instruction.

    string representation of the instruction is represented as
    a table cell(row) in dot.

    Args:
        ins: teal instruction to represent in dot format.
        config: configuration for dot output

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
    ins_str = html.escape(ins.source_code.strip(), quote=True)  # original teal code
    # make callsub and retsub bold and italic
    if isinstance(ins, (Callsub, Retsub)):
        ins_str = f"<B><I>{ins_str}</I></B>"

    # format:
    # <B>
    #   // tealer_comment_1 <BR/>
    #   // tealer_comment_2 <BR/>
    # </B>
    # <BR/>
    tealer_comments = ""
    if ins.tealer_comments + config.ins_additional_comments(ins):
        sanitized_comments = [
            html.escape(comment.strip(), quote=True)
            for comment in ins.tealer_comments + config.ins_additional_comments(ins)
        ]
        tealer_comments = "<BR/>".join(f"// {comment}" for comment in sanitized_comments)
        tealer_comments = f"<B>{tealer_comments}</B><BR/>"  # make them bold

    # format:
    #   // source_comment_1 <BR/>
    #   // source_comment_2 <BR/>
    source_code_comments = ""
    if ins.comments_before_ins:
        sanitized_comments = [
            html.escape(comment.strip(), quote=True) for comment in ins.comments_before_ins
        ]
        source_code_comments = "<BR/>".join(f"{comment}" for comment in sanitized_comments)
        source_code_comments += "<BR/>"

    color = config.custom_background_color.get(ins, "BLACK")

    cell_i = (
        "<TR>"
        f'<TD ALIGN="LEFT" BALIGN="LEFT" COLOR="{color}">'
        f"{tealer_comments}"
        f"{source_code_comments}"
        f"{ins.line}. {ins_str}"
        "</TD>"
        "</TR>\n"
    )
    return cell_i


def _bb_to_dot(bb: "BasicBlock", config: CFGDotConfig) -> str:
    """Return dot representation of basic block.

    Basic Blocks are represented in the form of a tabel in dot.
    Each instruction in the basic block is represented as a row.

    Args:
        bb: basic block to represent in dot format.
        config: configuration for dot output

    Returns:
        string containing the dot representation of the given
        basic block.
    """

    # format: `{source_node}:s -> {dest_node}{dest_port}:n [color=""];`
    def graph_edge_str(src_bb: "BasicBlock", dest_bb: "BasicBlock", edge_color: str) -> str:
        if config.ignore_edge(src_bb, dest_bb):
            return ""
        return f'{src_bb.idx}:s -> {dest_bb.idx}:{dest_bb.entry_instr.line}:n [color="{edge_color}"];\n'

    # format:
    #     <TR> tealer_comments and additional_comments </TR>
    #     <TR> instruction_1                           </TR>
    #     <TR> instruction_2                           </TR>
    #     ...
    table_rows: List[str] = []

    santized_comments = [
        html.escape(comment.strip(), quote=True)
        for comment in bb.tealer_comments + config.bb_additional_comments(bb)
    ]
    comments_cell_str = (
        "<TR>"
        f'<TD COLOR="BLACK" ALIGN="LEFT" BALIGN="LEFT" PORT="{bb.entry_instr.line}" BORDER="{config.comments_cell_border_size}">'
        "<B>"
        f'{"<BR/>".join(f"// {comment}" for comment in santized_comments)}'
        "</B>"
        "</TD>"
        "</TR>\n"
    )

    table_rows.append(comments_cell_str)

    for ins in bb.instructions:
        table_rows.append(_instruction_to_dot(ins, config))

    graph_edges: List[str] = []
    if config.color_edges and isinstance(bb.exit_instr, (BZ, BNZ)):
        if isinstance(bb.exit_instr, (BZ, BNZ)):
            # color graph edges if exit instruction is BZ or BNZ.
            if len(bb.next) == 1:
                # happens when bz/bnz is the last instruction in the contract and there is no default branch
                default_branch = None
                jump_branch = bb.next[0]
            else:
                default_branch = bb.next[0]
                jump_branch = bb.next[1]

            if default_branch is not None:
                graph_edges.append(graph_edge_str(bb, default_branch, config.default_branch_color))
            graph_edges.append(graph_edge_str(bb, jump_branch, config.jump_branch_color))
    else:
        for next_bb in bb.next:
            graph_edges.append(graph_edge_str(bb, next_bb, config.remaining_edges_color))

    table_str = (
        f'<<TABLE ALIGN="LEFT" COLOR="{config.bb_border_color(bb)}">\n'
        f'{"".join(table_rows)}'
        "</TABLE>> labelloc=top shape=plain\n"
    )

    return f'{bb.idx}[label={table_str}] {"".join(graph_edges)}'


def subroutine_to_dot(subroutine: "Subroutine", config: Optional[CFGDotConfig] = None) -> str:
    if config is None:
        config = CFGDotConfig()
    # ignore edges from callsub to the return point block because we place an empty node to represent
    # the called subroutine in between the callsub block and the return point.
    # replacing the ignore_edge function directly should be ok (?) for now
    config.ignore_edge = lambda bi, _: isinstance(bi.exit_instr, (Callsub))

    def empty_subroutine_box(callsub_block: "BasicBlock") -> str:
        # Include a empty box between callsub and it's return point. Empty box represents
        # the subroutine called by `callsub`.
        called_subroutine = callsub_block.called_subroutine
        return_point_block = callsub_block.sub_return_point
        if return_point_block is None:
            # happens when callsub is the last instruction in the CFG and subroutine always exits the program.
            return_point_block_idx = "none"
        else:
            return_point_block_idx = str(return_point_block.idx)
        content = (
            f'"Subroutine {called_subroutine.name}"'  # TODO: add other information in the future
        )
        node_name = f"x{callsub_block.idx}_{return_point_block_idx}"
        edge1 = f"{callsub_block.idx}:s -> {node_name}:n;\n"  # callsub to empty box
        edge2 = ""
        if return_point_block is not None:
            # edge from empty box to return point block
            edge2 = f"{node_name}:s -> {return_point_block.idx}:{return_point_block.entry_instr.line}:n;\n"

        return f"{node_name}[label={content},style=dashed,shape=box,fontname=bold] {edge1}{edge2}"

    nodes_dot: List[str] = []
    for bi in subroutine.blocks:
        nodes_dot.append(_bb_to_dot(bi, config))
        if bi.is_callsub_block:
            # add empty box to represent the graph of called subroutine
            # add edge from callsub to that box and box to callsub return point.
            # ignoring recursion here. adds empty box even if callsub calls the same subroutine.
            nodes_dot.append(empty_subroutine_box(bi))

    nodes_str = "\n".join(nodes_dot)

    dot_output = "digraph g{\n ranksep = 1 \n overlap = scale \n" f"{nodes_str}\n" "}"  # .......

    return dot_output


def all_subroutines_to_dot(
    teal: "Teal",
    dest: Path,
    config: Optional[CFGDotConfig] = None,
    filename_prefix: str = "",
) -> None:
    """Export CFG of each subroutine to a dot file.

    Args:
        teal: contract instance
        dest: destination directory to save the dot files.
        config: CFGDotConfig to use for generating the dot files. if None, function uses
            default settings.
        filename_prefix: prefix to add before each filename to distinguish files generated
            by multiple calls to this function.
    """
    if filename_prefix:  # not empty string
        filename_prefix = f"{filename_prefix}_"
    main_entry_sub_filename = f"{filename_prefix}contract_shortened_cfg.dot"

    with open(dest / Path(main_entry_sub_filename), "w", encoding="utf-8") as f:
        f.write(subroutine_to_dot(teal.main, config))
        print(f"Exported contract's shortened cfg to: {dest / Path(main_entry_sub_filename)}")

    for sub_name, subroutine in teal.subroutines.items():
        filename = f"{filename_prefix}subroutine_{sub_name}_cfg.dot"
        with open(dest / Path(filename), "w", encoding="utf-8") as f:
            f.write(subroutine_to_dot(subroutine, config))
            print(f'Exported cfg of "{sub_name}" subroutine to: {dest / Path(filename)}')


def full_cfg_to_dot(  # pylint: disable=too-many-locals
    teal: "Teal", config: Optional[CFGDotConfig] = None, filename: Optional[Path] = None
) -> Optional[str]:
    """Export control flow graph to a dot file.

    The control flow graph is represented as a digraph in dot.
    basic blocks are represented as a table with it's instructions
    as rows.

    Args:
        teal: The contract.
        config: optional configuration for dot output.
        filename: name of the file to save the dot representation
            of control flow graph in.

    Returns:
        Returns dot representation of the CFG if filename is not given. If filename is given,
        writes the dot representation to the file.
    """

    bbs = teal.bbs
    subroutine_block_idx = set(bb.idx for bb in teal.bbs if bb in teal.main.blocks)
    # responsible for "box" around each subroutine.
    subroutine_clusters: List[str] = []
    for i, (subroutine_name, subroutine) in enumerate(teal.subroutines.items()):
        subroutine_bbs = subroutine.blocks
        cluster_name = i
        cluster_nodes = " ".join(str(bb.idx) for bb in subroutine_bbs)
        # TODO: Add number of args and return values to label in the future.
        subgraph_dot = f"""
            subgraph cluster_{cluster_name} {{
                label = "Subroutine {subroutine_name}";
                graph[style=dashed];
                {cluster_nodes};
            }}
        """
        subroutine_clusters.append(subgraph_dot)

    # format: `{source_node}:s -> {dest_node}{dest_port}:n [color=""];`
    def graph_edge_str(src_bb: "BasicBlock", dest_bb: "BasicBlock", edge_color: str) -> str:
        return f'{src_bb.idx}:s -> {dest_bb.idx}:{dest_bb.entry_instr.line}:n [color="{edge_color}"];\n'

    # default config
    if not config:
        config = CFGDotConfig()
        # border color for subroutine blocks
        subroutine_blocks_border_color = "#000066"
        config.bb_border_color = (
            lambda bb: "BLACK"
            if bb.idx not in subroutine_block_idx
            else subroutine_blocks_border_color
        )

    # ignore callsub block to return point edges. Add edges from callsub blocks to subroutine entry and retsubs to return points
    config.ignore_edge = lambda bi, _: isinstance(bi.exit_instr, (Callsub))

    bb_nodes_dot: List[str] = []
    for bb in bbs:
        bb_nodes_dot.append(_bb_to_dot(bb, config))
        if bb.is_callsub_block:
            # add edge from callsub block to subroutine entry
            bb_nodes_dot.append(
                graph_edge_str(bb, bb.called_subroutine.entry, config.callsub_edge_color)
            )
            # add edge from retsub blocks to return point
            return_point_block = bb.sub_return_point
            if return_point_block is None:
                continue
            for src_bb in bb.called_subroutine.retsub_blocks:
                bb_nodes_dot.append(
                    graph_edge_str(src_bb, return_point_block, config.remaining_edges_color)
                )

    subroutine_clusters_str = "\n".join(subroutine_clusters)
    bb_nodes_str = "\n".join(bb_nodes_dot)

    dot_output = (
        "digraph g{\n ranksep = 1 \n overlap = scale \n"
        f"{subroutine_clusters_str}\n"
        f"{bb_nodes_str}\n"
        "}"
    )

    if filename is None:
        return dot_output

    with open(filename, "w", encoding="utf-8") as f:
        f.write(dot_output)
    return None


def detector_terminal_description(detector: "AbstractDetector") -> str:
    """Return description for the detector that is printed to terminal before listing vulnerable paths.

    Args:
        detector: A detector object.

    Returns:
        Returns description for the :detector: that can be printed on the terminal or used as general description
        for the detector.
    """
    return (
        f'\nCheck: "{detector.NAME}", Impact: {detector.IMPACT}, Confidence: {detector.CONFIDENCE}\n'
        f"Description: {detector.DESCRIPTION}\n\n"
        f"Wiki: {detector.WIKI_URL}\n"
    )


def detector_ouptut_dir(destination: Path, detector: "AbstractDetector") -> Path:
    return destination / Path(detector.NAME)


class Output(abc.ABC):
    @property
    @abc.abstractmethod
    def detector(self) -> "AbstractDetector":
        pass

    @abc.abstractmethod
    def filter_paths(self, filter_regex: str) -> None:
        pass

    @abc.abstractmethod
    def to_json(self) -> Dict:
        pass

    @abc.abstractmethod
    def generate_output(self, dest: Path) -> bool:
        """
        Generate the output


        Args:
            dest: The files will be saved in the given :dest: destination directory.

        Returns:
            Returns true if something was generated - False if there is nothing to be written
        """

        return False  # this statement is needed for darglint


class InstructionsOutput(Output):
    def __init__(
        self, teal: "Teal", detector: "AbstractDetector", instructions: List[List["Instruction"]]
    ):
        self._teal = teal
        self._detector = detector
        self.instructions: List[List["Instruction"]] = instructions

    @property
    def detector(self) -> "AbstractDetector":
        return self._detector

    def filter_paths(self, filter_regex: str) -> None:
        pass

    def to_json(self) -> Dict:
        result = {
            "type": "InstructionsOutput",
            "count": len(self.instructions),
            "description": detector_terminal_description(self.detector),
            "check": self.detector.NAME,
            "impact": str(self.detector.IMPACT),
            "confidence": str(self.detector.CONFIDENCE),
            "help": self.detector.WIKI_RECOMMENDATION.strip(),
            "paths": [str(ins) for ins in self.instructions],
        }
        return result

    def generate_output(self, dest: Path) -> bool:
        """
        Generate the output


        Args:
            dest: Not use (no files are generated for InstructionsOutput)

        Returns:
            Returns true if something was generated - False if there is nothing to be written
        """

        if not self.instructions:
            return False

        print(detector_terminal_description(self.detector))
        print("\tFollowing are the unoptimized instructions found:")

        for ins in self.instructions:
            print(ins)

        return True


class ExecutionPaths(Output):
    """Detector output class to represent vulnerable execution paths."""

    def __init__(self, teal: "Teal", detector: "AbstractDetector", paths: List[List["BasicBlock"]]):
        self._teal = teal
        self._detector = detector
        self.paths: List[List["BasicBlock"]] = paths

    @property
    def detector(self) -> "AbstractDetector":
        return self._detector

    def _filename(self, path_index: int) -> Path:
        return Path(f"{self.detector.NAME}-{path_index}.dot")

    @staticmethod
    def _short_notation(path_bbs: List["BasicBlock"]) -> str:
        """Return short notation representation of path

        Args:
            path_bbs: List of basic blocks in the path from the contract's entry.

        Returns:
            Returns short notation representation of the path.
            if path has [B0, B2, B3, B5] then short notation is "0 -> 2 -> 3 -> 5"
        """
        # TODO: Change notation from "0 -> 2 -> 3 -> 5" to "B0 -> B2 -> B3 -> B5"
        return " -> ".join(map(str, [bb.idx for bb in path_bbs]))

    def filter_paths(self, filter_regex: str) -> None:
        if filter_regex == "":
            return
        filtered_paths: List[List["BasicBlock"]] = []
        for path in self.paths:
            if re.search(filter_regex, self._short_notation(path)) is None:
                # short notation does not contain string matching the regex
                filtered_paths.append(path)
        self.paths = filtered_paths
        return

    def generate_output(self, dest: Path) -> bool:
        """Export execution paths to dot files.

        The execution paths are highlighted in the dot representation
        of CFG. Each execution path is indexed based on the order they
        are added to the result and index will be used in the filename.

        Args:
            dest: The dot files will be saved in the given :dest: destination
                directory.

        Returns:
            Returns true if something was written - False if there is nothing to be written
        """

        if not self.paths:
            return False

        print(detector_terminal_description(self.detector))

        # cfg_to_dot config
        config = CFGDotConfig()
        config.color_edges = False
        print("\tFollowing are the vulnerable paths found:")

        dest = detector_ouptut_dir(dest, self.detector)
        # create output directory if not present
        os.makedirs(dest, exist_ok=True)

        for idx, path in enumerate(self.paths, start=1):
            short = self._short_notation(path)
            print(f"\n\t\t path: {short}")

            filename = dest / self._filename(idx)
            print(f"\t\t check file: {filename}")

            config.bb_border_color = (
                lambda bb: "BLACK"
                if bb not in path  # pylint: disable=cell-var-from-loop
                else "RED"
            )
            full_cfg_to_dot(self._teal, config, filename)
        print("-" * 100)

        return True

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
            "description": detector_terminal_description(self.detector),
            "check": self.detector.NAME,
            "impact": str(self.detector.IMPACT),
            "confidence": str(self.detector.CONFIDENCE),
            "help": self.detector.WIKI_RECOMMENDATION.strip(),
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


class GroupTransactionOutput(Output):
    def __init__(
        self,
        detector: "AbstractDetector",
        group: "GroupTransaction",
        transactions: Dict["Transaction", List["Function"]],
    ) -> None:
        self._detector = detector
        self._group = group
        self._transactions = transactions

    @property
    def detector(self) -> "AbstractDetector":
        return self._detector

    @property
    def group_transaction(self) -> "GroupTransaction":
        return self._group

    @property
    def transactions(self) -> Dict["Transaction", List["Function"]]:
        return self._transactions

    def filter_paths(self, filter_regex: str) -> None:
        pass

    def to_json(self) -> Dict:
        transactions = {}
        for txn in self._transactions:
            contracts = []
            for function in self._transactions[txn]:
                contracts.append(
                    {
                        "contract": function.contract.contract_name,
                        "function": function.function_name,
                    }
                )
            transactions[txn.transacton_id] = contracts

        result = {
            "type": "GroupTransactionOutput",
            "description": detector_terminal_description(self.detector),
            "check": self.detector.NAME,
            "impact": str(self.detector.IMPACT),
            "confidence": str(self.detector.CONFIDENCE),
            "help": self.detector.WIKI_RECOMMENDATION.strip(),
            "operation": self._group.operation_name,
            "transactions": transactions,
        }
        return result

    def generate_output(self, dest: Path) -> bool:
        """
        Generate the output

        Args:
            dest: Not used, no files are generated for GroupTransactionOutput

        Returns:
            Returns true if something was generated - False if there is nothing to be written.
        """
        print(detector_terminal_description(self.detector))
        print(
            f"\tFollowing transactions of the operation {self._group.operation_name} are vulnerable:\n"
        )

        for txn in self._transactions:
            print(f"\tTransaction {txn.transacton_id}")
            if self._transactions[txn]:
                # contract was given by the user.
                for function in self._transactions[txn]:
                    print(f"\t\tContract: {function.contract.contract_name}")
                    print(f"\t\tFunction: {function.function_name}")
                    print("\n")

        return True


ListOutput = List[Output]
