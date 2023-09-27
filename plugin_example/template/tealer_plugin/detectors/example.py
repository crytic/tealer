from typing import TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)


if TYPE_CHECKING:
    from tealer.utils.output import ListOutput


class Example(AbstractDetector):  # pylint: disable=too-few-public-methods
    """
    Documentation
    """

    NAME = "mydetector"  # this is used to select the detector and also while showing output
    DESCRIPTION = "Description of the detector."
    TYPE: DetectorType = DetectorType.STATELESS  # type of detector

    IMPACT: DetectorClassification = DetectorClassification.HIGH
    CONFIDENCE: DetectorClassification = DetectorClassification.HIGH

    WIKI_TITLE = ""
    WIKI_DESCRIPTION = ""
    WIKI_EXPLOIT_SCENARIO = ""
    WIKI_RECOMMENDATION = ""  # this will be shown in json output as help message

    def detect(self) -> "ListOutput":
        """This method will be called if this detector is chosen.

        Implement this method to return output in one of the supported formats (ExecutionPaths).
        Use `generate_result` method to generate the output after finding the list of execution
        paths considered to be vulnerable or need to be highlighted. `generate_result` also takes
        two parameters `description` and `filename`. `description` is supposed to explain about the
        execution path and `filename` is the filename prefix of the output dot files.

        See `rekey_plugin` for actual implementation of a plugin.
        """
