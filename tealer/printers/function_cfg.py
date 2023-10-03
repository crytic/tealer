"""Printer for exporting subroutines in dot format.

Control Flow Graph of each subroutine defined in the contract
is exported in dot format. As the subroutines are only
supported from teal version 4, for contracts written in version
3 or less, printer doesn't do anything. Each subroutine is saved
in a new dot file with filename ``function_{subroutine_name}_cfg.dot``
in the destination directly which will be current directory if not
specified.

Classes:
    PrinterFunctionCFG: Printer to export CFGs of subroutines defined
        in the contract. The CFGs will be saved in dot format.
"""

import os
from pathlib import Path

from tealer.printers.abstract_printer import AbstractPrinter
from tealer.utils.output import all_subroutines_to_dot, ROOT_OUTPUT_DIRECTORY


class PrinterFunctionCFG(AbstractPrinter):  # pylint: disable=too-few-public-methods
    """Printer to export CFGs of subroutines in dot.

    This printer is supposed to work for contracts written in teal version 4 or greater.
    Dot files will be saved as `function_{subroutine_name}_cfg.dot` in destination folder
    if given or else in the current directory.

    """

    NAME = "subroutine-cfg"
    HELP = "Export the CFG of each subroutine"
    WIKI_URL = "https://github.com/crytic/tealer/wiki/Printer-documentation#subroutine-cfg"

    def print(self) -> None:
        """Export CFG of each subroutine defined in the contract."""
        # outputs multiple files: set the dir to {ROOT_DIRECTORY}/{CONTRACT_NAME}/{"print-"PRINTER_NAME}
        dest = ROOT_OUTPUT_DIRECTORY / Path(self.teal.contract_name) / Path(f"print-{self.NAME}")
        os.makedirs(dest, exist_ok=True)

        all_subroutines_to_dot(self.teal, dest)
