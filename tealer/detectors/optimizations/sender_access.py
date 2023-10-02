"""Detector for finding unoptimized access to the sender."""

from typing import TYPE_CHECKING, List

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.instructions.instructions import Instruction, Txna
from tealer.teal.instructions.transaction_field import Accounts
from tealer.utils.output import InstructionsOutput

if TYPE_CHECKING:
    from tealer.utils.output import ListOutput


class SenderAccess(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find unoptimized access to the sender"""

    NAME = "sender-access"
    DESCRIPTION = "Unoptimized Gtxn"
    TYPE = DetectorType.STATELESS

    IMPACT = DetectorClassification.OPTIMIZATION
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_URL = (
        "https://github.com/crytic/tealer/wiki/Detector-Documentation#Unoptimized-sender-access"
    )
    WIKI_TITLE = "Unoptimized sender access"
    WIKI_DESCRIPTION = "Txn.accounts[0] can be optimized to be Txn.sender()]"
    WIKI_EXPLOIT_SCENARIO = """"""

    WIKI_RECOMMENDATION = """Use Txn.sender()."""

    def detect(self) -> "ListOutput":
        """Detector to find unoptimized access to the sender

        Returns:
              The instruction to optimized
        """

        detector_output: "ListOutput" = []

        for contract in self.tealer.contracts.values():

            all_findings: List[List[Instruction]] = []

            for function in contract.functions.values():
                for block in function.blocks:
                    for ins in block.instructions:
                        if isinstance(ins, Txna) and isinstance(ins.field, Accounts) and ins.field.idx == 0:  # type: ignore
                            all_findings.append([ins])

            if all_findings:
                detector_output.append(InstructionsOutput(contract, self, all_findings))

        return detector_output
