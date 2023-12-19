"""Defines a class to represent a Function in Teal contract.

Functions are different from subroutine. Functions are abstract blocks of code, each callable
by a end-user. Function represents an operation of the contract.

Classes:
    Function: Represents a Function.
"""

from typing import TYPE_CHECKING, List, Dict

from tealer.teal.context.block_transaction_context import BlockTransactionContext

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.teal import Teal
    from tealer.teal.subroutine import Subroutine


# pylint: disable=too-few-public-methods,too-many-instance-attributes
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
        # A subroutine is represented using a single CFG. A subroutine can be part of multiple
        # functions. Basic Blocks part of the subroutine CFG will be part of all functions the subroutine
        # is used in. But, block transaction context is specific for each function. As a result,
        # We cannot store the block transaction context in basic block object.
        self._transaction_contexts: Dict["BasicBlock", "BlockTransactionContext"] = {
            block: BlockTransactionContext() for block in self._blocks
        }
        # caller blocks of a subroutine depend on the function __main__ CFG. As a result, they
        # cannot be computed without considering the function.
        self._subroutine_caller_blocks: Dict["Subroutine", List["BasicBlock"]] = {
            sub: [] for sub in subroutines.values()
        }

        for block in self._blocks:
            if block.is_callsub_block:
                self._subroutine_caller_blocks[block.called_subroutine].append(block)

        self._subroutine_return_point_blocks: Dict["Subroutine", List["BasicBlock"]] = {}
        for sub, caller_blocks in self._subroutine_caller_blocks.items():
            self._subroutine_return_point_blocks[sub] = [
                bi.next[0] for bi in caller_blocks if len(bi.next) == 1
            ]

        # print(self._subroutine_caller_blocks)

        # TODO: add exit_blocks

    @property
    def blocks(self) -> List["BasicBlock"]:
        return self._blocks

    def transaction_context(self, block: "BasicBlock") -> "BlockTransactionContext":
        return self._transaction_contexts[block]

    def caller_blocks(self, subroutine: "Subroutine") -> List["BasicBlock"]:
        """BasicBlock with callsub instructions which call the subroutine.

        Args:
            subroutine: the subroutine

        Returns:
            List of caller callsub basic blocks. This blocks have "callsub {subroutine.name}"
            as exit instruction.
        """
        return self._subroutine_caller_blocks[subroutine]

    def return_point_blocks(self, subroutine: "Subroutine") -> List["BasicBlock"]:
        return self._subroutine_return_point_blocks[subroutine]
