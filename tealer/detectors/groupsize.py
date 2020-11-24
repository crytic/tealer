from pathlib import Path
from typing import Dict, List

from tealer.detectors.abstract_detector import AbstractDetector
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.global_field import GroupSize
from tealer.teal.instructions import Gtxn, Return, Int, Global
from tealer.teal.teal import Teal


class Result:
    def __init__(self, filename: Path, path_initial: List[BasicBlock]):
        self.filename = filename
        self.paths = [path_initial]

    def add_path(self, path: List[BasicBlock]):
        self.paths.append(path)

    @property
    def all_bbs_in_paths(self):
        return [p for sublist in self.paths for p in sublist]


class MissingGroupSize(AbstractDetector):  # pylint: disable=too-few-public-methods
    def __init__(self, teal: Teal):
        super().__init__(teal)
        self.results_number = 0

    def _check_groupsize(
        self,
        bb: BasicBlock,
        current_path: List[BasicBlock],
        # use_gtnx: bool,
        all_results: Dict[str, Result],
    ):
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

                filename = Path(f"group_size{self.results_number}.dot")
                res = f"Bug found {ins.line}: {ins} does not check group_size\n"

                if res not in all_results:
                    self.results_number += 1

                    all_results[res] = Result(filename, current_path)
                else:
                    all_results[res].add_path(current_path)

        for next_bb in bb.next:
            self._check_groupsize(next_bb, current_path, all_results)

    def detect(self):

        all_results: Dict[str, Result] = dict()

        # Only applicable if there is a group instruction
        use_gtnx = [ins for ins in self.teal.instructions if isinstance(ins, Gtxn)]
        if use_gtnx:
            self._check_groupsize(self.teal.bbs[0], [], all_results)

        all_results_txt: List[str] = []
        for desc, res in all_results.items():
            all_results_txt.append(f"Result in {res.filename}:\n{desc}")
            self.teal.bbs_to_dot(res.filename, res.all_bbs_in_paths)

        return all_results_txt
