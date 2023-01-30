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

import html
from pathlib import Path
from typing import Optional, List, TYPE_CHECKING

from tealer.printers.abstract_printer import AbstractPrinter
from tealer.teal.instructions.instructions import Callsub

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock


class PrinterFunctionCFG(AbstractPrinter):  # pylint: disable=too-few-public-methods
    """Printer to export CFGs of subroutines in dot.

    This printer is supposed to work for contracts written in teal version 4 or greater.
    Dot files will be saved as `function_{subroutine_name}_cfg.dot` in destination folder
    if given or else in the current directory.

    """

    NAME = "function-cfg"
    HELP = "Export cfgs of each subroutine defined in the contract."

    @staticmethod
    def _subroutine_to_dot(subroutine: List["BasicBlock"]) -> str:
        """Return dot representation of directed graph representing the cfg of given subroutine.

        Subroutine CFG doesn't show an edge between callsub basic block to called subroutine basic block
        unlike the contract CFG. Instead, an edge between callsub and it's return point is shown.

        Args:
            subroutine (List["BasicBlock"]): list of all basic blocks part of the given subroutine.

        Returns:
            (str): dot representation of the subroutine cfg.
        """

        dot_output = "digraph g{\n"

        for bb in subroutine:
            label = str(bb)
            label = html.escape(label, quote=True)
            dot_output += f'{bb.idx}[label="{label}", shape=box];\n'

            for next_bb in bb.next:
                if next_bb in subroutine:
                    dot_output += f"{bb.idx} -> {next_bb.idx};\n"

            # callsub instructions are not connected to their return points in cfg.
            # but a output cfg needs a edge between callsub and it's return point.
            if isinstance(bb.exit_instr, Callsub):
                if bb.exit_instr.return_point:
                    return_point_bb = bb.exit_instr.return_point.bb
                    if return_point_bb:
                        dot_output += f"{bb.idx} -> {return_point_bb.idx};\n"

        dot_output += "}"

        return dot_output

    def print(self, dest: Optional[Path] = None) -> None:
        """Export CFG of each subroutine defined in the contract.

        As subroutines are supported from teal version 4, for contracts with version 3 or less,
        only an error message is printed. And for version 4 or larger, dot representation of each
        subroutine cfg is written to file `function_{subroutine_name}_cfg.dot`.

        Args:
            dest (Optional[Path]): files will be saved in the `dest` folder if it's not None. if
            it is, then dot files will be saved in the current directory.
        """

        if self.teal.version < 4:
            print("subroutines are not supported in teal version 3 or less.")
            return

        print()
        for sub_name, sub in self.teal.subroutines.items():
            dot_output = self._subroutine_to_dot(sub.blocks)

            filename = Path(f"function_{sub_name}_cfg.dot")
            if dest is not None:
                filename = dest / filename

            print(f"Exported {sub_name} function cfg to {filename}")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(dot_output)
