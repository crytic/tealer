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


class Function:
    """Class to represent a function in a contract."""

    def __init__(
        self, function_name: str, entry: "BasicBlock", cfg: List["BasicBlock"], contract: "Teal"
    ) -> None:
        self.function_name: str = function_name
        self.entry: "BasicBlock" = entry
        self.cfg: List["BasicBlock"] = []
        self.contract: "Teal" = contract
        # TODO: add exit_blocks

    @property
    def subroutines(self) -> Dict[str, "Subroutine"]:
        return self.contract.subroutines
