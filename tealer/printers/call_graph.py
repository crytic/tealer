"""Printer for exporting call-graph of the contract."""

import html
import os
from pathlib import Path
from typing import Dict, Set

from tealer.printers.abstract_printer import AbstractPrinter
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

    def _construct_call_graph(self) -> Dict[str, Set[str]]:
        """construct call graph for the contract.

        entry point is treated as a separate subroutine/function `__main__`.
        For each subroutine, label(subroutine name) represents the node and each callsub
        instruction in the subroutine corresponds to directed edge to the target subroutine.

        Returns:
            Dict[str, Set[str]]: dictionary representing the graph. The graph has edges from each
            subroutine in d[key] to key. The source node of the edge are values and destination node is the key.
            if d["S1"] = ["S2", "S3"] then graph has edges "S3 -> S1", "S2 -> S1".
        """

        graph: Dict[str, Set[str]] = {}
        for _, subroutine in self.teal.subroutines.items():
            graph[subroutine.name] = set(
                map(lambda bi: bi.subroutine.name, subroutine.caller_blocks)
            )

        # no need to handle __main__ subroutine cause it is program entry point and there won't be caller blocks.
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
        for destination_sub, source_subs in graph.items():
            destination_sub = html.escape(destination_sub, quote=True)
            dot_output += f"{destination_sub}[label={destination_sub}];\n"
            for source_sub in source_subs:
                source_sub = html.escape(source_sub, quote=True)
                graph_edges += f"{source_sub} -> {destination_sub};\n"
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
