import logging
from typing import List, TYPE_CHECKING, Dict, Any, Type


from tealer.detectors.abstract_detector import AbstractDetector, DetectorClassification
from tealer.printers.abstract_printer import AbstractPrinter
from tealer.exceptions import TealerException


if TYPE_CHECKING:
    from tealer.teal.teal import Teal
    from tealer.utils.output import ListOutput
    from tealer.execution_context.transactions import GroupTransaction


# from slither: slither/slither.py
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

    def __init__(
        self,
        contracts: Dict[str, "Teal"],
        groups: List["GroupTransaction"],
        output_group: bool = False,
    ):
        self._contracts = contracts
        self._groups = groups

        self._detectors: List[AbstractDetector] = []
        self._printers: List[AbstractPrinter] = []
        # debug parameter to decide on the type of output reported by the detectors. TODO: Remove later.
        self._output_group: bool = output_group

    @property
    def contracts(self) -> Dict[str, "Teal"]:
        return self._contracts

    @property
    def contracts_list(self) -> List["Teal"]:
        return list(self._contracts.values())

    @property
    def groups(self) -> List["GroupTransaction"]:
        return self._groups

    @property
    def output_group(self) -> bool:
        return self._output_group

    # from slither: Slither Class in slither/slither.py
    @property
    def detectors(self) -> List[AbstractDetector]:
        """return list of registered detectors.

        Returns:
            Returns the list of registered detectors.
        """
        return self._detectors

    # from slither: Slither Class in slither/slither.py
    @property
    def detectors_high(self) -> List[AbstractDetector]:
        """return list of registered detectors with impact high

        Returns:
            Returns the list of registered detectors with impact high.
        """
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.HIGH]

    # from slither: Slither Class in slither/slither.py
    @property
    def detectors_medium(self) -> List[AbstractDetector]:
        """return list of registered detectors with impact medium

        Returns:
            Returns the list of registered detectors with impact medium.
        """
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.MEDIUM]

    # from slither: Slither Class in slither/slither.py
    @property
    def detectors_low(self) -> List[AbstractDetector]:
        """return list of registered detectors with impact low

        Returns:
            Returns the list of registered detectors with impact low.
        """
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.LOW]

    # from slither: Slither Class in slither/slither.py
    @property
    def detectors_informational(self) -> List[AbstractDetector]:
        """return list of registered detectors with impact informational

        Returns:
            Returns the list of registered detectors with impact informational.
        """
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.INFORMATIONAL]

    # from slither: Slither Class in slither/slither.py
    @property
    def detectors_optimization(self) -> List[AbstractDetector]:
        """return list of registered detectors with impact optimization

        Returns:
            Returns the list of registered detectors with impact optimization.
        """
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.OPTIMIZATION]

    # from slither: Slither Class in slither/slither.py
    @property
    def printers(self) -> List[AbstractPrinter]:
        """return list of registered printers.

        Returns:
            Returns the list of registered printers.
        """
        return self._printers

    # from slither: Slither Class in slither/slither.py
    def register_detector(self, detector_class: Type[AbstractDetector]) -> None:
        """Register detector to run on the contract.

        Args:
            detector_class: Class representing the detector.
        """

        _check_common_things("detector", detector_class, AbstractDetector, self._detectors)

        instance = detector_class(self)
        self._detectors.append(instance)

    # from slither: Slither Class in slither/slither.py
    def register_printer(self, printer_class: Type[AbstractPrinter]) -> None:
        """Register printer to run on the contract.

        Args:
            printer_class: Class representing the printer.
        """

        _check_common_things("printer", printer_class, AbstractPrinter, self._printers)
        # Run on the first contract for now. TODO: decide on how printers should behave in group context.
        instance = printer_class(list(self.contracts.values())[0])
        self._printers.append(instance)

    # from slither: Slither Class in slither/slither.py
    def run_detectors(self) -> List["ListOutput"]:
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

    # from slither: Slither Class in slither/slither.py
    def run_printers(self) -> List:
        """Run all the registered printers.

        Returns:
            List of results, each result corresponds to the output
            of a single printer.
        """

        return [p.print() for p in self._printers]
