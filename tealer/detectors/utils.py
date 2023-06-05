import logging
from typing import List, TYPE_CHECKING, Callable, Tuple, Optional

from tealer.teal.instructions.instructions import Retsub, Callsub

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.subroutine import Subroutine
    from tealer.teal.context.block_transaction_context import BlockTransactionContext
    from tealer.detectors.abstract_detector import AbstractDetector

logger_detectors = logging.getLogger("Detectors")
logging.basicConfig(level=logging.DEBUG)


def validated_in_block(
    block: "BasicBlock", checks_field: Callable[["BlockTransactionContext"], bool]
) -> bool:
    """
    A transaction field can be validated by accessing using instructions
    - txn {field}
    - gtxn {current_transaction_index} {field}

    `block.transaction_context` is information from `txn {field}` instructions.
    `block.transaction_context.gtxn_context({index})` is information from `gtxn {index} {field}` instructions.
    block.transaction_context.gtxn_context(i) represents values `transaction field` have when it's index is `i`.
    Note that, block.transaction_context.gtxn_context(i) does not represent possible values of any transaction at index
    `i`. It only represents possible values of current txn given that txn index is `i`.

    Args:
        block:
        checks_field: Given a block context, should return True if the target field cannot have the vulnerable value or else False

        e.g: For is_updatable detector, vulnerable value is `UpdateApplication`.
        if `block_ctx.transaction_types` can have `UpdateApplication`, this method will
        return false or else returns True.
    Returns:
        returns True if the field(s) is validated in this block or else False
    """
    # if field is checked using `txn {field}`, return true
    if checks_field(block.transaction_context):
        return True
    # for each possible {index} the transaction can have, check if field is checked using `gtxn {index} {field}`
    for i in block.transaction_context.group_indices:
        if not checks_field(block.transaction_context.gtxn_context(i)):
            return False
    # the field is checked for all possible indices.
    return True


