"""Defines generic class for dataflow analysis to find constraints on transaction fields.

Possible values for a field are considered to be a set, referred to as universal set(U) for that field.
if U is finite and small, values are enumerated and are stored in the context. However, in case U is large
for example, address type fields have very large set, Enum type values are used to represent U and NullSet.

Algorithm works as:
 - Collect constraints asserted within the block and constraints specific for each path, happens if bz/bnz are
    directly used on the constraint.
 - Use fix point algorithm and repeatedly merge information until no new information is found

Equation for merging:
        # path_transaction_context[b][bi] gives the transaction constraints for path bi -> b
        block_transaction_context[b] = Union((block_transaction_context[bi] & path_transaction_context[b][bi]) for bi in predecessors[b]) \
                            & block_transaction_context[b] \
                            & Union(block_transaction_context[bi] for bi in successors[b])
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

from tealer.teal.instructions.instructions import (
    Assert,
    Return,
    BZ,
    BNZ,
    Err,
)

from tealer.utils.analyses import is_int_push_ins

if TYPE_CHECKING:
    from tealer.teal.teal import Teal
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.instructions.instructions import Instruction


class IncorrectDataflowTransactionContextInitialization(Exception):
    pass


class DataflowTransactionContext(ABC):  # pylint: disable=too-few-public-methods

    # List of keys, unique and separate context is stored for each key.
    KEYS: List[str] = []

    def __init__(self, teal: "Teal"):
        self._teal: "Teal" = teal
        # self._block_contexts[KEY][B] -> block_context of KEY for block B
        self._block_contexts: Dict[str, Dict["BasicBlock", Any]] = {}
        # self._path_contexts[KEY][Bi][Bj] -> path_context of KEY for path Bj -> Bi
        self._path_contexts: Dict[str, Dict["BasicBlock", Dict["BasicBlock", Any]]] = {}
        if not self.KEYS:
            raise IncorrectDataflowTransactionContextInitialization(
                f"KEYS are not initialized {self.__class__.__name__}"
            )

    def _gtx_key(self, idx: int, key: str) -> str:  # pylint: disable=no-self-use
        """return key used for tracking context of gtxn {idx} {field represented by key}"""
        return f"GTXN_{idx:02d}_{key}"

    @abstractmethod
    def _universal_set(self, key: str) -> Any:
        """Return universal set of the field corresponding to given key"""

    @abstractmethod
    def _null_set(self, key: str) -> Any:
        """Return null set of the field corresponding to given key"""

    @abstractmethod
    def _union(self, key: str, a: Any, b: Any) -> Any:
        """return union of a and b, where a, b represent values for the given key"""

    @abstractmethod
    def _intersection(self, key: str, a: Any, b: Any) -> Any:
        """return intersection of a and b, where a, b represent values for the given key"""

    @abstractmethod
    def _get_asserted(self, key: str, ins_stack: List["Instruction"]) -> Tuple[Any, Any]:
        """For the given key and ins_stack, return true_values and false_values

        true_values for a key are considered to be values which result in non-zero value on
        top of the stack.
        false_values for a key are considered to be values which result in zero value on top
        of the stack.
        """

    @abstractmethod
    def _store_results(self) -> None:
        """Store the collected information in the context object of each block"""

    def _block_level_constraints(self, block: "BasicBlock") -> None:
        """Calculate and store constraints on keys applied within the block.

        By default, no constraints are considered i.e values are assumed to be universal_set
        if block contains `Err` or `Return 0`, values are set to null set.

        if block contains assert instruction, values are further constrained using the comparison being
        asserted. Values are stored in self._block_contexts
        self._block_contexts[KEY][B] -> block_context of KEY for block B
        """
        for key in self.KEYS:
            if key not in self._block_contexts:
                self._block_contexts[key] = {}
            self._block_contexts[key][block] = self._universal_set(key)

        stack: List["Instruction"] = []
        for ins in block.instructions:
            if isinstance(ins, Assert):
                for key in self.KEYS:
                    asserted_values, _ = self._get_asserted(key, stack)
                    present_values = self._block_contexts[key][block]
                    self._block_contexts[key][block] = self._intersection(
                        key, present_values, asserted_values
                    )

            # if return 0, set possible values to NullSet()
            if isinstance(ins, Return):
                if len(ins.prev) == 1:
                    is_int, value = is_int_push_ins(ins.prev[0])
                    if is_int and value == 0:
                        for key in self.KEYS:
                            self._block_contexts[key][block] = self._null_set(key)

            if isinstance(ins, Err):
                for key in self.KEYS:
                    self._block_contexts[key][block] = self._null_set(key)

            stack.append(ins)

    def _path_level_constraints(self, block: "BasicBlock") -> None:
        """Calculate and store constraints on keys applied along each path.

        By default, no constraints are considered i.e values are assumed to be universal_set

        if block contains bz/bnz instruction, possible values are calculated for each branch and
        are stored in self._path_contexts
        self._path_contexts[KEY][Bi][Bj] -> path_context of KEY for path Bj -> Bi
        """

        for key in self.KEYS:
            if key not in self._path_contexts:
                self._path_contexts[key] = {}
            path_context = self._path_contexts[key]
            for b in block.next:
                # path_context[bi][bj]: path context of path bj -> bi, bi is the successor
                if b not in path_context:
                    path_context[b] = {}
                # if there are no constraints, set the possible values to universal set
                path_context[b][block] = self._universal_set(key)

        if isinstance(block.exit_instr, (BZ, BNZ)):
            for key in self.KEYS:
                # true_values: possible values for {key} which result in non-zero value on top of the stack
                # false_values: possible values for {key} which result in zero value on top of the stack
                # if the check is not related to the field, true_values and false_values will be universal sets
                true_values, false_values = self._get_asserted(key, block.instructions[:-1])

                if len(block.next) == 1:
                    # happens when bz/bnz is the last instruction in the contract and there is no default branch
                    default_branch = None
                    jump_branch = block.next[0]
                else:
                    default_branch = block.next[0]
                    jump_branch = block.next[1]

                if isinstance(block.exit_instr, BZ):
                    # jump branch is taken if the comparison is false i.e not in asserted values
                    self._path_contexts[key][jump_branch][block] = false_values
                    # default branch is taken if the comparison is true i.e in asserted values
                    if default_branch is not None:
                        self._path_contexts[key][default_branch][block] = true_values
                elif isinstance(block.exit_instr, BNZ):
                    # jump branch is taken if the comparison is true i.e in asserted values
                    self._path_contexts[key][jump_branch][block] = true_values
                    # default branch is taken if the comparison is false i.e not in asserted values
                    if default_branch is not None:
                        self._path_contexts[key][default_branch][block] = false_values

    def _merge_information(self, block: "BasicBlock") -> bool:
        """Merge information for predecessors, successors for the :block: and return whether information is updated or not

        # path_transaction_context[b][bi] gives the transaction constraints for path bi -> b
        block_transaction_context[b] = Union((block_transaction_context[bi] & path_transaction_context[b][bi]) for bi in predecessors[b]) \
                            & block_transaction_context[b] \
                            & Union(block_transaction_context[bi] for bi in successors[b])
        """

        updated = False
        for key in self.KEYS:
            block_context = self._block_contexts[key]
            path_context = self._path_contexts[key]

            new_block_context = self._union(key, block_context[block], block_context[block])

            if len(block.prev) != 0:
                prev_b = block.prev[0]
                # TODO: While considering predecessor information, use dominator block information instead of
                # all predecessors. Current approach doesn't consider constraints applied within the loop body
                # blocks for the blocks outside the loop. Or use reverse postorder while constructing the block contexts(?)
                predecessor_information = self._intersection(
                    key, block_context[prev_b], path_context[block][prev_b]
                )
                for prev_b in block.prev[1:]:
                    predecessor_information = self._union(
                        key,
                        predecessor_information,
                        self._intersection(key, block_context[prev_b], path_context[block][prev_b]),
                    )

                new_block_context = self._intersection(
                    key, predecessor_information, new_block_context
                )

            if len(block.next) != 0:
                next_b = block.next[0]
                successor_information = block_context[next_b]
                for next_b in block.next[1:]:
                    successor_information = self._union(
                        key, successor_information, block_context[next_b]
                    )

                new_block_context = self._intersection(
                    key, successor_information, new_block_context
                )

            if new_block_context != block_context[block]:
                block_context[block] = new_block_context
                updated = True
        return updated

    def run_analysis(self) -> None:
        """Run analysis"""
        # phase 1
        for block in self._teal.bbs:
            self._block_level_constraints(block)
            self._path_level_constraints(block)

        # phase 2
        worklist = list(self._teal.bbs)

        while worklist:
            b = worklist[0]
            worklist = worklist[1:]
            updated = self._merge_information(b)

            if updated:
                for bi in b.prev + b.next:
                    if bi not in worklist:
                        worklist.append(bi)

            print([b.idx for b in worklist])
        self._store_results()
