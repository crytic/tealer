"""Detector for finding execution paths missing GroupSize check."""

from typing import List, TYPE_CHECKING, Tuple

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import (
    Gtxn,
    Gtxna,
    Gtxnas,
    Gtxns,
    Gtxnsa,
    Gtxnsas,
)

from tealer.utils.algorand_constants import MAX_GROUP_SIZE
from tealer.utils.analyses import is_int_push_ins
from tealer.analyses.utils.stack_ast_builder import construct_stack_ast, UnknownStackValue
from tealer.detectors.utils import detect_missing_tx_field_validations_group
from tealer.utils.output import ExecutionPaths


if TYPE_CHECKING:
    from tealer.teal.teal import Teal
    from tealer.utils.output import ListOutput
    from tealer.teal.instructions.instructions import Instruction
    from tealer.teal.context.block_transaction_context import BlockTransactionContext


class MissingGroupSize(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find execution paths using absoulte index without checking group size."""

    NAME = "group-size-check"
    DESCRIPTION = "Usage of absolute indexes without validating GroupSize"
    TYPE = DetectorType.STATELESS_AND_STATEFULL

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_URL = (
        "https://github.com/crytic/tealer/wiki/Detector-Documentation#missing-groupsize-validation"
    )
    WIKI_TITLE = "Missing GroupSize Validation"
    WIKI_DESCRIPTION = (
        "Contract's execution depends on multiple transactions in the group"
        " and it uses absolute index to access information of other transactions in the group."
        " Attacker can exploit the contract by abusing the lack of validations on `GroupSize`."
        " More at [building-secure-contracts/not-so-smart-contracts/algorand/group_size_check]"
        "(https://github.com/crytic/building-secure-contracts/tree/master/not-so-smart-contracts/algorand/group_size_check)"
    )
    WIKI_EXPLOIT_SCENARIO = """
```py
def mint_wrapped_algo() -> Expr:
    validations = Assert(
        And(
            Gtxn[0].receiver() == Global.current_application_address(),
            Gtxn[0].type_enum() == TxnType.Payment,
        )
    )
    transfer_op = transfer_wrapped_algo(Txn.sender(), Gtxn[0].amount())
    return Seq([validations, transfer_op, Approve()])
```

Eve sends the following group transaction:
```
0. Payment of 1 million ALGOs to application address
1. Call mint_wrapped_algo
2. Call mint_wrapped_algo 
...
15. Call mint_wrapped_algo
```

Eve receives 15 million wrapped-algos instead of 1 million wrapped-algos.\
 Eve exchanges the Wrapped-algo to ALGO and steals 14 million ALGOs.
"""
    WIKI_RECOMMENDATION = """
- Avoid using absolute indexes. Validate GroupSize if used.
- Favor using ARC-4 ABI and relative indexes for group transactions.
"""

    @staticmethod
    def _accessed_using_absolute_index(bb: BasicBlock) -> bool:
        """Return True if a instruction in bb access a field using absolute index

        a. gtxn t f, gtxna t f i, gtxnas t f,
        b. gtxns f, gtxnsa f i, gtxnsas f

        Instructions in (a) take transaction index as a immediate argument.
        Return True if bb contains any one of those instructions.

        Instructions in (b) take transaction index from the stack.
        `gtxns f` and `gtxnsa f i` take only one argument and it is the transaction index.
        `gtxnsas f` takes two arguments and transaction index is the first argument.
        Return True if the transaction index is pushed by an int instruction.

        Args:
            bb: A basic block of the CFG

        Returns:
            Returns True if a instruction in bb access a field of group transaction using
            an absolute index. returns False otherwise.
        """
        stack_gtxns_ins: List["Instruction"] = []
        for ins in bb.instructions:
            if isinstance(ins, (Gtxn, Gtxna, Gtxnas)):
                return True
            if isinstance(ins, (Gtxns, Gtxnsa, Gtxnsas)):
                stack_gtxns_ins.append(ins)
        if not stack_gtxns_ins:
            return False
        ast_values = construct_stack_ast(bb)
        for ins in stack_gtxns_ins:
            index_value = ast_values[ins].args[0]
            if isinstance(index_value, UnknownStackValue):
                continue
            is_int, _ = is_int_push_ins(index_value.instruction)
            if is_int:
                return True
        return False

    def detect(self) -> "ListOutput":
        """Detect execution paths with missing GroupSize check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        def checks_group_size(block_ctx: "BlockTransactionContext") -> bool:
            # return True if group-size is checked in the path
            # otherwise return False
            if block_ctx.is_gtxn_context:
                # gtxn_contexts have group-sizes, group-indices set to 0.
                return False
            return MAX_GROUP_SIZE not in block_ctx.group_sizes

        def satisfies_report_condition(path: List["BasicBlock"]) -> bool:

            for block in path:
                if self._accessed_using_absolute_index(block):
                    return True
            return False

        output: List[
            Tuple["Teal", List[List["BasicBlock"]]]
        ] = detect_missing_tx_field_validations_group(
            self.tealer, checks_group_size, satisfies_report_condition
        )
        construct_stack_ast.cache_clear()

        detector_output: "ListOutput" = []
        for contract, vulnerable_paths in output:
            detector_output.append(ExecutionPaths(contract, self, vulnerable_paths))

        return detector_output
