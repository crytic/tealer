from collections import defaultdict
from copy import copy
from pathlib import Path
from typing import Dict, Set, List

from tealer.detectors.abstract_detector import AbstractDetector, DetectorType
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Gtxn, Return, Int, BZ, Instruction
from tealer.teal.teal import Teal
from tealer.teal.instructions.transaction_field import RekeyTo
from tealer.teal.instructions.instructions import Return, Int, Txn, Eq, BNZ
from tealer.teal.instructions.transaction_field import OnCompletion


def _is_delete(ins1: Instruction, ins2: Instruction):
    if isinstance(ins1, Int) and ins1.value == "DeleteApplication":
        return isinstance(ins2, Txn) and isinstance(ins2.field, OnCompletion)
    return False


def _is_oncompletion_check(ins1: Instruction, ins2: Instruction):
    if isinstance(ins1, Txn) and isinstance(ins1.field, OnCompletion):
        return isinstance(ins2, Int) and ins2.value in ["UpdateApplication", "NoOp", "OptIn", "CloseOut"]
    return False


class CanDelete(AbstractDetector):
    NAME = "canDelete"
    DESCRIPTION = "Detect paths that can delete the application"
    TYPE = DetectorType.STATEFULL

    def __init__(self, teal: Teal):
        super().__init__(teal)

    def _check_delete(
            self,
            bb: BasicBlock,
            current_path: List[BasicBlock],
            paths_without_check: List[List[BasicBlock]],
    ):
        current_path = current_path + [bb]

        # prev_was_oncompletion = False
        # prev_was_int = False
        prev_was_equal = False
        skip_false = False
        skip_true = False
        stack = []

        for ins in bb.instructions:

            if isinstance(ins, Return):
                if len(ins.prev) == 1:
                    prev = ins.prev[0]
                    if isinstance(prev, Int) and prev.value == 0:
                        return

                paths_without_check.append(current_path)
                return

            if isinstance(ins, BNZ) and prev_was_equal:
                skip_false = True

            if isinstance(ins, BZ) and prev_was_equal:
                skip_true = True

            prev_was_equal = False
            if isinstance(ins, Eq):
                one = stack[-1]
                two = stack[-2]
                if _is_delete(one, two) or _is_delete(two, one):
                    return
                if _is_oncompletion_check(one, two) or _is_oncompletion_check(two, one):
                    prev_was_equal = True

            stack.append(ins)

        if skip_false:
            self._check_delete(bb.next[0], current_path, paths_without_check)
        elif skip_true:
            if len(bb.next) > 1:
                self._check_delete(bb.next[1], current_path, paths_without_check)
        else:
            for next_bb in bb.next:
                self._check_delete(next_bb, current_path, paths_without_check)

    def detect(self):

        paths_without_check: List[List[BasicBlock]] = []
        self._check_delete(self.teal.bbs[0], [], paths_without_check)

        all_results_txt: List[str] = []
        idx = 1
        for path in paths_without_check:
            filename = Path(f"can_delete_{idx}.dot")
            idx += 1
            description = f"Lack of OnCompletion check allows to delete the app\n"
            description += f"\tCheck the path in {filename}\n"
            all_results_txt.append(description)
            self.teal.bbs_to_dot(filename, path)

        return all_results_txt
