from pathlib import Path
from typing import List, Any, Optional, Type, TYPE_CHECKING

from tealer.detectors.abstract_detector import AbstractDetector
from tealer.printers.abstract_printer import AbstractPrinter

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Instruction, ContractType
from tealer.exceptions import TealerException

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput


def _check_common_things(
    thing_name: str, cls: Any, base_cls: Any, instance_list: List[Any]
) -> None:

    if not issubclass(cls, base_cls) or cls is base_cls:
        raise TealerException(
            f"You can't register {cls.__name__} as a {thing_name}."
            f"You need to pass a class that inherits from {base_cls.__name__}"
        )

    if any(isinstance(obj, cls) for obj in instance_list):
        raise TealerException(f"You can't register {cls.__name__} twice.")


class Teal:
    def __init__(
        self,
        instructions: List[Instruction],
        bbs: List[BasicBlock],
        version: int,
        mode: ContractType,
    ):
        self._instructions = instructions
        self._bbs = bbs
        self._version = version
        self._mode = mode

        self._detectors: List[AbstractDetector] = []
        self._printers: List[AbstractPrinter] = []

    @property
    def instructions(self) -> List[Instruction]:
        return self._instructions

    @property
    def bbs(self) -> List[BasicBlock]:
        return self._bbs

    @property
    def version(self) -> int:
        return self._version

    @version.setter
    def version(self, ver: int) -> None:
        self._version = ver

    @property
    def mode(self) -> ContractType:
        return self._mode

    @mode.setter
    def mode(self, m: ContractType) -> None:
        self._mode = m

    @property
    def detectors(self) -> List[AbstractDetector]:
        return self._detectors

    @property
    def printers(self) -> List[AbstractPrinter]:
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
