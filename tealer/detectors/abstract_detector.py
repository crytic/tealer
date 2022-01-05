import abc
from typing import List, TYPE_CHECKING

from tealer.utils.comparable_enum import ComparableEnum
from tealer.utils.output import ExecutionPaths

if TYPE_CHECKING:
    from tealer.teal.teal import Teal
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.utils.output import SupportedOutput


class IncorrectDetectorInitialization(Exception):
    pass


class DetectorType(ComparableEnum):
    STATELESS = 0
    STATEFULL = 1
    STATEFULLGROUP = 2

    UNDEFINED = 255


DETECTOR_TYPE_TXT = {
    DetectorType.STATELESS: "Stateless",
    DetectorType.STATEFULL: "Stateful",
    DetectorType.STATEFULLGROUP: "StatefulGroup",
}


class DetectorClassification(ComparableEnum):
    HIGH = 0
    MEDIUM = 1
    LOW = 2
    INFORMATIONAL = 3
    OPTIMIZATION = 4

    UNIMPLEMENTED = 999


classification_txt = {
    DetectorClassification.OPTIMIZATION: "Optimization",
    DetectorClassification.INFORMATIONAL: "Informational",
    DetectorClassification.LOW: "Low",
    DetectorClassification.MEDIUM: "Medium",
    DetectorClassification.HIGH: "High",
}


class AbstractDetector(metaclass=abc.ABCMeta):  # pylint: disable=too-few-public-methods

    NAME = ""  # detector name
    DESCRIPTION = ""
    TYPE = DetectorType.UNDEFINED

    IMPACT: DetectorClassification = DetectorClassification.UNIMPLEMENTED
    CONFIDENCE: DetectorClassification = DetectorClassification.UNIMPLEMENTED

    WIKI_TITLE = ""
    WIKI_DESCRIPTION = ""
    WIKI_EXPLOIT_SCENARIO = ""
    WIKI_RECOMMENDATION = ""

    def __init__(self, teal: "Teal"):
        self.teal = teal

        if not self.NAME:
            raise IncorrectDetectorInitialization(
                f"NAME is not initialized {self.__class__.__name__}"
            )

        if not self.DESCRIPTION:
            raise IncorrectDetectorInitialization(
                f"DESCRIPTION is not initialized {self.__class__.__name__}"
            )

        if self.TYPE == DetectorType.UNDEFINED:
            raise IncorrectDetectorInitialization(
                f"TYPE is not initialized {self.__class__.__name__}"
            )

        if not self.WIKI_TITLE:
            raise IncorrectDetectorInitialization(
                f"WIKI_TITLE is not initialized {self.__class__.__name__}"
            )

        if not self.WIKI_DESCRIPTION:
            raise IncorrectDetectorInitialization(
                f"WIKI_DESCRIPTION is not initialized {self.__class__.__name__}"
            )

        if not self.WIKI_EXPLOIT_SCENARIO:
            raise IncorrectDetectorInitialization(
                f"WIKI_EXPLOIT_SCENARIO is not initialized {self.__class__.__name__}"
            )

        if not self.WIKI_RECOMMENDATION:
            raise IncorrectDetectorInitialization(
                f"WIKI_RECOMMENDATION is not initialized {self.__class__.__name__}"
            )

        if self.IMPACT not in [
            DetectorClassification.LOW,
            DetectorClassification.MEDIUM,
            DetectorClassification.HIGH,
            DetectorClassification.INFORMATIONAL,
            DetectorClassification.OPTIMIZATION,
        ]:
            raise IncorrectDetectorInitialization(
                f"IMPACT is not initialized {self.__class__.__name__}"
            )

        if self.CONFIDENCE not in [
            DetectorClassification.LOW,
            DetectorClassification.MEDIUM,
            DetectorClassification.HIGH,
        ]:
            raise IncorrectDetectorInitialization(
                f"CONFIDENCE is not initialized {self.__class__.__name__}"
            )

    def generate_result(
        self, paths: List[List["BasicBlock"]], description: str, filename: str
    ) -> ExecutionPaths:
        output = ExecutionPaths(self.teal.bbs, description, filename)

        for path in paths:
            output.add_path(path)

        output.check = self.NAME
        # output.impact = classification_txt[self.IMPACT]
        # output.confidence = classification_txt[self.CONFIDENCE]
        output.help = self.WIKI_RECOMMENDATION.strip()

        return output

    @abc.abstractmethod
    def detect(self) -> "SupportedOutput":
        """TODO Documentation"""
