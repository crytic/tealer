"""Detector for finding unoptimized usage of constant GTXN."""

from typing import TYPE_CHECKING, List

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.instructions.instructions import Gtxns, Instruction
from tealer.utils.analyses import is_int_push_ins
from tealer.utils.output import InstructionsOutput

if TYPE_CHECKING:
    from tealer.utils.output import ListOutput


class ConstantGtxn(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find unoptimized usage of constant GTXN"""

    NAME = "constant-gtxn"
    DESCRIPTION = "Unoptimized Gtxn"
    TYPE = DetectorType.STATELESS

    IMPACT = DetectorClassification.OPTIMIZATION
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_URL = "https://github.com/crytic/tealer/wiki/Detector-Documentation#Unoptimized-Gtxn"
    WIKI_TITLE = "Unoptimized Gtxn"
    WIKI_DESCRIPTION = (
        "- Gtxn[Int(1)].field() produces instructions int 1; gtxns field"
        "- Gtxn[1].field() produces only one instruction: gtxn 1 field"
    )
    WIKI_EXPLOIT_SCENARIO = """"""

    WIKI_RECOMMENDATION = """Use Gtxn[idx].field()."""

    def detect(self) -> "ListOutput":
        """Detector to find unoptimized usage of constant GTXN

        Returns:
              The two instructions to optimized
        """

        detector_output: "ListOutput" = []

        for contract in self.tealer.contracts.values():

            all_findings: List[List[Instruction]] = []

            for function in contract.functions.values():
                for block in function.blocks:
                    if len(block.instructions) < 2:
                        continue

                    # Sliding windows
                    for i in range(0, len(block.instructions) - 1):
                        first = block.instructions[i]
                        second = block.instructions[i + 1]

                        # Note: first / second are always assigned, as we check for len(block.instructions) first
                        # pylint: disable=undefined-loop-variable
                        first_ins_is_int, _ = is_int_push_ins(first)
                        # pylint: disable=undefined-loop-variable
                        if first_ins_is_int and isinstance(second, Gtxns):
                            # pylint: disable=undefined-loop-variable
                            all_findings.append([first, second])

            if all_findings:
                detector_output.append(InstructionsOutput(contract, self, all_findings))

        return detector_output
