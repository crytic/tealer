"""Defines a class to represent a Function in Teal contract.

Functions are different from subroutine. Functions are abstract blocks of code, each callable
by a end-user. Function represents an operation of the contract.

Classes:
    Function: Represents a Function.
"""

from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.teal import Teal
    from tealer.teal.subroutine import Subroutine


# pylint: disable=too-few-public-methods
class Function:
    """Class to represent a function in a contract."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        function_name: str,
        entry: "BasicBlock",
        blocks: List["BasicBlock"],
        contract: "Teal",
        main: "Subroutine",
        subroutines: Dict[str, "Subroutine"],
    ) -> None:
        self.function_name: str = function_name
        self.entry: "BasicBlock" = entry
        self._blocks: List["BasicBlock"] = blocks
        self.contract: "Teal" = contract
        self.main: "Subroutine" = main
        self.subroutines: Dict[str, "Subroutine"] = subroutines
        # TODO: add exit_blocks

    @property
    def blocks(self) -> List["BasicBlock"]:
        return self._blocks
