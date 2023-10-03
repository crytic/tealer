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

---------------------------------------------------------------------------

`DataflowTransactionContext._get_asserted_single(key, ins_stack_value)` returns a Tuple of true_values and false_values.
    true_values: Given that the result of `ins_stack_value` is NON-ZERO, what are the possible
                values for the key.
    false_values: Given that the result of `ins_stack_value` is ZERO, what are the possible values
                for the key.

`_get_asserted_single` uses pattern matching to identify comparisons on interested fields. It only works when the
`ins_stack_value` directly represents the value of the comparison.
e.g
    - Eq(txn RekeyTo, global Zeroaddress)
    - Neq(txn OnCompletion, int UpdateApplication)
    - ...

But when the result depends on multiple equations it is NOT possible to use the same kind of pattern matching and derive
possible values.
e.g
ins_stack_value =   Or(
                        And(
                            Eq(txn RekeyTo, global ZeroAddress),
                            Eq(txn CloseRemainderTo, global ZeroAddress),
                        ),
                        And(
                            Eq(txn Fee, global MinTxnFee),
                            Eq(txn AssetCloseTo, global ZeroAddress),
                        ),
                    )


We can combine information from multiple equations when they are connected using And, Or, !.
e.g
    txn RekeyTo
    global ZeroAddress
    ==                      // equation <1>
    txn CloseRemainderTo
    global ZeroAddress
    ==                      // <2>
    &&
    txn Fee
    global MinTxnFee
    <=                      // <3>
    &&

=> And(
    And(
        Eq(txn RekeyTo, global ZeroAddress),
        Eq(txn CloseRemainderTo, global ZeroAddress),
    ),
    LessE(txn Fee, global MinTxnFee),
)

=> And(And(<1>, <2>), <3>)
=> ins_stack_value = And(<1>, <2>, <3>)           // flattend

if it is given that ins_stack_value is False, Then atleast ONE of the equations <1>, <2> or <3> is False.
if it is given that ins_stack_value is True, Then ALL of the equations <1>, <2> and <3> are True.

This applies for any number of equations: And(<1>, <2>, <3>, <4>, ....)

-> if the ins_stack_value is of form And(<1>, <2>, <3>, <4>, ....) and is `True`, Then we can combine possible values
from multiple equations using set `Intersection`.
-> if the ins_stack_value is of form And(<1>, <2>, <3>, <4>, ....) and is `False`, Then we can combine possible values
from multiple equations using set `Union`.

if any of equation in And(<1>, ...) is UnknownStackValue then `false_values` for And(...) is universal_set U.
    -> The result of And() could be false because the UnknownStackValue is False. None of the known values have
        to be False.
    -> true_values are not affected by having an UnknownStackValue. All the known values have to be True irrespective
        of unknown values for the result to be True.

Similar reasoning can be done for Or(<1>, <2>, <3>, <4>, ....)

if ins_stack_value is True, Then atleast ONE of the equations <1>, <2>, <3>, ... is True.   (Union)
if ins_stack_value is False, Then ALL of the equations <1>, <2>, <3>, ... are False.        (Intersection)

if any of equation in Or(<1>, ...) is UnknownStackValue then `true_values` for Or(...) is universal_set U.
    -> The result of Or() could be True because the UnknownStackValue is True. None of the known values have
        to be True.
    -> false_values are not affected by having an UnknownStackValue. All the known values have to be False irrespective
        of unknown values for the result to be False
