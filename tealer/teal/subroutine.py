from typing import TYPE_CHECKING, List, Optional

from tealer.exceptions import TealerException
from tealer.teal.instructions.instructions import Retsub

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.teal import Teal


class Subroutine:  # pylint: disable=too-many-instance-attributes
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
        self._caller_callsub_blocks: List["BasicBlock"] = []
        self._return_point_blocks: List["BasicBlock"] = []

    @property
    def name(self) -> str:
        """Name of the subroutine

        Returns:
            Returns the name of the subroutine. The name of the CFG with non-subroutine blocks is "__main__"
        """
        return self._name

    @property
    def entry(self) -> "BasicBlock":
        """Entry block of the subroutine.

        Returns:
            entry block of the subroutine.
        """
        return self._entry

    @property
    def exit_blocks(self) -> List["BasicBlock"]:
        """Exit blocks of the subroutine.

        Returns:
            Returns the exit blocks of the subroutine. Exit blocks include blocks which return from the subroutine(retsub)
            and also blocks which exit from the contract.
        """
        return self._exit_blocks

    @property
    def blocks(self) -> List["BasicBlock"]:
        """List of all basic blocks of the subroutine.

        Returns:
            Returns list of all basic blocks that are part of this subroutine.
        """
        return self._blocks

    @property
    def contract(self) -> "Teal":
        """The Teal contract this subroutine is a part of

        Returns:
            Returns the contract.

        Raises:
            TealerException: Raises error if contract is not set during parsing.
        """
        if self._contract is None:
            raise TealerException(f"Contract of subroutine {self._name} is not set")
        return self._contract

    @contract.setter
    def contract(self, contract_obj: "Teal") -> None:
        self._contract = contract_obj

    @property
    def caller_blocks(self) -> List["BasicBlock"]:
        """BasicBlock with callsub instructions which call this subroutine.

        Returns:
            List of caller callsub basic blocks. This blocks have "callsub {self.name}"
            as exit instruction.
        """
        return self._caller_callsub_blocks

    @caller_blocks.setter
    def caller_blocks(self, caller_callsub_blocks: List["BasicBlock"]) -> None:
        """Set caller_blocks and return point blocks

        Args:
            caller_callsub_blocks: basic blocks with callsub instruction calling this subroutine.
        """
        self._caller_callsub_blocks = caller_callsub_blocks
        self._return_point_blocks = [
            bi.next[0] for bi in caller_callsub_blocks if len(bi.next) == 1
        ]

    @property
    def return_point_blocks(self) -> List["BasicBlock"]:
        return self._return_point_blocks

    @property
    def retsub_blocks(self) -> List["BasicBlock"]:
        """List of basic blocks of the subroutine containing `Retsub`.

        Returns:
            Returns the list of retsub blocks. This blocks return the execution from the
            subroutine to the caller.
        """
        return [b for b in self._exit_blocks if isinstance(b.exit_instr, Retsub)]

    @property
    def called_subroutines(self) -> List["Subroutine"]:
        """List of subroutines called by this subroutine.

        Returns:
            Returns a list of subroutines called by the subroutine.
        """
        return list(set(bi.called_subroutine for bi in self._blocks if bi.is_callsub_block))
