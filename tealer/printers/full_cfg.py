"""Printer for exporting full contract CFG in dot format.

Classes:
    PrinterCFG: Printer to export contract CFG.
"""

from pathlib import Path

from typing import Optional

from tealer.printers.abstract_printer import AbstractPrinter
from tealer.utils.output import cfg_to_dot


class PrinterCFG(AbstractPrinter):  # pylint: disable=too-few-public-methods
    """Printer to export contract CFG in dot."""

    NAME = "cfg"
    HELP = "Export the CFG of entire contract"
    WIKI_URL = "https://github.com/crytic/tealer/wiki/Printer-documentation#cfg"

    def print(self, dest: Optional[Path] = None) -> None:
        """Export the CFG of entire contract.

        Args:
            dest (Optional[Path]): destination directory to save the dot file in.
        """
        if dest is None:
            dest = Path(".")

        filename = Path("full_cfg.dot")
        print(f"\nCFG exported to file: {filename}")
        cfg_to_dot(self.teal.bbs, filename=dest / filename)
