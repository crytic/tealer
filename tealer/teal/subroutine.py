from typing import TYPE_CHECKING, List, Optional

from tealer.exceptions import TealerException
from tealer.teal.instructions.instructions import Retsub

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.teal import Teal


class Subroutine:
    """Represent a Teal subroutine.

    Main entry point code, code that is not part of any subroutine, is represented as a separate subroutine.
    """

    def __init__(self, name: str, entry: "BasicBlock", blocks: List["BasicBlock"]) -> None:
        self._name = name
        self._entry = entry
        self._blocks = blocks
        self._exit_blocks = [
            b for b in blocks if len(b.next) == 0 or isinstance(b.exit_instr, Retsub)
        ]
        self._contract: Optional["Teal"] = None

    @property
    def name(self) -> str:
        """Name of the subroutine"""
        return self._name

    @property
    def entry(self) -> "BasicBlock":
        """Entry block of the subroutine"""
        return self._entry

    @property
    def exit_blocks(self) -> List["BasicBlock"]:
        """Exit blocks of the subroutine."""
        return self._exit_blocks

    @property
    def blocks(self) -> List["BasicBlock"]:
        """List of all basic blocks of the subroutine"""
        return self._blocks

    @property
    def contract(self) -> "Teal":
        """The Teal contract this subroutine is a part of"""
        if self._contract is None:
            raise TealerException(f"Contract of subroutine {self._name} is not set")
        return self._contract

    @contract.setter
    def contract(self, contract_obj: "Teal") -> None:
        self._contract = contract_obj
