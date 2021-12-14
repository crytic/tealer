from pathlib import Path
from typing import List

from tealer.detectors.abstract_detector import AbstractDetector, DetectorType
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.global_field import GroupSize
from tealer.teal.instructions.instructions import Return, Int, Global
from tealer.teal.teal import Teal


class Result:  # pylint: disable=too-few-public-methods
    def __init__(self, filename: Path, path_initial: List[BasicBlock], idx: int):
        self.filename = filename
        self.paths = [path_initial]
        self.idx = idx

    @property
    def all_bbs_in_paths(self) -> List[BasicBlock]:
        return [p for sublist in self.paths for p in sublist]


class MissingGroupSize(AbstractDetector):  # pylint: disable=too-few-public-methods

    NAME = "groupSize"
    DESCRIPTION = "Detect paths with a missing GroupSize check"
    TYPE = DetectorType.STATEFULLGROUP

    def __init__(self, teal: Teal):
        super().__init__(teal)
        self.results_number = 0

    def _check_groupsize(
        self,
        bb: BasicBlock,
        current_path: List[BasicBlock],
        # use_gtnx: bool,
        all_results: List[Result],
    ) -> None:
        # check for loops
        if bb in current_path:
            return

        current_path = current_path + [bb]
        for ins in bb.instructions:

            if isinstance(ins, Global):
                if isinstance(ins.field, GroupSize):
                    return

            if isinstance(ins, Return):
                if len(ins.prev) == 1:
                    prev = ins.prev[0]
                    if isinstance(prev, Int):
                        if prev.value == 0:
                            return

                filename = Path(f"group_size_{self.results_number}.dot")
                self.results_number += 1
                all_results.append(Result(filename, current_path, self.results_number))

        for next_bb in bb.next:
            self._check_groupsize(next_bb, current_path, all_results)

    def detect(self) -> List[str]:

        all_results: List[Result] = []

        self._check_groupsize(self.teal.bbs[0], [], all_results)

        all_results_txt: List[str] = []
        for res in all_results:
            description = "Lack of groupSize check found\n"
            description += f"\tFix the paths in {res.filename}\n"
            description += (
                "\tOr ensure it is used with stateless contracts that check for GroupSize\n"
            )

            all_results_txt.append(description)
            self.teal.bbs_to_dot(res.filename, res.all_bbs_in_paths)

        return all_results_txt
