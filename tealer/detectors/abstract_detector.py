"""Defines abstract base class for detectors in tealer.

This module contains implementation of abstract class which
defines the attributes, common methods and must implement methods
of detectors. All detectors in tealer must inherit from this class
and set attributes, override abstract methods.

Attributes:
    DetectorType: DetectorType is a comparable enumerator. Detector
        type indicates what kind of contracts is that detector supposed
        to work on and find issues in them. DetectorType defines three
        symbols ``STATELESS``, ``STATEFULL``, ``STATEFULLGROUP``.

        ``STATELESS`` detectors work on and find issues in stateless
        contracts(signatures).

        ``STATEFULL`` detectors try to find issues that commonly occur
        in stateful(application) contracts.

        ``STATEFULLGROUP`` detectors work on stateful contracts that are
        supposed to verify security related checks for other transactions/
        contracts in the atomic group. One of the algorand smart contract
        development architecture is to have one contract commonly an
        application that must be included with most of the transaction
        groups interacting with the system. This contract's job is to
        verify the security properties of other transactions in the group
        along with the security properties of it's own transaction.
        ``STATEFULLGROUP`` type of detectors find issues in this kind of
        contracts, whether they are verifying/doing all the related
        security checks for other transactions in the group.

    DETECTOR_TYPE_TXT: Map from DetectorType symbol to it's string representation.

    DetectorClassification: DetectorClassification is a comparable enumerator.
        It defines ``HIGH``, ``MEDIUM``, ``LOW``, ``INFORMATIONAL`` and
        ``OPTIMIZATION``. This class is used to classify detector's impact and
        confidence.

    classification_txt: Map from DetectorClassification symbol to it's string
        representation.

Classes:
    AbstractDetector: Abstract class to represent detectors in tealer.
"""

import abc
from typing import TYPE_CHECKING

from tealer.utils.comparable_enum import ComparableEnum

if TYPE_CHECKING:
    from tealer.tealer import Tealer
    from tealer.utils.output import ListOutput


class IncorrectDetectorInitialization(Exception):
    """Exception class to represent incorrect detector intialization.

    This exception will be used if any of the necessary attributes of
    the AbstractDetector are not set by the inheriting detector class.
    """


# DetectorType is used to specify "Applicability of a detector."
class DetectorType(ComparableEnum):
    # Order by stateful, stateless and stateful, stateless
    STATEFULL = 0
    STATELESS_AND_STATEFULL = 1
    STATELESS = 2
    STATEFULLGROUP = 3

    UNDEFINED = 255


DETECTOR_TYPE_TXT = {
    DetectorType.STATELESS: "Stateless",
    DetectorType.STATEFULL: "Stateful",
    DetectorType.STATELESS_AND_STATEFULL: "Stateless, Stateful",
    DetectorType.STATEFULLGROUP: "StatefulGroup",
}


class DetectorClassification(ComparableEnum):
    HIGH = 0
    MEDIUM = 1
    LOW = 2
    INFORMATIONAL = 3
    OPTIMIZATION = 4

    UNIMPLEMENTED = 999

    def __str__(self) -> str:
        return self.name.title()


classification_txt = {
    DetectorClassification.OPTIMIZATION: "Optimization",
    DetectorClassification.INFORMATIONAL: "Informational",
    DetectorClassification.LOW: "Low",
    DetectorClassification.MEDIUM: "Medium",
    DetectorClassification.HIGH: "High",
}


class AbstractDetector(metaclass=abc.ABCMeta):  # pylint: disable=too-few-public-methods
    """Abstract class to represent detectors in tealer.

    All detectors in tealer must inherit from this class and overrride
    the abstract methods with functionality specific to them. This class
    defines the api methods that must be implemented by every detector.
    ``detect`` method of each detector will be called to execute the
    detector. Every detector must implement ``detect`` method.

    Attributes:
        NAME: Name of the detector. Detector name will be used while
            displaying information about the printer and also for selecting
            the detector from command line.

        DESCRIPTION: Description of the detector about what it tries to find.

        IMPACT: Severity of the issue the detector tries to detect. IMPACT is
            classified into ``HIGH``, ``MEDIUM``, ``LOW``, ``INFORMATIONAL`` and
        ``OPTIMIZATION`` using DetectorClassification enum.

        CONFIDENCE: Precision of the detector, how often the results of this
            detector are true. Confidence is classified into ``HIGH``, ``MEDIUM``
            and ``LOW`` using DetectorClassification enum.

        WIKI_TITLE: Wiki title of the detector/issue.

        WIKI_DESCRIPTION: Wiki description of the detector.

        WIKI_EXPLOIT_SCENARIO: Example exploit scenario exploiting the issue this
            detector tries to find.

        WIKI_RECOMMENDATION: Help or recommendation message on how to avoid, remove
            this issue/vuln from the contract.

    Args:
        teal: Teal instance representing the contract. Detector will analyze the
            contract represented by :teal: for issues/vulnerabilites .

    Raises:
        IncorrectDetectorInitialization: Exception is raised if any of the class
            attributes are not intialized properly by the inheriting detector class.
    """

    NAME = ""  # detector name
    DESCRIPTION = ""
    TYPE = DetectorType.UNDEFINED

    IMPACT: DetectorClassification = DetectorClassification.UNIMPLEMENTED
    CONFIDENCE: DetectorClassification = DetectorClassification.UNIMPLEMENTED

    WIKI_URL = ""
    WIKI_TITLE = ""
    WIKI_DESCRIPTION = ""
    WIKI_EXPLOIT_SCENARIO = ""
    WIKI_RECOMMENDATION = ""

    def __init__(self, tealer: "Tealer"):
        self.tealer = tealer

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

        if not self.WIKI_EXPLOIT_SCENARIO and self.IMPACT not in [
            DetectorClassification.INFORMATIONAL,
            DetectorClassification.OPTIMIZATION,
        ]:
            raise IncorrectDetectorInitialization(
                f"WIKI_EXPLOIT_SCENARIO is not initialized {self.__class__.__name__}"
            )

        if not self.WIKI_RECOMMENDATION:
            raise IncorrectDetectorInitialization(
                f"WIKI_RECOMMENDATION is not initialized {self.__class__.__name__}"
            )

        if not self.WIKI_URL:
            raise IncorrectDetectorInitialization(
                f"WIKI_URL is not initialized {self.__class__.__name__}"
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

    @abc.abstractmethod
    def detect(self) -> "ListOutput":
        """Entry method of detector.

        All detectors must override this method with the functionality specific
        to them. This method is the entry point of the detector and will be
        called to execute it.

        Returns:
            Detector results represented in one of the supported types. Currently,
            all detectors work on Control Flow Graph(CFG) of the contract and represent
            the issues in the form of execution path in the CFG. ExecutionPaths class
            is used to represent them.

        # noqa: DAR202
        """
