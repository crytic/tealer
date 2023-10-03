"""Detector for finding unoptimized self access"""

from typing import TYPE_CHECKING, List

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.instructions.instructions import Gtxns, Instruction, Txn, Gtxnsa, Gtxnsas
from tealer.teal.instructions.transaction_field import GroupIndex
from tealer.utils.output import InstructionsOutput

if TYPE_CHECKING:
    from tealer.utils.output import ListOutput


class SelfAccess(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find unoptimized self access"""

    NAME = "self-access"
    DESCRIPTION = "Unoptimized self access"
    TYPE = DetectorType.STATELESS

    IMPACT = DetectorClassification.OPTIMIZATION
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_URL = (
        "https://github.com/crytic/tealer/wiki/Detector-Documentation#Unoptimized-self-access"
    )
    WIKI_TITLE = "Unoptimized self access"
    WIKI_DESCRIPTION = "Gtxn[Txn.group_index()].field can be replaced by Txn.field"
    WIKI_EXPLOIT_SCENARIO = """"""

    WIKI_RECOMMENDATION = """Use Txn.field."""

    def detect(self) -> "ListOutput":
        """Detector to find unoptimized usage of self access

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
                        if (
                            isinstance(first, Txn)
                            and isinstance(first.field, GroupIndex)
                            and isinstance(second, (Gtxns, Gtxnsa, Gtxnsas))
                        ):
                            # pylint: disable=undefined-loop-variable
                            all_findings.append([first, second])

            if all_findings:
                detector_output.append(InstructionsOutput(contract, self, all_findings))

        return detector_output
