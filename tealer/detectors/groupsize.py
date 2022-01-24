"""Detector for finding execution paths missing GroupSize check."""

from typing import List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.global_field import GroupSize
from tealer.teal.instructions.instructions import Return, Int, Global
from tealer.teal.teal import Teal

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput


class MissingGroupSize(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find execution paths missing GroupSize check.

    Algorand supports atomic transactions. Atomic transactions are a
    group of transactions with the property that either all execute
    successfully or None of them. It is necessary to check the group size
    of the transaction based on the application.

    This detector tries to find execution paths that approve the algorand
    transaction("return 1") and doesn't check the CloseRemainderTo field.
    """

    NAME = "groupSize"
    DESCRIPTION = "Detect paths with a missing GroupSize check"
    TYPE = DetectorType.STATEFULLGROUP

    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_TITLE = "Missing GroupSize check"
    WIKI_DESCRIPTION = "Detect paths with a missing GroupSize check"
    WIKI_EXPLOIT_SCENARIO = """
Consider the system consisting of two contracts, designed in such a way that first contract should be called by the
first transaction of the group and second one by the second transaction. first contract handles all the verification,
second contract approves the transfer of certain amount of assets if first contract approves its transaction.
ofcourse, second contract verifies that first transaction in the group is call to the first contract.

Possible exploit scenario is if second contract **only** verifies that first transaction is a call to first contract and
doesn't check the group size to the expected value of `2`. The attacker could add an additional transaction(s) which are
copy of second transaction i.e transfer of assets. As all the transactions to second contract only verify the first transaction,
the attacker may possibly transfer all the assets by appending transactions which are each a copy of second transaction.

Attacker can get upto 14 times(max atomic group size 16) more than the intended amount.
"""
    WIKI_RECOMMENDATION = """
Always verify that group size(number of transactions in atomic group) is equal to what logic is expecting.
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
        """Find execution paths with missing GroupSize check.

        This function recursively explores the Control Flow Graph(CFG) of the
        contract and reports execution paths with missing GroupSize
        check.

        This function is "in place", modifies arguments with the data it is
        supposed to return.

        Args:
            bb: Current basic block being checked(whose execution is simulated.)
            current_path: Current execution path being explored.
            paths_without_check:
                Execution paths with missing GroupSize check. This is a
                "in place" argument. Vulnerable paths found by this function are
                appended to this list.
        """

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
        """Detect execution paths with missing GroupSize check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        paths_without_check: List[List[BasicBlock]] = []
        self._check_groupsize(self.teal.bbs[0], [], paths_without_check)

        description = "Lack of groupSize check found"
        filename = "missing_group_size"

        return self.generate_result(paths_without_check, description, filename)
