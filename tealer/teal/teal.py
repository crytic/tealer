"""Defines class to represent Teal contracts.

Teal class is used to store Control Flow Graph of the contract.
It comes with methods for running detectors, printers on the contract.
And also has properties for easy access of the parsed contract
information.

Classes:
    Teal: Class to represent a contract.
"""

import logging
from typing import List, Any, Type, TYPE_CHECKING, Tuple, Dict, Optional

from tealer.detectors.abstract_detector import AbstractDetector, DetectorClassification
from tealer.printers.abstract_printer import AbstractPrinter

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.subroutine import Subroutine
from tealer.teal.instructions.instructions import Instruction, ExecutionMode
from tealer.exceptions import TealerException

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput

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


# disable pylint errors for now. errors should be resolved after completing refactoring.
class Teal:  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """Class to represent a teal contract.

    This class stores CFG, subroutines and other information of the
    contract. Also comes with easy api methods to run detectors, printers
    on the contract.

    Args:
        instructions: List of parsed instruction objects.
        bbs: List of basic blocks representing the Control Flow Graph(CFG)
            of the contract.
        version: Teal version this contract is written in.
        mode: Mode of the contract.
        subroutines: List of subroutines defined in the contract, will be
            empty for contracts written in Teal version 3 or less. Each
            subroutine is represented by the list of basic blocks part of
            that subroutine.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        version: int,
        mode: ExecutionMode,
        instructions: List[Instruction],
        bbs: List[BasicBlock],
        main: Subroutine,
        subroutines: Dict[str, Subroutine],
    ):
        self._version = version
        self._mode = mode
        self._int_constants: List[int] = []
        self._byte_constants: List[str] = []

        self._instructions = instructions
        self._bbs = bbs
        self._main = main
        self._subroutines = subroutines

        self._contract_name: str = ""
        self._detectors: List[AbstractDetector] = []
        self._printers: List[AbstractPrinter] = []

    @property
    def instructions(self) -> List[Instruction]:
        """List of instructions of the contract
        
        Returns:
            List of instructions of the contract
        """
        return self._instructions

    @property
    def bbs(self) -> List[BasicBlock]:
        """List of all basic blocks of the contract
        
        Returns:
            List of all basic blocks of the contract
        """
        return self._bbs

    @property
    def version(self) -> int:
        """Teal version for this contract.

        Version of the contract is based on whether the first instruction of the
        contract is #pragma version instruction or not. if it is, then version will
        be the teal version specified or else version will be 1.

        Returns:
            Returns the contract version.
        """

        return self._version

    @version.setter
    def version(self, ver: int) -> None:
        self._version = ver

    @property
    def mode(self) -> ExecutionMode:
        """Type of the contract: Stateless, Stateful or Any.

        Mode is determined based on the instructions of the contract. if there are
        any instructions that are only supported in one kind of contract then that
        will be the contract type. if there aren't any such type of instructions, then
        this will be "Any".

        Returns:
            Returns the execution mode this contract can be executed successfully.
        """

        return self._mode

    @mode.setter
    def mode(self, m: ExecutionMode) -> None:
        self._mode = m

    @property
    def main(self) -> "Subroutine":
        """Returns subroutine representing the contract entry-point
        
        Returns:
            Returns the subroutine object representing the non-subroutine blocks.
        """
        return self._main

    @property
    def subroutines(self) -> Dict[str, "Subroutine"]:
        """Returns dict of subroutine names and corresponding subroutine obj.
        
        Returns:
            Returns the subroutines in the contract. keys are the subroutine's name
            and the value is the subroutine.
        """
        return self._subroutines

    @property
    def subroutines_list(self) -> List["Subroutine"]:
        """Returns list of all contract's subroutines
        
        Returns:
            Returns the list of all subroutines in the contract.
        """
        return list(self._subroutines.values())

    @property
    def contract_name(self) -> str:
        return self._contract_name

    @contract_name.setter
    def contract_name(self, name: str) -> None:
        self._contract_name = name

    def subroutine(self, name: str) -> Optional["Subroutine"]:
        """Return subroutine with id/name `name`, return none if subroutine does not exist.
        
        Args:
            name: name of the subroutine.

        Returns:
            Returns the subroutine object given its name. Returns None if the subroutine is
            not in identified subroutines list.
        """
        return self._subroutines.get(name, None)

    def get_int_constant(self, index: int) -> Tuple[bool, int]:
        """Return int value stored by intcblock instruction

        Returns boolean and an int. Boolean indicates whether there's a value at that index
        and whether Tealer was able to identify that information.

        Cases:
            intcblock is only present in the entry block; Tealer is able to identify the confirmed and
            correct constants. As a result, Tealer can know the values of `intc_*` instructions.

            intcblock instruction occurs multiple times. Tealer cannot determine the exact value a `intc_`
            instruction refers to. This method returns `False` in this case.

            A `intc_*` instruction refers to a value that is not declared in the intcblock instruction. For example,
            intcblock only stores 3 values in the constant space and a intc instruction refers to 5th value. Execution
            will fail at runtime in this case. Return value will be `False` in this case as well.

        Args:
            index: The index into the int constants filled by the intcblock instruction.

        Returns:
            bool: True if Tealer was able to determine the value referred by that instruction or else False
            int: value referred by intc instruction at that index.
        """
        if len(self._int_constants) <= index:
            return False, 0
        return True, self._int_constants[index]

    def get_byte_constant(self, index: int) -> Tuple[bool, str]:
        """Return []byte value stored by bytecblock instruction

        Behavior is same as `get_int_constant`.

        Args:
            index: The index into the byte constants filled by the bytecblock instruction.

        Returns:
            bool: True if Tealer was able to determine the value referred by that instruction or else False
            int: value referred by bytec instruction at that index.
        """
        if len(self._byte_constants) <= index:
            return False, ""
        return True, self._byte_constants[index]

    def set_int_constants(self, int_constants: List[int]) -> None:
        self._int_constants = int_constants

    def set_byte_constants(self, byte_constants: List[str]) -> None:
        self._byte_constants = byte_constants

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

        instance = printer_class(self)
        self._printers.append(instance)

    # from slither: Slither Class in slither/slither.py
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

    # from slither: Slither Class in slither/slither.py
    def run_printers(self) -> List:
        """Run all the registered printers.

        Returns:
            List of results, each result corresponds to the output
            of a single printer.
        """

        return [p.print() for p in self._printers]
