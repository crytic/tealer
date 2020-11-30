from pathlib import Path
from typing import List

from tealer.printers.abstract_printer import AbstractPrinter
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Return, Int, Txn, Eq, BNZ
from tealer.teal.teal import Teal
from tealer.teal.instructions.transaction_field import OnCompletion


class UpdateApplication(AbstractPrinter):  # pylint: disable=too-few-public-methods
    def __init__(self, teal: Teal):
        super().__init__(teal)
        self.results_number = 0

    def _check_update(
        self,
        bb: BasicBlock,
        current_path: List[BasicBlock],
        paths_without_check: List[List[BasicBlock]],
    ):
        current_path = current_path + [bb]

        prev_was_oncompletion = False
        prev_was_int = False
        prev_was_equal = False
        skip_false = False

        for ins in bb.instructions:
            if isinstance(ins, Int) and prev_was_oncompletion and ins.value == "UpdateApplication":
                return

            if isinstance(ins, Return):
                if len(ins.prev) == 1:
                    prev = ins.prev[0]
                    if isinstance(prev, Int) and prev.value == 0:
                        return

                paths_without_check.append(current_path)
                return

            if isinstance(ins, BNZ) and prev_was_equal:
                skip_false = True

            prev_was_equal = False
            if isinstance(ins, Eq) and prev_was_int:
                prev_was_equal = True

            prev_was_int = False
            if (
                isinstance(ins, Int)
                and prev_was_oncompletion
                and ins.value in ["DeleteApplication", "NoOp", "OptIn", "CloseOut"]
            ):
                prev_was_int = True

            prev_was_oncompletion = False
            if isinstance(ins, Txn) and isinstance(ins.field, OnCompletion):
                prev_was_oncompletion = True

        if skip_false:
            self._check_update(bb.next[0], current_path, paths_without_check)
        else:
            for next_bb in bb.next:
                self._check_update(next_bb, current_path, paths_without_check)

    def print(self):

        filename = Path("can_update.dot")

        paths_without_check: List[List[BasicBlock]] = []
        self._check_update(self.teal.bbs[0], [], paths_without_check)

        self.teal.bbs_to_dot(
            filename, list({p for sublist in paths_without_check for p in sublist})
        )

        print(f"Export in {filename}")