"""


from abc import ABC, abstractmethod
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Set
from collections import defaultdict

from tealer.analyses.dataflow.transaction_context.utils.key_helpers import (
    get_gtxn_at_index_key,
    get_absolute_index_key,
    get_relative_index_key,
)
from tealer.teal.instructions.instructions import (
    Assert,
    Return,
    BZ,
    BNZ,
    Err,
    And,
    Or,
    Not,
    TealerCustomErrInstruction,
)
from tealer.utils.analyses import (
    is_int_push_ins,
    prev_blocks_global,
    next_blocks_global,
    leaf_block_global,
)
from tealer.utils.algorand_constants import MAX_GROUP_SIZE
from tealer.analyses.utils.stack_ast_builder import (
    KnownStackValue,
    UnknownStackValue,
    get_stack_value_for_ins,
    compute_equations,
)

if TYPE_CHECKING:
    from tealer.teal.teal import Teal
    from tealer.teal.functions import Function
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.instructions.instructions import Instruction


class IncorrectDataflowTransactionContextInitialization(Exception):
    pass


logger_txn_ctx = logging.getLogger("TransactionCtxAnalysis")
logging.basicConfig(level=logging.DEBUG)

debug_keys = ["TransactionType"]


class DataflowTransactionContext(ABC):  # pylint: disable=too-few-public-methods

    # List of keys, unique and separate context is stored for each key.
    # each key represents a transaction field.
    BASE_KEYS: List[str] = []
    # BASE_KEYS for which transaction context information from `gtxn {i} {field}` is also stored.
    KEYS_WITH_GTXN: List[str] = []  # every key in this list should also present in BASE_KEYS.

    def __init__(self, function: "Function"):
        # self._teal: "Teal" = teal
        self._function: "Function" = function
        # entry block of CFG
        self._entry_block: "BasicBlock" = function.entry
        # self._block_contexts[KEY][B] -> block_context of KEY for block B
        self._block_contexts: Dict[str, Dict["BasicBlock", Any]] = defaultdict(dict)
        # self._path_contexts[KEY][Bi][Bj] -> path_context of KEY for path Bj -> Bi
        self._path_contexts: Dict[str, Dict["BasicBlock", Dict["BasicBlock", Any]]] = defaultdict(
            dict
        )
        if not self.BASE_KEYS:
            raise IncorrectDataflowTransactionContextInitialization(
                f"BASE_KEYS are not initialized {self.__class__.__name__}"
            )

    @abstractmethod
    def _universal_set(self, key: str) -> Any:
        """Return universal set for the field corresponding to given key

        Args:
            key: The key used to represent values of a field in the analysis.

        Returns:
            Returns the universal set: list of all possible values for the field tracked by the
            :key:
        """

    @abstractmethod
    def _null_set(self, key: str) -> Any:
        """Return null set for the field corresponding to given key

        Args:
            key: The key used to represent values of a field in the analysis.

        Returns:
            Returns the null set: empty value for the field tracked by the :key:
        """

    @abstractmethod
    def _union(self, key: str, a: Any, b: Any) -> Any:
        """return union of a and b, where a, b represent values for the given key

        Args:
            key: The analysis key. The values in set :a: and :b: are values of this key.
            a: Set 1.
            b: Set 2.

        Returns:
            Returns union of set a and b.
        """

    @abstractmethod
    def _intersection(self, key: str, a: Any, b: Any) -> Any:
        """return intersection of a and b, where a, b represent values for the given key

        Args:
            key: The analysis key. The values in set :a: and :b: are values of this key.
            a: Set 1.
            b: Set 2.

        Returns:
            Returns union of set a and b.
        """

    @abstractmethod
    def _get_asserted_single(self, key: str, ins_stack_value: KnownStackValue) -> Tuple[Any, Any]:
        """For the given key and ins_stack, return true_values and false_values

        true_values: Given that the result of `ins_stack_value` is NON-ZERO, what are the possible
            values for the key.
        false_values: Given that the result of `ins_stack_value` is ZERO, what are the possible values
            for the key.

        Args:
            key: The key used to represent values of a field in the analysis.
            ins_stack_value: The stack value being considered for assertion. The :ins_stack_value: is
                not the result of "And" or "Or" or "Not" instructions.

        Returns:
            Returns the "true_values" and "false_values" for the key.
        """

    @abstractmethod
    def _store_results(self) -> None:
        """Store the collected information in the context object of each block"""

    def _get_asserted(self, key: str, ins_stack_value: KnownStackValue) -> Tuple[Any, Any]:
        """For the given key and ins_stack_value, return true_values and false_values

        true_values: Given that the result of `ins_stack_value` is NON-ZERO, what are the possible
            values for the key.
        false_values: Given that the result of `ins_stack_value` is ZERO, what are the possible values
            for the key.

        Args:
            key: The key used to represent values of a field in the analysis.
            ins_stack_value: The stack value being considered for assertion.

        Returns:
            Returns the "true_values" and "false_values" for the key.
        """
        if not isinstance(ins_stack_value.instruction, (And, Or, Not)):
            # and not isinstance(ins_stack_value.instruction, Or):
            # single equation
            t, f = self._get_asserted_single(key, ins_stack_value)
            return t, f
        if isinstance(ins_stack_value.instruction, Not):
            arg = ins_stack_value.args[0]
            if isinstance(arg, UnknownStackValue):
                # unknown value
                return self._universal_set(key), self._universal_set(key)
            true_values, false_values = self._get_asserted(key, arg)
            # swap the values
            final_true_values, final_false_values = false_values, true_values
            return final_true_values, final_false_values
        if isinstance(ins_stack_value.instruction, And):
            # x = And(<1>, <2>, <3>, ...),
            #   if x is True then <1>, <2>, ... are all True, Intersection
            #   if x is False then one of <1>, <2>, ... is False, Union
            individual_equations, has_unknown_value = compute_equations(ins_stack_value, And)
            final_true_values = self._universal_set(key)
            final_false_values = self._null_set(key)
            for equation in individual_equations:
                # combine values recursively.
                # And(<Eq()>, <Or()>, <Or()>, ...):
                #      values Or() cannot be calculated using _get_asserted_single
                true_values, false_values = self._get_asserted(key, equation)
                final_true_values = self._intersection(key, final_true_values, true_values)
                final_false_values = self._union(key, final_false_values, false_values)
            if has_unknown_value:
                # has_unknown_value is True if result of And depends on an unknown value.
                # if And is False, the unknown value could be false and that unknown value
                # might or might not depend on the key.
                # note: Having a unknown value does not affect true_values, known values have
                # to be True irrespective of unknown value for the result to be True
                final_false_values = self._universal_set(key)
            return final_true_values, final_false_values
        # x = Or(<1>, <2>, <3>, ....),
        #   if x is False then <1>, <2>, ... are all False,     Intersection
        #   if x is True then one of <1>, <2>, ... is True,     Union
        individual_equations, has_unknown_value = compute_equations(ins_stack_value, Or)
        final_false_values = self._universal_set(key)
        final_true_values = self._null_set(key)
        for equation in individual_equations:
            true_values, false_values = self._get_asserted(key, equation)
            final_false_values = self._intersection(key, final_false_values, false_values)
            final_true_values = self._union(key, final_true_values, true_values)
        if has_unknown_value:
            # has_unknown_value is True if result of Or depends on an unknown value.
            # if Or is True, the unknown value could be True and that unknown value
            # might or might not depend on the key
            # note: Having a unknown value does not affect false_values, known values have
            # to be False irrespective of unknown value for the result to be False
            final_true_values = self._universal_set(key)
        return final_true_values, final_false_values

    def _block_level_constraints(  # pylint: disable=too-many-branches
        self, analysis_keys: List[str], block: "BasicBlock"
    ) -> None:
        """Calculate and store constraints on keys applied within the block.

        By default, no constraints are considered i.e values are assumed to be universal_set
        if block contains `Err` or `Return 0`, values are set to null set.

        if block contains assert instruction, values are further constrained using the comparison being
        asserted. Values are stored in self._block_contexts
        self._block_contexts[KEY][B] -> block_context of KEY for block B

        Args:
            analysis_keys: List of keys, each representing a field.
            block: The basic block.

        Fills the _block_contexts[:key:][:block:] based on assertions performed by the instructions in the
        :block:
        """
        for key in analysis_keys:
            self._block_contexts[key][block] = self._universal_set(key)

        for ins in block.instructions:
            if isinstance(ins, Assert):
                assert_ins_stack_value = get_stack_value_for_ins(ins)
                assert_ins_arg = assert_ins_stack_value.args[0]
                if isinstance(assert_ins_arg, UnknownStackValue):
                    continue
                for key in analysis_keys:
                    # asserted_values, _ = self._get_asserted(key, stack)
                    asserted_values, _ = self._get_asserted(key, assert_ins_arg)
                    present_values = self._block_contexts[key][block]
                    self._block_contexts[key][block] = self._intersection(
                        key, present_values, asserted_values
                    )
            elif isinstance(ins, Return):
                # if return 0, set possible values to NullSet()
                return_ins_value = get_stack_value_for_ins(ins)
                return_ins_arg = return_ins_value.args[0]
                if isinstance(return_ins_arg, UnknownStackValue):
                    continue
                # if int 0; return; set possible values to null set.
                is_int, value = is_int_push_ins(return_ins_arg.instruction)
                if is_int and value == 0:
                    for key in analysis_keys:
                        self._block_contexts[key][block] = self._null_set(key)
                    continue
                # if And(<1>, <2>, ..); return; i.e return value depends on the result of a comparison
                for key in analysis_keys:
                    true_values, _ = self._get_asserted(key, return_ins_arg)
                    present_values = self._block_contexts[key][block]
                    self._block_contexts[key][block] = self._intersection(
                        key, present_values, true_values
                    )
            elif isinstance(ins, (Err, TealerCustomErrInstruction)):
                # if err, set possible values to NullSet()
                for key in analysis_keys:
                    self._block_contexts[key][block] = self._null_set(key)

    def _path_level_constraints(  # pylint: disable=too-many-branches
        self, analysis_keys: List[str], block: "BasicBlock"
    ) -> None:
        """Calculate and store constraints on keys applied along each path.

        By default, no constraints are considered i.e values are assumed to be universal_set

        if block contains bz/bnz instruction, possible values are calculated for each branch and
        are stored in self._path_contexts
        self._path_contexts[KEY][Bi][Bj] -> path_context of KEY for path Bj -> Bi

        Args:
            analysis_keys: List of keys, each representing a field.
            block: The basic block.

        Fills the _path_contexts[key][Bj][Bi] where :key: is the key in analysis_keys and
        Bi is the :block: and Bj are next blocks of :block: in the global CFG.
        """

        for key in analysis_keys:
            path_context = self._path_contexts[key]
            for b in next_blocks_global(self._function, block):
                # print(
                #     f"block: {repr(block)}, b: {repr(b)}, {key:}, block: {block.__hash__()}, b: {b.__hash__()}, block sub: {block.subroutine.name}, b sub: {b.subroutine.name}"
                # )
                # path_context[bi][bj]: path context of path bj -> bi, bi is the successor
                if b not in path_context:
                    path_context[b] = {}
                    # print(f"block: {repr(block)}, b: {repr(b)}, {key:}, ddd")

                # if there are no constraints, set the possible values to universal set
                path_context[b][block] = self._universal_set(key)

        if isinstance(block.exit_instr, (BZ, BNZ)):
            exit_ins_stack_value = get_stack_value_for_ins(block.exit_instr)
            exit_ins_arg = exit_ins_stack_value.args[0]
            if isinstance(exit_ins_arg, UnknownStackValue):
                return
            for key in analysis_keys:
                # true_values: possible values for {key} which result in non-zero value on top of the stack
                # false_values: possible values for {key} which result in zero value on top of the stack
                # if the check is not related to the field, true_values and false_values will be universal sets
                true_values, false_values = self._get_asserted(key, exit_ins_arg)

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

    def _update_gtxn_constraints(self, keys_with_gtxn: List[str], block: "BasicBlock") -> None:
        """Use information from txn constraints on gtxn_

        `block.transaction_context.group_indices` will contain indices the `txn` can have.

        The values of each key represent possible values for that field. Values of `GTXN_0_RekeyTo` are
        possible values for `gtxn 0 RekeyTo` i.e possible `RekeyTo` field values of transaction present at index 0.

        self._block_contexts[f"GTXN_{idx}_{key}"] stores the information collected from
        instructions `gtxn {idx} {field}`. This information represents validations performed
        on the `txn {field}` by accessing it through `gtxn {idx} {field}`.

        e.g if index of the `txn` should be 0 then `txn RekeyTo` is same as `gtxn 0 RekeyTo`.
        similary, if index of `txn` can be `0` or `1` then checking `txn RekeyTo` is equaivalent to
        checking both `gtxn 0 RekeyTo` and `gtxn 1 RekeyTo`.

        if `i` is not a possible index of `txn` for basic block `B`, then possible values for `txn {field}` when
        accessed through `gtxn {i} {field}` is Null. Because, `txn` can never have index `i` and `gtxn {i} {field}` is field
        of `txn` when index of `txn` is `i`.

        This requires that group_indices analysis is done before any other analysis.

        Args:
            keys_with_gtxn: The list of base keys whose gtxn {idx} {RekeyTo} should be tracked.
            block: The basic block

        Fill the _block_contexts[gtx_key][block] using the possible group indices of the transaction and possible
        values of the base key.
        """
        for key in keys_with_gtxn:
            for ind in range(MAX_GROUP_SIZE):
                gtx_key = get_gtxn_at_index_key(ind, key)
                if ind in self._function.transaction_context(block).group_indices:
                    # txn can have index {ind}
                    # gtxn {ind} {field} can have a value if and only if {txn} {field} can also have that value
                    self._block_contexts[gtx_key][block] = self._intersection(
                        gtx_key,
                        self._block_contexts[gtx_key][block],
                        self._block_contexts[key][block],
                    )
                else:
                    # txn cannot have index {ind}
                    self._block_contexts[gtx_key][block] = self._null_set(gtx_key)

    def _calculate_reachin(
        self, key: str, block: "BasicBlock", reachout: Dict["BasicBlock", Any]
    ) -> Any:
        if block == self._entry_block:
            # We are considering each possible value as a definition defined at the start of entry block.
            reachin_information = self._universal_set(key)
        else:
            reachin_information = self._null_set(key)

        path_context = self._path_contexts[key]
        for prev_b in prev_blocks_global(self._function, block):
            # print(f"block:", repr(block),"prev_b ", repr(prev_b), f"block: {block.__hash__()}, prev_b: {prev_b.__hash__()}")
            # print(path_context)
            # print(path_context[block])
            reachin_information = self._union(
                key,
                reachin_information,
                self._intersection(key, reachout[prev_b], path_context[block][prev_b]),
            )

        if block.is_sub_return_point:
            # this block is the return point for callsub instruction present in `block.callsub_block`
            # execution will only reach this block, if it reaches `block.callsub_block`
            reachin_information = self._intersection(
                key, reachin_information, reachout[block.callsub_block]
            )

        return reachin_information

    def _merge_information_forward(
        self,
        analysis_keys: List[str],
        block: "BasicBlock",
        global_reachout: Dict[str, Dict["BasicBlock", Any]],
    ) -> bool:
        updated = False
        for key in analysis_keys:
            # RCHout(b) = intersection(RCHin(b), PRSV(b))
            new_reachout = self._intersection(
                key,
                self._calculate_reachin(key, block, global_reachout[key]),
                self._block_contexts[key][block],
            )
            if new_reachout != global_reachout[key][block]:
                global_reachout[key][block] = new_reachout
                updated = True
        return updated

    def forward_analyis(self, analysis_keys: List[str], worklist: List["BasicBlock"]) -> None:
        """Perform forward analysis for analysis_keys and update self._block_contexts

        Args:
            analysis_keys: List of keys.
            worklist: List of basic blocks considered for the analysis. Initial worklist.
        """
        # reachout for all analysis keys. global_reachout[key] -> reachout of key.
        # global_reachout[key][block] -> reachout of block for key.
        global_reachout: Dict[str, Dict["BasicBlock", Any]] = {}
        for key in analysis_keys:
            global_reachout[key] = {}
            for b in self._function.blocks:
                global_reachout[key][b] = self._null_set(key)

        while worklist:
            b = worklist[0]
            worklist = worklist[1:]
            updated = self._merge_information_forward(analysis_keys, b, global_reachout)

            if updated:
                # if b is callsub block the information of the called subroutine and return point need to be computed.
                # called subroutine entry is already included by next_blocks_global. So, add return point here.
                return_point_block = (
                    [b.sub_return_point]
                    if b.is_callsub_block and b.sub_return_point is not None
                    else []
                )

                for bi in next_blocks_global(self._function, b) + return_point_block:
                    if bi not in worklist:
                        worklist.append(bi)

        for key in analysis_keys:
            self._block_contexts[key] = global_reachout[key]

    def _calculate_livein(
        self, key: str, block: "BasicBlock", liveout: Dict["BasicBlock", Any]
    ) -> Any:
        livein_information = self._null_set(key)

        for next_b in next_blocks_global(self._function, block):
            livein_information = self._union(key, livein_information, liveout[next_b])

        if (
            block.is_callsub_block
            and block.sub_return_point is not None
            and len(block.called_subroutine.retsub_blocks) != 0
        ):
            # this block is the `callsub block` and `block.sub_return_point` is the block that will be executed after subroutine.
            livein_information = self._intersection(
                key, livein_information, liveout[block.sub_return_point]
            )
        return livein_information

    def _merge_information_backward(
        self,
        analysis_keys: List[str],
        block: "BasicBlock",
        global_liveout: Dict[str, Dict["BasicBlock", Any]],
    ) -> bool:
        if leaf_block_global(block):  # leaf block
            return False

        updated = False
        for key in analysis_keys:
            new_liveout = self._intersection(
                key,
                self._calculate_livein(key, block, global_liveout[key]),
                self._block_contexts[key][block],
            )
            if new_liveout != global_liveout[key][block]:
                global_liveout[key][block] = new_liveout
                updated = True
        return updated

    def backward_analysis(self, analysis_keys: List[str], worklist: List["BasicBlock"]) -> None:
        """Perform backward analysis for analysis_keys and update self._block_contexts

        Args:
            analysis_keys: List of keys.
            worklist: List of basic blocks considered for the analysis. Initial worklist.
        """
        global_liveout: Dict[str, Dict["BasicBlock", Any]] = {}
        for key in analysis_keys:
            global_liveout[key] = {}
            for b in self._function.blocks:
                if leaf_block_global(b):  # leaf block
                    global_liveout[key][b] = self._block_contexts[key][b]
                else:
                    global_liveout[key][b] = self._null_set(key)

        while worklist:
            b = worklist[0]
            worklist = worklist[1:]
            updated = self._merge_information_backward(analysis_keys, b, global_liveout)

            if updated:
                callsub_block = [b.callsub_block] if b.is_sub_return_point else []
                for bi in prev_blocks_global(self._function, b) + callsub_block:
                    if bi not in worklist:
                        worklist.append(bi)

        for key in analysis_keys:
            self._block_contexts[key] = global_liveout[key]

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

        gtx_keys = []
        for key in self.KEYS_WITH_GTXN:
            for ind in range(MAX_GROUP_SIZE):
                gtx_keys.append(get_gtxn_at_index_key(ind, key))
                gtx_keys.append(get_absolute_index_key(ind, key))

            for offset in range(-(MAX_GROUP_SIZE - 1), MAX_GROUP_SIZE):
                if offset == 0:
                    continue
                gtx_keys.append(get_relative_index_key(offset, key))

        all_keys = self.BASE_KEYS + gtx_keys

        # step 1: initialise information
        # print(self._function.blocks)
        for block in self._function.blocks:
            self._block_level_constraints(all_keys, block)  # initialise information for all keys
            self._path_level_constraints(all_keys, block)
            for debug_key in debug_keys:
                if debug_key in self.BASE_KEYS:
                    logger_txn_ctx.debug(f"Debug key: {debug_key}")
                    logger_txn_ctx.debug(f"block: B{block.idx}:\n {block}")
                    logger_txn_ctx.debug(f"block_ctx: {self._block_contexts[debug_key][block]}")
                    logger_txn_ctx.debug("\n\n")
                    logger_txn_ctx.debug(f"path_context: {self._path_contexts[debug_key]}")
        # print(self._block_contexts)
        # The contract is represented using multiple CFG, one for each subroutine.
        # Calculate postorder for each CFG and concatenate the lists for now.
        postorder = [self._postorder(self._entry_block)]
        for subroutine in self._function.subroutines.values():
            postorder.append(self._postorder(subroutine.entry))

        # perform analysis of base keys first. Information of these base keys will be used for
        # gtxn keys. see `self._update_gtxn_constraints`
        analysis_keys = list(self.BASE_KEYS)

        worklist = []
        for l in postorder:
            worklist += l[::-1]  # Reverse postorder

        self.forward_analyis(analysis_keys, worklist)

        logger_txn_ctx.debug("After Forward:")
        for debug_key in debug_keys:
            for block in self._function.blocks:
                if debug_key in self.BASE_KEYS:
                    logger_txn_ctx.debug(f"block_id: B{block.idx}")
                    logger_txn_ctx.debug(f"block_ctx: {self._block_contexts[debug_key][block]}")

        worklist = []
        for l in postorder:
            worklist += [b for b in l if not leaf_block_global(b)]  # postorder, exclude leaf blocks

        self.backward_analysis(analysis_keys, worklist)

        logger_txn_ctx.debug("After Backward:")
        for debug_key in debug_keys:
            for block in self._function.blocks:
                if debug_key in self.BASE_KEYS:
                    logger_txn_ctx.debug(f"block_id: B{block.idx}")
                    logger_txn_ctx.debug(f"block_ctx: {self._block_contexts[debug_key][block]}")

        # update gtxn constraints using possible group indices and txn constraints.
        for block in self._function.blocks:
            self._update_gtxn_constraints(self.KEYS_WITH_GTXN, block)

        # Now perform analysis for gtx_keys
        analysis_keys = gtx_keys

        worklist = []
        for l in postorder:
            worklist += l[::-1]  # Reverse postorder
        self.forward_analyis(analysis_keys, worklist)

        worklist = []
        for l in postorder:
            worklist += [b for b in l if not leaf_block_global(b)]  # postorder, exclude leaf blocks
        self.backward_analysis(analysis_keys, worklist)

        self._store_results()
