"""Printer for exporting call-graph of the contract."""

import html
import os
from pathlib import Path
from typing import List, Dict

from tealer.printers.abstract_printer import AbstractPrinter
from tealer.teal.instructions.instructions import Callsub
from tealer.utils.output import ROOT_OUTPUT_DIRECTORY


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

        entry point is treated as a separate subroutine/function `__entry__`.
        For each subroutine, label(subroutine name) represents the node and each callsub
        instruction in the subroutine corresponds to directed edge to the target subroutine.

        Returns:
            Dict[str, List[str]]: dictionary representing the graph. each `key` is a node and
            `value` is a list representing the edges. Each str in value list corresponds to end
            node for a directed edge from `key` node.
        """

        graph: Dict[str, List[str]] = {}
        for sub_name, sub in self.teal.subroutines.items():
            # graph edges
            edges = []
            for bb in sub.blocks:
                for ins in bb.instructions:
                    if isinstance(ins, Callsub):
                        edges.append(ins.label)

            graph[sub_name] = edges

        # treat entry point of the contract as a separate function
        entry_function_blocks = self.teal.main.blocks
        # use __entry__ as function name for entry point
        entry_function_name = "__entry__"
        graph[entry_function_name] = []
        for bb in entry_function_blocks:
            for ins in bb.instructions:
                if isinstance(ins, Callsub):
                    graph[entry_function_name].append(ins.label)

        return graph

    def print(self) -> None:
        """Export call graph of the contract in dot format.

        Each node in the call graph corresponds to a subroutine and edge representing call from
        source subroutine to called subroutine. Entry point of the contract is treated as another
        function and represented with label `__entry__`. Call graph will be saved as `call-graph.dot`
        in the destination directory if given or else in the current directory.
        Subroutines are supported from teal version 4. so, for contracts written in lesser version, this
        function only prints the error message stating the same."""

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

        # outputs a single file: set the dir to {ROOT_DIRECTORY}/{CONTRACT_NAME}
        dest = ROOT_OUTPUT_DIRECTORY / Path(self.teal.contract_name)
        os.makedirs(dest, exist_ok=True)

        filename = Path("call-graph.dot")
        filename = dest / filename

        print(f"\nExported call graph to {filename}")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(dot_output)
