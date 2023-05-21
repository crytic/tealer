"""Defines class to represent Teal contracts.

Teal class is used to store Control Flow Graph of the contract.
It comes with methods for running detectors, printers on the contract.
And also has properties for easy access of the parsed contract
information.

Classes:
    Teal: Class to represent a contract.
"""

from typing import List, TYPE_CHECKING, Tuple, Dict, Optional

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.subroutine import Subroutine
from tealer.teal.instructions.instructions import Instruction, ContractType

if TYPE_CHECKING:
    from tealer.teal.functions import Function


class Teal:
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
        mode: ContractType,
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
        self._functions: List["Function"] = []

        self._contract_name: str = ""

    @property
    def instructions(self) -> List[Instruction]:
        """List of instructions of the contract"""
        return self._instructions

    @property
    def bbs(self) -> List[BasicBlock]:
        """List of all basic blocks of the contract"""
        return self._bbs

    @property
    def version(self) -> int:
        """Teal version for this contract.

        Version of the contract is based on whether the first instruction of the
        contract is #pragma version instruction or not. if it is, then version will
        be the teal version specified or else version will be 1.
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
    def main(self) -> "Subroutine":
        "Returns subroutine representing the contract entry-point"
        return self._main

    @property
    def subroutines(self) -> Dict[str, "Subroutine"]:
        """Returns dict of subroutine names and corresponding subroutine obj."""
        return self._subroutines

    @property
    def subroutines_list(self) -> List["Subroutine"]:
        """Returns list of all contract's subroutines"""
        return list(self._subroutines.values())

    @property
    def contract_name(self) -> str:
        return self._contract_name

    @contract_name.setter
    def contract_name(self, name: str) -> None:
        self._contract_name = name

    @property
    def functions(self) -> List["Function"]:
        return self._functions

    @functions.setter
    def functions(self, functions: List["Function"]) -> None:
        self._functions = functions

    def subroutine(self, name: str) -> Optional["Subroutine"]:
        """Return subroutine with id/name `name`, return none if subroutine does not exist."""
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

        Returns:
            bool: True if Tealer was able to determine the value referred by that instruction or else False
            int: value referred by intc instruction at that index.
        """
        if len(self._int_constants) <= index:
            return False, 0
        return True, self._int_constants[index]

    def get_byte_constant(self, index: int) -> Tuple[bool, str]:
        """Return []byte value stored by bytecblock instruction"""
        if len(self._byte_constants) <= index:
            return False, ""
        return True, self._byte_constants[index]

    def set_int_constants(self, int_constants: List[int]) -> None:
        self._int_constants = int_constants

    def set_byte_constants(self, byte_constants: List[str]) -> None:
        self._byte_constants = byte_constants
