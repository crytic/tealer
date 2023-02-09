"""Printer for exporting call-graph of the contract."""

import html
from pathlib import Path
from typing import List, Dict, Optional

from tealer.printers.abstract_printer import AbstractPrinter
from tealer.teal.instructions.instructions import Callsub, Label


class PrinterCallGraph(AbstractPrinter):  # pylint: disable=too-few-public-methods
    """Printer to export call-graph of the contract.

    This printer is supposed to work for contracts written in teal version 4 or greater.
    Call graph dot file will be saved as `call-graph.dot` in destination folder if given
    or else in the current directory. The entry point of the contract is
    treated as another function("__entry__") while constructing the call graph.

    """

    NAME = "call-graph"
    HELP = "Export the call graph of contract to a dot file"
    WIKI_URL = "https://github.com/crytic/tealer/wiki/Printer-documentation#call-graph"

    def _construct_call_graph(self) -> Dict[str, List[str]]:
        """construct call graph for the contract.

        entry point is treated as a separate function `__entry__`.
        For each subroutine, label(subroutine name) represents the node and each callsub
        instruction in the subroutine corresponds to directed edge from subroutine the
        callsub instruction is part of to subroutine corresponding to the callsub label.

        Returns:
            Dict[str, List[str]]: dictionary representing the graph. each `key` is a node and
            `value` is a list representing the edges. Each str in value list corresponds to end
            node for a directed edge from `key` node.
        """

        graph = {}
        for sub in self.teal.subroutines:
            # graph node
            if isinstance(sub[0].entry_instr, Label):
                sub_name = sub[0].entry_instr.label
            else:
                # should be unreachable
                sub_name = str(sub[0].entry_instr)

            # graph edges
            edges = []
            for bb in sub:
                for ins in bb.instructions:
                    if isinstance(ins, Callsub):
                        edges.append(ins.label)

            graph[sub_name] = edges

        # treat entry point of the contract as a separate function
        subroutine_blocks = [bb for sub in self.teal.subroutines for bb in sub]
        entry_function_blocks = [bb for bb in self.teal.bbs if bb not in subroutine_blocks]

        # use __entry__ as function name for entry point
        graph["__entry__"] = []
        for bb in entry_function_blocks:
            for ins in bb.instructions:
                if isinstance(ins, Callsub):
                    graph["__entry__"].append(ins.label)

        return graph

    def print(self, dest: Optional["Path"] = None) -> None:
        """Export call graph of the contract in dot format.

        Each node in the call graph corresponds to a subroutine and edge representing call from
        source subroutine to called subroutine. Entry point of the contract is treated as another
        function and represented with label `__entry__`. Call graph will be saved as `call-graph.dot`
        in the destination directory if given or else in the current directory.
        Subroutines are supported from teal version 4. so, for contracts written in lesser version, this
        function only prints the error message stating the same.

        Args:
            dest (Optional[Path]): destination directory to save output files in. files will be saved in
            the current directory if it is None.
        """

        if self.teal.version < 4:
            print("subroutines are not supported in teal version 3 or less")
            return

        dot_output = "digraph g{\n"
        graph = self._construct_call_graph()

        # construct dot representation of the graph
        graph_edges = ""
        for sub_name, targets in graph.items():
            sub_name = html.escape(sub_name, quote=True)
            dot_output += f"{sub_name}[label={sub_name}];\n"
            for target_sub in targets:
                target_sub = html.escape(target_sub, quote=True)
                graph_edges += f"{sub_name} -> {target_sub};\n"
        dot_output += graph_edges
        dot_output += "}\n"

        filename = Path("call-graph.dot")
        if dest is not None:
            filename = dest / filename

        print(f"\nExported call graph to {filename}")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(dot_output)
