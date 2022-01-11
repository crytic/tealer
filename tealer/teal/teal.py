from pathlib import Path
from typing import List, Any, Optional, Type, TYPE_CHECKING

from tealer.detectors.abstract_detector import AbstractDetector, DetectorClassification
from tealer.printers.abstract_printer import AbstractPrinter

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Instruction, ContractType
from tealer.exceptions import TealerException

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput


def _check_common_things(
    thing_name: str, cls: Any, base_cls: Any, instance_list: List[Any]
) -> None:
    """check if cls is subclass of base_cls and it's instance is not already
    present in instance_list. if either of the conditions fail, then error is
    raised.
    """
    if not issubclass(cls, base_cls) or cls is base_cls:
        raise TealerException(
            f"You can't register {cls.__name__} as a {thing_name}."
            f"You need to pass a class that inherits from {base_cls.__name__}"
        )

    if any(isinstance(obj, cls) for obj in instance_list):
        raise TealerException(f"You can't register {cls.__name__} twice.")


class Teal:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        instructions: List[Instruction],
        bbs: List[BasicBlock],
        version: int,
        mode: ContractType,
        subroutines: List[List["BasicBlock"]],
    ):
        self._instructions = instructions
        self._bbs = bbs
        self._version = version
        self._mode = mode
        self._subroutines = subroutines

        self._detectors: List[AbstractDetector] = []
        self._printers: List[AbstractPrinter] = []

    @property
    def instructions(self) -> List[Instruction]:
        """List of instructions of the contract"""
        return self._instructions

    @property
    def bbs(self) -> List[BasicBlock]:
        """CFG of the contract"""
        return self._bbs

    @property
    def subroutines(self) -> List[List["BasicBlock"]]:
        """Returns list of subroutines.

        Each subroutine is represented by the list of basic blocks that constitute
        a that particular subroutine. Subroutines are supported from version Teal 4 onwards.
        For Teal version 3 or less this property will return empty List.
        """
        return self._subroutines

    @property
    def version(self) -> int:
        """Teal version for this contract.

        Version of the contract is based on whether the first instruction of the
        contract is #pragma version instruction or not. if it is, then version will
        be the teal version specified or else, version will be 1.
        """
        return self._version

    @version.setter
    def version(self, ver: int) -> None:
        self._version = ver

    @property
    def mode(self) -> ContractType:
        """Type of the contract: Stateless, Stateful or Any.

        Mode is determined based on the instructions of the contract. if there are
        any instructions that are only supported in one kind of contract then that
        will be the contract type. if there aren't any such type of instructions, then
        this will be "Any".
        """
        return self._mode

    @mode.setter
    def mode(self, m: ContractType) -> None:
        self._mode = m

    @property
    def detectors(self) -> List[AbstractDetector]:
        """return list of registered detectors."""
        return self._detectors

    @property
    def detectors_high(self) -> List[AbstractDetector]:
        """return list of registered detectors with impact high"""
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.HIGH]

    @property
    def detectors_medium(self) -> List[AbstractDetector]:
        """return list of registered detectors with impact medium"""
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.MEDIUM]

    @property
    def detectors_low(self) -> List[AbstractDetector]:
        """return list of registered detectors with impact low"""
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.LOW]

    @property
    def detectors_informational(self) -> List[AbstractDetector]:
        """return list of registered detectors with impact informational"""
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.INFORMATIONAL]

    @property
    def detectors_optimization(self) -> List[AbstractDetector]:
        """return list of registered detectors with impact optimization"""
        return [d for d in self._detectors if d.IMPACT == DetectorClassification.OPTIMIZATION]

    @property
    def printers(self) -> List[AbstractPrinter]:
        """return list of registered printers."""
        return self._printers

    def register_detector(self, detector_class: Type[AbstractDetector]) -> None:
        _check_common_things("detector", detector_class, AbstractDetector, self._detectors)

        instance = detector_class(self)
        self._detectors.append(instance)

    def register_printer(self, printer_class: Type[AbstractPrinter]) -> None:
        _check_common_things("printer", printer_class, AbstractPrinter, self._printers)

        instance = printer_class(self)
        self._printers.append(instance)

    def run_detectors(self) -> List["SupportedOutput"]:
        results = [d.detect() for d in self._detectors]

        return results

    def run_printers(self, dest: Optional[Path] = None) -> List:
        return [p.print(dest) for p in self._printers]
