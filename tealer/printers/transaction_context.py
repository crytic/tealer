"""Printer to output information about transaction fields in the CFG."""

from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

from tealer.printers.abstract_printer import AbstractPrinter
from tealer.utils.output import CFGDotConfig, full_cfg_to_dot

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock


class PrinterTransactionContext(AbstractPrinter):  # pylint: disable=too-few-public-methods
    """Printer to output information about transaction fields in the CFG.

    Transaction field analysis finds possible values for transaction fields. This printer
    adds this information on top of each of the basic blocks in the output CFG.
    """

    NAME = "transaction-context"
    # TODO: Add TxnType, Sender, RekeyTo, CloseRemainderTo, AssetCloseTo field values
    HELP = "Output possible values of GroupIndices, GroupSize"
    WIKI_URL = "https://github.com/crytic/tealer/wiki/Printer-documentation#transaction-context"

    @staticmethod
    def _repr_num_list(values: List[int]) -> str:
        """Return short string representation of range of integers.

        intergers are space-separated and represented in ascending order.

        Continous sequence of more than 3 integers are represented using short-form(a..b).
        e.g
            5 6 7 8
           => 5..8

            1 2 3 5 6 7 8 9 11 13 14 15 16
           => 1 2 3 5..9 11 13..16
        """
        values = sorted(values)
        sequences: List[List[int]] = [[]]
        for i in values:
            if not sequences[-1]:
                sequences[-1].append(i)
            elif sequences[-1][-1] == (i - 1):
                sequences[-1].append(i)
            else:
                sequences.append([i])
        str_seqs = []
        for seq in sequences:
            if len(seq) >= 4:
                str_seqs.append(f"{seq[0]}..{seq[-1]}")
            else:
                str_seqs.append(" ".join(str(i) for i in seq))
        return " ".join(str_seqs)

    def print(self, dest: Optional["Path"] = None) -> None:
        """
        Args:
            dest (Optional[Path]): destination directory to save output files in. files will be saved in
            the current directory if it is None.
        """

        filename = Path("transaction-context.dot")
        if dest is not None:
            filename = dest / filename

        def get_info(bb: "BasicBlock") -> List[str]:
            group_indices_str = self._repr_num_list(bb.transaction_context.group_indices)
            group_sizes_str = self._repr_num_list(bb.transaction_context.group_sizes)
            return [f"GroupIndex: {group_indices_str}", f"GroupSize: {group_sizes_str}"]

        config = CFGDotConfig()
        config.bb_additional_comments = get_info
        full_cfg_to_dot(self.teal.bbs, config, filename)
        print(f"\nExported CFG with transaction context information to {filename}")