def detect_missing_tx_field_validations(
    entry_block: "BasicBlock",
    checks_field: Callable[["BlockTransactionContext"], bool],
    satisfies_report_condition: Callable[[List["BasicBlock"]], bool] = lambda _x: True,
) -> List[List["BasicBlock"]]:
    """search for execution paths lacking validations on transaction fields.

    `tealer.analyses.dataflow` calculates possible values a transaction field can have to successfully complete execution.
    Information is computed at block level. Each block's context(`BlockTransactionContext`)
    will have information on possible values for a transaction field such that
        - Execution reaches to the first instruction of block `B`
        - Execution reaches exit instruction of block `B` without failing.

    The goal of current detectors is to find if a given transaction field(s) can have a certain vulnerable value(s).
    e.g: is_updatable detector checks if the transaction can be UpdateApplication type transaction. Here, the vulnerable value for
    transaction type is "UpdateApplication". if "UpdateApplication" is a possible value then the contract is considered vulnerable and is reported.

    In order to find whether the given contract is vulnerable, it is sufficient to check the leaf blocks: whether transaction field can
    have target value and execution reaches end of a leaf block.
    However, The current output format requires "a execution path" from entry block to leaf block. And when a leaf block is vulnerable,
    it does **not** mean that all execution paths ending at that leaf block are vulnerable. It only means that atleast one path ending at
    that leaf block is vulnerable.

    For this reason, a traversal over the CFG is performed to enumerate execution paths. And for each block in the path it is checked
    whether transaction field(s) can have the target vulnerable value.

    Args:
        entry_block: entry basic block of the CFG
        checks_field: Given a block context, should return True if the target field cannot have the vulnerable value
            or else False.

            e.g: For is_updatable detector, vulnerable value is `UpdateApplication`.
            if `block_ctx.transaction_types` can have `UpdateApplication`, this method will
            return false or else returns True.
        satisfies_report_condition: Given a path, should return True if the "path" satifies the vulnerable condition.
    Returns:
        Returns a list of vulnerable execution paths: none of the blocks in the path check the fields.
    """

    def search_paths(
        bb: "BasicBlock",
        current_path: List["BasicBlock"],
        paths_without_check: List[List["BasicBlock"]],
        current_call_stack: List[Tuple[Optional["BasicBlock"], "Subroutine"]],
        current_subroutine_executed: List[List["BasicBlock"]],
    ) -> None:
        """
        Args:
            current_call_stack: list of callsub blocks and called subroutine along the current path.
                e.g current_callsub_blocks = [(Bi, S1), (Bj, S2), (Bk, S3), ...]
                => 1. Bi, Bj, Bk, .. all end with callsub instruction.
                   2. Bi called subroutine S1. S1 contains block Bj which called subroutine S2.
                        S2 contains Bk which calls S3.
                        S1 calls S2, S2 calls S3, ...
            current_subroutine_executed: list of subroutine basic blocks that were executed in the path.
                e.g if call stack is [(Bi, S1), (Bj, S2), (Bk, S3)]
                1. current_subroutine_executed[0] contains basic blocks of S1 that were executed before call to S2.
                2. current_subroutine_executed[1] contains basic blocks of S2 that were executed before call to S3.
                3. current_subroutine_executed[2] contains basic blocks of S3 that were executed upto this call.

                Main purpose of this argument is to identify loops. A loop contains a back edge to a previously executed block.
                if presence of loop is checked using `return True if bb in current_path else False`, detector misses paths that
                does not contain a loop.
                Mainly, when a subroutine is called twice in a path, the second call is treated as a back edge because the subroutine's blocks
                will be present in the current path (added in the first call.)
                e.g
                    ```
                    callsub Sa  // B0
                    callsub Sa  // B1
                    int 1       // B2
                    return
                    Sa:         // B3
                        callsub Sb
                        retsub      // B4
                    Sb:         // B5
                        retsub
                    ```
                before executing B1, current_path = [B0, B3, B5, B4], bb = B1
                after executing B1, current_path = [B0, B3, B5, B4, B1], bb = B3

                B3 is already present in the current_path and so is treated as a loop even though it's not.

                In order to identify loops properly, basic blocks that are executed as part of the current subroutines are tracked.
                For above example,
                    At the start of the function
                        bb = B0, current_path = [], current_call_stack = [(None, Main)], current_subroutine_executed = [[]]

                    At the end of the function before calling search_paths again
                        bb = B0, current_path = [B0], current_call_stack = [(None, Main)], current_subroutine_executed = [[B0]]

                    # B0 calls Sa. Calling a subroutine adds a item to current_call_stack and current_subroutine_executed.
                    Start
                        bb = B3, current_path = [B0], current_call_stack = [(None, Main), (B0, Sa)], current_subroutine_executed = [[B0], []]
                    End
                        bb = B3, current_path = [B0, B3], current_call_stack = [(None, Main), (B0, Sa)], current_subroutine_executed = [[B0], [B3]]

                    # B3 calls Sb. Calling a subroutine adds a item to current_call_stack and current_subroutine_executed.
                    Start
                        bb = B5, current_path = [B0, B3], current_call_stack = [(None, Main), (B0, Sa), (B3, Sb)], current_subroutine_executed = [[B0], [B3], []]
                    End
                        bb = B5, current_path = [B0, B3, B5], current_call_stack = [(None, Main), (B0, Sa), (B3, Sb)], current_subroutine_executed = [[B0], [B3], [B5]]

                    # B5 returns the execution from Sb. Returning from a subroutine removes a item from current_call_stack, current_subroutine_executed.
                    Start
                        bb = B4, current_path = [B0, B3, B5], current_call_stack = [(None, Main), (B0, Sa)], current_subroutine_executed = [[B0], [B3]]
                    End
                        bb = B4, current_path = [B0, B3, B5, B4], current_call_stack = [(None, Main), (B0, Sa)], current_subroutine_executed = [[B0], [B3, B4]]

                    Start
                        bb = B1, current_path = [B0, B3, B5, B4], current_call_stack = [(None, Main)], current_subroutine_executed = [[B0]]
                    End
                        bb = B1, current_path = [B0, B3, B5, B4, B1], current_call_stack = [(None, Main)], current_subroutine_executed = [[B0, B1]]

                    ....
        """
        # check for loops
        if bb in current_subroutine_executed[-1]:
            logger_detectors.debug(
                f"Loop Path: current_full_path = {current_path}\n, current_subroutine_executed = {current_subroutine_executed[-1]}, current_block: {repr(bb)}"
            )
            return

        if validated_in_block(bb, checks_field):
            logger_detectors.debug(
                f"Validated Path: current_full_path = {current_path}\n, current_block: {repr(bb)}"
            )
            return

        current_path = current_path + [bb]

        # leaf block
        if len(bb.next) == 0:
            logger_detectors.debug(f"Vulnerable Path: current_full_path = {current_path}")
            if satisfies_report_condition(current_path):
                # only report if it satisfies the report condition
                logger_detectors.debug(
                    f"Vulnerable Path Satisfied Report Condition: current_full_path = {current_path} "
                )
                paths_without_check.append(current_path)
            return

        # do we need to make a copy of lists in [:-1]???
        current_subroutine_executed = current_subroutine_executed[:-1] + [
            current_subroutine_executed[-1] + [bb]
        ]
        if isinstance(bb.exit_instr, Callsub):
            teal = bb.teal
            assert teal is not None
            called_subroutine = teal.subroutines[bb.exit_instr.label]
            # check for recursion
            already_called_subroutines = [frame[1] for frame in current_call_stack]
            if called_subroutine in already_called_subroutines:
                # recursion
                return
            current_call_stack = current_call_stack + [(bb, called_subroutine)]
            current_subroutine_executed = current_subroutine_executed + [[]]

        if isinstance(bb.exit_instr, Retsub):
            # if this block is retsub then it returns execution to the return
            # point of callsub block. return point is the next instruction after the callsub
            # instruction.
            (callsub_block, _) = current_call_stack[-1]
            assert callsub_block is not None
            return_point = callsub_block.sub_return_point
            if return_point is not None and return_point in bb.next:
                search_paths(
                    return_point,
                    current_path,
                    paths_without_check,
                    current_call_stack[:-1],  # returning from a subroutine
                    current_subroutine_executed[:-1],
                )
        else:
            for next_bb in bb.next:
                search_paths(
                    next_bb,
                    current_path,
                    paths_without_check,
                    current_call_stack,
                    current_subroutine_executed,
                )

    teal = entry_block.teal
    assert teal is not None
    paths_without_check: List[List["BasicBlock"]] = []
    search_paths(entry_block, [], paths_without_check, [(None, teal.main)], [[]])
    return paths_without_check


def detector_terminal_description(detector: "AbstractDetector") -> str:
    """Return description for the detector that is printed to terminal before listing vulnerable paths."""
    return (
        f'\nCheck: "{detector.NAME}", Impact: {detector.IMPACT}, Confidence: {detector.CONFIDENCE}\n'
        f"Description: {detector.DESCRIPTION}\n\n"
        f"Wiki: {detector.WIKI_URL}\n"
    )
