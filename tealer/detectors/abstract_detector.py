import abc
from typing import List

from tealer.teal.teal import Teal
from tealer.utils.comparable_enum import ComparableEnum


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

    def __init__(self, teal: Teal):
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
                "WIKI_TITLE is not initialized {}".format(self.__class__.__name__)
            )

        if not self.WIKI_DESCRIPTION:
            raise IncorrectDetectorInitialization(
                "WIKI_DESCRIPTION is not initialized {}".format(self.__class__.__name__)
            )

        if not self.WIKI_EXPLOIT_SCENARIO:
            raise IncorrectDetectorInitialization(
                "WIKI_EXPLOIT_SCENARIO is not initialized {}".format(self.__class__.__name__)
            )

        if not self.WIKI_RECOMMENDATION:
            raise IncorrectDetectorInitialization(
                "WIKI_RECOMMENDATION is not initialized {}".format(self.__class__.__name__)
            )

    @abc.abstractmethod
    def detect(self) -> List[str]:
        """TODO Documentation"""
        return []
