from typing import List, TYPE_CHECKING

from tealer.detectors.abstract_detector import AbstractDetector, DetectorType
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.global_field import GroupSize
from tealer.teal.instructions.instructions import Return, Int, Global
from tealer.teal.teal import Teal

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput


class MissingGroupSize(AbstractDetector):  # pylint: disable=too-few-public-methods

    NAME = "groupSize"
    DESCRIPTION = "Detect paths with a missing GroupSize check"
    TYPE = DetectorType.STATEFULLGROUP

    WIKI_TITLE = "Missing GroupSize check"
    WIKI_DESCRIPTION = "Detect paths with a missing GroupSize check"
    WIKI_EXPLOIT_SCENARIO = """
**TODO**
"""
    WIKI_RECOMMENDATION = """
**TODO**
"""

    def __init__(self, teal: Teal):
        super().__init__(teal)
        self.results_number = 0

    def _check_groupsize(
        self,
        bb: BasicBlock,
        current_path: List[BasicBlock],
        # use_gtnx: bool,
        paths_without_check: List[List[BasicBlock]],
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

                paths_without_check.append(current_path)

        for next_bb in bb.next:
            self._check_groupsize(next_bb, current_path, paths_without_check)

    def detect(self) -> "SupportedOutput":

        paths_without_check: List[List[BasicBlock]] = []
        self._check_groupsize(self.teal.bbs[0], [], paths_without_check)

        description = "Lack of groupSize check found"
        filename = "missing_group_size"

        return self.generate_result(paths_without_check, description, filename)
