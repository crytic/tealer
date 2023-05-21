import logging
from typing import List, Any, Type, TYPE_CHECKING

from tealer.detectors.abstract_detector import AbstractDetector, DetectorClassification
from tealer.printers.abstract_printer import AbstractPrinter

from tealer.exceptions import TealerException

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput
    from tealer.teal.teal import Teal
    from tealer.group_config.group_config import GroupTransaction


def _check_common_things(
    thing_name: str, cls: Any, base_cls: Any, instance_list: List[Any]
) -> None:
    """Check if the class is correct subclass and is unique.

    check if :cls: is subclass of :base_cls: and it's instance is not already
    present in :instance_list:. if either of the conditions fail, then an
    exception is raised.

    Args:
        thing_name: name of the feature(add-on) that will on the teal
            contract("detector" or "printer"). Used for error reporting.
        cls: Class representing the feature.
        base_cls: Base class for the feature.
        instance_list: List of objects already registered to run.

    Raises:
        TealerException: raises exception if the :cls: is not subclass of
            :base_cls: or if an object of :cls: is present in the
            :instance_list:.
    """

    if not issubclass(cls, base_cls) or cls is base_cls:
        raise TealerException(
            f"You can't register {cls.__name__} as a {thing_name}."
            f"You need to pass a class that inherits from {base_cls.__name__}"
        )

    if any(isinstance(obj, cls) for obj in instance_list):
        raise TealerException(f"You can't register {cls.__name__} twice.")


class Tealer:
    """Base class for the tool"""

    def __init__(self, contracts: List["Teal"], group_configs: List["GroupTransaction"]):
        self._contracts = contracts
        self._group_configs = group_configs

        self._detectors: List[AbstractDetector] = []
        self._printers: List[AbstractPrinter] = []

    @property
    def contracts(self) -> List["Teal"]:
        """List of contracts being analyzed"""
        return self._contracts

    @property
    def group_configs(self) -> List["GroupTransaction"]:
        return self._group_configs

    @property
    def detectors(self) -> List[AbstractDetector]:
        """List of registered detectors."""
        return self._detectors

    @property
    def detectors_high(self) -> List[AbstractDetector]:
        """List of registered detectors with impact high"""
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.HIGH]

    @property
    def detectors_medium(self) -> List[AbstractDetector]:
        """List of registered detectors with impact medium"""
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.MEDIUM]

    @property
    def detectors_low(self) -> List[AbstractDetector]:
        """List of registered detectors with impact low"""
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.LOW]

    @property
    def detectors_informational(self) -> List[AbstractDetector]:
        """List of registered detectors with impact informational"""
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.INFORMATIONAL]

    @property
    def detectors_optimization(self) -> List[AbstractDetector]:
        """List of registered detectors with impact optimization"""
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.OPTIMIZATION]

    @property
    def printers(self) -> List[AbstractPrinter]:
        """List of registered printers."""
        return self._printers

    def register_detector(self, detector_class: Type[AbstractDetector]) -> None:
        """Register detector to run on the contract.

        Args:
            detector_class: Class representing the detector.
        """

        _check_common_things("detector", detector_class, AbstractDetector, self._detectors)
        for contract in self.contracts:
            instance = detector_class(contract)
            self._detectors.append(instance)

    def register_printer(self, printer_class: Type[AbstractPrinter]) -> None:
        """Register printer to run on the contract.

        Args:
            printer_class: Class representing the printer.
        """

        _check_common_things("printer", printer_class, AbstractPrinter, self._printers)

        for contract in self.contracts:
            instance = printer_class(contract)
            self._printers.append(instance)

    def run_detectors(self) -> List["SupportedOutput"]:
        """Run all the registered detectors.

        Returns:
            List of results, each result corresponds to the output
            of a single detector.
        """

        results = []
        logger = logging.getLogger("Tealer")
        for d in self._detectors:
            logger.debug(f'[+] Running detector "{d.NAME}"')
            results.append(d.detect())

        return results

    def run_printers(self) -> List:
        """Run all the registered printers.

        Args:
            dest: Optional. :dest: is used by printers to determine
                the destination directory to save the output files.
                if :dest: is None, current directory is used as destination
                directory.

        Returns:
            List of results, each result corresponds to the output
            of a single printer.
        """

        return [p.print() for p in self._printers]
