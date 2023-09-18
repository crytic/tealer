"""Printer to output information about transaction fields in the CFG."""

import os
from pathlib import Path
from typing import List, TYPE_CHECKING

from tealer.printers.abstract_printer import AbstractPrinter
from tealer.utils.output import (
    CFGDotConfig,
    full_cfg_to_dot,
    all_subroutines_to_dot,
    ROOT_OUTPUT_DIRECTORY,
)

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

        Args:
            values: Sorted list of integers. smaller value is first.

        Returns:
            Returns short string representation of the :values:
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

    def print(self) -> None:
        filename = Path("transaction-context.dot")

        # outputs multiple files: set the dir to {ROOT_DIRECTORY}/{CONTRACT_NAME}/{"print-"PRINTER_NAME}
        dest = ROOT_OUTPUT_DIRECTORY / Path(self.teal.contract_name) / Path(f"print-{self.NAME}")
        os.makedirs(dest, exist_ok=True)

        filename = dest / filename
        function = list(self.teal.functions.values())[0]

        def get_info(bb: "BasicBlock") -> List[str]:
            # NOTE: use the first function for now as `init_tealer_from_single_contract` uses entire contract as single function.
            group_indices_str = self._repr_num_list(function.transaction_context(bb).group_indices)
            group_sizes_str = self._repr_num_list(function.transaction_context(bb).group_sizes)
            return [f"GroupIndex: {group_indices_str}", f"GroupSize: {group_sizes_str}"]

        config = CFGDotConfig()
        config.bb_additional_comments = get_info
        # generate a Full CFG with all group-size, group-index comments
        full_cfg_to_dot(self.teal, config, filename)
        # Also generate shortened CFGs with group-size and group-index comments.
        all_subroutines_to_dot(
            self.teal, dest, config, "txn_ctx"
        )  # set prefix differentiate from other printers
        print(f"\nExported CFG with transaction context information to {filename}")
