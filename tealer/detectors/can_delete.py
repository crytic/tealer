from pathlib import Path
from typing import List

from tealer.detectors.abstract_detector import AbstractDetector, DetectorType
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import BZ, Instruction
from tealer.teal.instructions.instructions import Return, Int, Txn, Eq, BNZ
from tealer.teal.instructions.transaction_field import OnCompletion


def _is_delete(ins1: Instruction, ins2: Instruction) -> bool:
    if isinstance(ins1, Int) and ins1.value == "DeleteApplication":
        return isinstance(ins2, Txn) and isinstance(ins2.field, OnCompletion)
    return False


def _is_oncompletion_check(ins1: Instruction, ins2: Instruction) -> bool:
    if isinstance(ins1, Txn) and isinstance(ins1.field, OnCompletion):
        return isinstance(ins2, Int) and ins2.value in [
            "UpdateApplication",
            "NoOp",
            "OptIn",
            "CloseOut",
        ]
    return False


class CanDelete(AbstractDetector):  # pylint: disable=too-few-public-methods
    NAME = "canDelete"
    DESCRIPTION = "Detect paths that can delete the application"
    TYPE = DetectorType.STATEFULL

    def _check_delete(
        self,
        bb: BasicBlock,
        current_path: List[BasicBlock],
        paths_without_check: List[List[BasicBlock]],
    ) -> None:
        if bb in current_path:
            return

        current_path = current_path + [bb]

        # prev_was_oncompletion = False
        # prev_was_int = False
        prev_was_equal = False
        skip_false = False
        skip_true = False
        stack: List[Instruction] = []

        for ins in bb.instructions:

            if isinstance(ins, Return):
                if len(ins.prev) == 1:
                    prev = ins.prev[0]
                    if isinstance(prev, Int) and prev.value == 0:
                        return

                paths_without_check.append(current_path)
                return

            skip_false = isinstance(ins, BNZ) and prev_was_equal

            skip_true = isinstance(ins, BZ) and prev_was_equal

            prev_was_equal = False
            if isinstance(ins, Eq) and len(stack) >= 2:
                one = stack[-1]
                two = stack[-2]
                if _is_delete(one, two) or _is_delete(two, one):
                    return
                if _is_oncompletion_check(one, two) or _is_oncompletion_check(two, one):
                    prev_was_equal = True

            stack.append(ins)

        if skip_false:
            self._check_delete(bb.next[0], current_path, paths_without_check)
            return
        if skip_true:
            self._check_delete(bb.next[1], current_path, paths_without_check)
            return
        for next_bb in bb.next:
            self._check_delete(next_bb, current_path, paths_without_check)

    def detect(self) -> List[str]:

        paths_without_check: List[List[BasicBlock]] = []
        self._check_delete(self.teal.bbs[0], [], paths_without_check)

        all_results_txt: List[str] = []
        idx = 1
        for path in paths_without_check:
            filename = Path(f"can_delete_{idx}.dot")
            idx += 1
            description = "Lack of OnCompletion check allows to delete the app\n"
            description += f"\tCheck the path in {filename}\n"
            all_results_txt.append(description)
            self.teal.bbs_to_dot(filename, path)

        return all_results_txt
