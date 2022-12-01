"""Defines generic class for dataflow analysis to find constraints on transaction fields.

Possible values for a field are considered to be a set, referred to as universal set `U` for that field.
if U is finite and small, values are enumerated and are stored in the context. However, in case U is large,
such as address type fields, enum type values are used to represent UniversalSet and NullSet.

For a given `key` and a `basic_block`, block_contexts[key][basic_block] are values(V), such that, if the transaction field represented by the `key`
is set to one of the values present in V, then:
    - The execution might reach the `basic_block`
    - The execution might successfully reach the end of the `basic_block`
    - The execution might reach a leaf basic block which results in successful completion of execution.

block_contexts is computed in three steps, each step making the information more precise.
1: In the first step, local information is considered. For each block, information inferred from the instructions present in the
    block is computed.
        - if the basic block contains instructions `assert(txn OnCompletion == int UpdateApplication)`, then block context of this block
        for transaction types will be equal to `{ApplUpdateApplication}`.
        - if basic block errors, contains `err` instruction or `return 0`, then block context will be NullSet.
        - if instructions in the block does not provide any information related to the field, then block context will be equal to
        UniversalSet (all possible values) for that key.
2: In the second step, information from the predecessors is considered. For this, forward dataflow analysis is used.
    This problem is analogous to reaching definitions problem:
        I   Each possible value is a definition that is defined at the start of execution i.e defined at the start of entry block.
        II  The definition(value) will reach start of the basic block, if it reaches the end of one of it's predecessors.
        III The definition(value) will reach the end of the block, if it is preserved by the basic block or it is defined in the basic block.
        IV  No definition(value) is defined in a basic block
        V   The definition(value) will reach start of the basic block, if the condition specific to reach this block is satisfied. Condition used
            to determine the branch taken can contain constraints related to the analysis. Developers can branch to error block or success block
            based on the transaction field value. Path based context is used to combine this information in forward analysis.

    Equations:
        initialization:
            RCHin(entry) = UniversalSet()  - from (I)
            RCHout(b) = NullSet() for all basic blocks b.
        fixed point iteration:
            RCHin(b) = union(intersection(RCHout(prev_b), path_context[b][prev_b]) for prev_b in predecessors) - from (II), (V)
            RCHout(b) = union(GEN(b), intersection(RCHin(b), PRSV(b)) - from (III)
            GEN(b) = NullSet() for all basic blocks b.
            RCHout(b) = intersection(RCHin(b), PRSV(b))

    `PRSV(b)` is `block_contexts` computed in the first step.
    Reverse postorder ordering is used for the iteration algorithm.

3: Finally, information from the successors is combined using backward dataflow analysis similar to Live-variable analysis.
    - `block_contexts` is equal to reach out information computed in the second step.
    - For leaf blocks, value is live if the value is preserved by the block.
    - For other blocks, the value is live, if the value is used(preserved) by one of the successors.
    equations:
        initialization:
            LIVEout(b) = NullSet() for all non-leaf blocks.
            LIVEout(b) = PRSV(b) for all leaf blocks.
        fixed point iteration:
            LIVEin(b) = union(LIVEou(succ_b) for succ_b in successors)
            LIVEout(b) = intersection(LIVEin(b), PRSV(b))

    `PRSV(b)` is `block_contexts` after the second step.
    Postorder ordering is used for the iteration algorithm.

Blocks containing `callsub` instruction and blocks which are right after the `callsub` instruction are
treated differently.
e.g
    main:           // Basic Block B1
        int 2
        retsub

    path_1:         // Basic Block B2
        txn OnCompletion
        int UpdateApplication
        ==
        assert
        callsub main

        byte "PATH_1"      // Basic Block B3
        int 1
        return

    path_2:                 // Basic Block B4
        txn OnCompletion
        int DeleteApplication
        ==
        assert
        callsub main

        byte "PATH_2"        // Basic Block B5
        int 1
        return

CFG:
                                  B2
                                  +--------------------------+
                                  |        4: path_1:        |
                                  |   5: txn OnCompletion    |
                                  | 6: int UpdateApplication |
                                  |          7: ==           |
                                  |        8: assert         |
                                  |     9: callsub main      |
                                  +--------------------------+
                                    |
                                    |
B4                                  v   B1                          B5
+---------------------------+     +--------------------------+     +-------------------+
|        13: path_2:        |     |                          |     |                   |
|   14: txn OnCompletion    |     |         1: main:         |     | 19: byte "PATH_2" |
| 15: int DeleteApplication |     |         2: int 2         |     |     20: int 1     |
|          16: ==           |     |        3: retsub         |     |    21: return     |
|        17: assert         |     |                          |     |                   |
|     18: callsub main      | --> |                          | --> |                   |
+---------------------------+     +--------------------------+     +-------------------+
                                    |
                                    |
                                    v   B3
                                  +--------------------------+
                                  |    10: byte "PATH_1"     |
                                  |        11: int 1         |
                                  |        12: return        |
                                  +--------------------------+

CFG will have edges:
    - B2 -> B1       # callsub instruction transfers the execution to called subroutine
    - B4 -> B1
    - B1 -> B3       # execution returns to the next instruction present after callsub instruction
    - B1 -> B5

B3 and B5 are return points of the subroutine.
B3 is only executed if execution reaches B2 => block_context for txn type is `{DeleteApplication}`.
similarly, B5 is only executed if execution reaches B4 => block_context for txn type is `{UpdateApplication}`.

block_contexts["TransactionType"][B1] = `{UpdateApplication, DeleteApplication}` # from B2 -> B1 and B4 -> B1.

B3 and B5 are return points and have only one predecessor(B1) in CFG. As a result, block_contexts will be
block_contexts["TransactionType"][B4] = `{UpdateApplication, DeleteApplication}`
block_contexts["TransactionType"][B5] = `{UpdateApplication, DeleteApplication}`.

This is because, when traversing the CFG without differentiating subroutine blocks and others, possible execution paths will be:
1. B2 -> B1 -> B3
2. B4 -> B1 -> B5
3. B2 -> B1 -> B5  # won't be possible at runtime.
4. B4 -> B1 -> B3  # won't be possible at runtime.

However, At runtime, execution will reach B3 if and only if it reaches B2, same for B5 and B3. Using this reasoning while
combining information from predecessors and successors will give more accurate results.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Set

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
        # entry block of CFG
        self._entry_block: "BasicBlock" = teal.bbs[
            0
        ]  # blocks are ordered by entry instruction in parsing stage.
        # self._block_contexts[KEY][B] -> block_context of KEY for block B
        self._block_contexts: Dict[str, Dict["BasicBlock", Any]] = {}
        # self._path_contexts[KEY][Bi][Bj] -> path_context of KEY for path Bj -> Bi
        self._path_contexts: Dict[str, Dict["BasicBlock", Dict["BasicBlock", Any]]] = {}
        self._reachout: Dict[str, Dict["BasicBlock", Any]] = {}  # used for forward analysis
        self._liveout: Dict[str, Dict["BasicBlock", Any]] = {}  # used for backward analysis
        if not self.KEYS:
            raise IncorrectDataflowTransactionContextInitialization(
                f"KEYS are not initialized {self.__class__.__name__}"
            )

    def _gtx_key(self, idx: int, key: str) -> str:  # pylint: disable=no-self-use
        """return key used for tracking context of gtxn {idx} {field represented by key}"""
        return f"GTXN_{idx:02d}_{key}"

    @abstractmethod
    def _universal_set(self, key: str) -> Any:
        """Return universal set for the field corresponding to given key"""

    @abstractmethod
    def _null_set(self, key: str) -> Any:
        """Return null set for the field corresponding to given key"""

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

    def _calculate_reachin(self, key: str, block: "BasicBlock") -> Any:
        if block == self._entry_block:
            # We are considering each possible value as a definition defined at the start of entry block.
            reachin_information = self._universal_set(key)
        else:
            reachin_information = self._null_set(key)

        reachout = self._reachout[key]
        path_context = self._path_contexts[key]
        for prev_b in block.prev:
            reachin_information = self._union(
                key,
                reachin_information,
                self._intersection(key, reachout[prev_b], path_context[block][prev_b]),
            )

        if block.callsub_block is not None:
            # this block is the return point for callsub instruction present in `block.callsub_block`
            # execution will only reach this block, if it reaches `block.callsub_block`
            reachin_information = self._intersection(
                key, reachin_information, reachout[block.callsub_block]
            )

        return reachin_information

    def _calculate_livein(self, key: str, block: "BasicBlock") -> Any:
        liveout = self._liveout[key]
        livein_information = self._null_set(key)

        for next_b in block.next:
            livein_information = self._union(key, livein_information, liveout[next_b])

        if block.sub_return_point is not None:
            # this block is the `callsub block` and `block.sub_return_point` is the block that will be executed after subroutine.
            livein_information = self._intersection(
                key, livein_information, liveout[block.sub_return_point]
            )
        return livein_information

    def _merge_information_forward(self, block: "BasicBlock") -> bool:
        updated = False
        for key in self.KEYS:
            # RCHout(b) = intersection(RCHin(b), PRSV(b))
            new_reachout = self._intersection(
                key, self._calculate_reachin(key, block), self._block_contexts[key][block]
            )
            if new_reachout != self._reachout[key][block]:
                self._reachout[key][block] = new_reachout
                updated = True
        return updated

    def _merge_information_backward(self, block: "BasicBlock") -> bool:
        if len(block.next) == 0:  # leaf block
            return False

        updated = False
        for key in self.KEYS:
            new_liveout = self._intersection(
                key, self._calculate_livein(key, block), self._block_contexts[key][block]
            )
            if new_liveout != self._liveout[key][block]:
                self._liveout[key][block] = new_liveout
                updated = True
        return updated

    @staticmethod
    def _postorder(entry: "BasicBlock") -> List["BasicBlock"]:
        visited: Set["BasicBlock"] = set()
        order: List["BasicBlock"] = []

        def dfs(block: "BasicBlock") -> None:
            visited.add(block)
            for successor in block.next:
                if not successor in visited:
                    dfs(successor)
            order.append(block)

        dfs(entry)
        return order

    def run_analysis(self) -> None:  # pylint: disable=too-many-branches
        """Run analysis"""
        # step 1
        for block in self._teal.bbs:
            self._block_level_constraints(block)
            self._path_level_constraints(block)

        # step 2 initialization
        for key in self.KEYS:
            self._reachout[key] = {}
            for b in self._teal.bbs:
                self._reachout[key][b] = self._null_set(key)

        postorder = self._postorder(self._entry_block)
        worklist = postorder[::-1]  # Reverse postorder

        while worklist:
            b = worklist[0]
            worklist = worklist[1:]
            updated = self._merge_information_forward(b)

            if updated:
                return_point_block = [b.sub_return_point] if b.sub_return_point is not None else []
                for bi in b.next + return_point_block:
                    if bi not in worklist:
                        worklist.append(bi)

        # step 3
        self._block_contexts = self._reachout
        for key in self.KEYS:
            self._liveout[key] = {}
            for b in self._teal.bbs:
                if len(b.next) == 0:  # leaf block
                    self._liveout[key][b] = self._block_contexts[key][b]
                else:
                    self._liveout[key][b] = self._null_set(key)

        worklist = [b for b in postorder if len(b.next) != 0]

        while worklist:
            b = worklist[0]
            worklist = worklist[1:]
            updated = self._merge_information_backward(b)

            if updated:
                callsub_block = [b.callsub_block] if b.callsub_block is not None else []
                for bi in b.prev + callsub_block:
                    if bi not in worklist:
                        worklist.append(bi)

        self._block_contexts = self._liveout
        self._store_results()