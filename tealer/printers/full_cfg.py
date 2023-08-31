"""Printer for exporting full contract CFG in dot format.

Classes:
    PrinterCFG: Printer to export contract CFG.
"""

import os
from pathlib import Path

from tealer.printers.abstract_printer import AbstractPrinter
from tealer.utils.output import full_cfg_to_dot, ROOT_OUTPUT_DIRECTORY


class PrinterCFG(AbstractPrinter):  # pylint: disable=too-few-public-methods
    """Printer to export contract CFG in dot."""

    NAME = "cfg"
    HELP = "Export the CFG of entire contract"
    WIKI_URL = "https://github.com/crytic/tealer/wiki/Printer-documentation#cfg"

    def print(self) -> None:
        """Export the CFG of entire contract."""
        # outputs a single file: set the dir to {ROOT_DIRECTORY}/{CONTRACT_NAME}
        dest = ROOT_OUTPUT_DIRECTORY / Path(self.teal.contract_name)
        os.makedirs(dest, exist_ok=True)

        filename = dest / Path("full_cfg.dot")

        print(f"\nCFG exported to file: {filename}")
        full_cfg_to_dot(self.teal, filename=filename)
