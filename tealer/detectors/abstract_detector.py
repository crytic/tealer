import abc
from typing import List, TYPE_CHECKING

from tealer.utils.comparable_enum import ComparableEnum

if TYPE_CHECKING:
    from tealer.teal.teal import Teal


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


class AbstractDetector(metaclass=abc.ABCMeta):  # pylint: disable=too-few-public-methods

    NAME = ""  # detector name
    DESCRIPTION = ""
    TYPE = DetectorType.UNDEFINED

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

    @abc.abstractmethod
    def detect(self) -> List[str]:
        """TODO Documentation"""
        return []
