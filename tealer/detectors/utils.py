from typing import List, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock
    from tealer.teal.context.block_transaction_context import BlockTransactionContext
    from tealer.detectors.abstract_detector import AbstractDetector


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
    entry_block: "BasicBlock", checks_field: Callable[["BlockTransactionContext"], bool]
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
    Returns:
        Returns a list of vulnerable execution paths: none of the blocks in the path check the fields.
    """

    def search_paths(
        bb: "BasicBlock",
        current_path: List["BasicBlock"],
        paths_without_check: List[List["BasicBlock"]],
    ) -> None:
        # check for loops
        if bb in current_path:
            return

        if validated_in_block(bb, checks_field):
            return

        current_path = current_path + [bb]

        # leaf block
        if len(bb.next) == 0:
            paths_without_check.append(current_path)
            return

        for next_bb in bb.next:
            search_paths(next_bb, current_path, paths_without_check)

    paths_without_check: List[List["BasicBlock"]] = []
    search_paths(entry_block, [], paths_without_check)
    return paths_without_check


def detector_terminal_description(detector: "AbstractDetector") -> str:
    """Return description for the detector that is printed to terminal before listing vulnerable paths."""
    return (
        f'\nCheck: "{detector.NAME}", Impact: {detector.IMPACT}, Confidence: {detector.CONFIDENCE}\n'
        f"Description: {detector.DESCRIPTION}\n\n"
        f"Wiki: {detector.WIKI_URL}\n"
    )
