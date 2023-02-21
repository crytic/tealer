"""Detector for finding execution paths missing GroupSize check."""

from typing import List, TYPE_CHECKING

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
from tealer.teal.teal import Teal

from tealer.utils.algorand_constants import MAX_GROUP_SIZE
from tealer.utils.analyses import is_int_push_ins
from tealer.analyses.utils.stack_ast_builder import construct_stack_ast, UnknownStackValue
from tealer.detectors.utils import detector_terminal_description

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput
    from tealer.teal.instructions.instructions import Instruction


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

    def __init__(self, teal: Teal):
        super().__init__(teal)
        self.results_number = 0

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

    def _check_groupsize(
        self,
        bb: BasicBlock,
        current_path: List[BasicBlock],
        paths_without_check: List[List[BasicBlock]],
        used_abs_index: bool,
    ) -> None:
        """Find execution paths with missing GroupSize check.

        This function recursively explores the Control Flow Graph(CFG) of the
        contract and reports execution paths with missing GroupSize
        check.

        This function is "in place", modifies arguments with the data it is
        supposed to return.

        Args:
            bb: Current basic block being checked(whose execution is simulated.)
            current_path: Current execution path being explored.
            paths_without_check:
                Execution paths with missing GroupSize check. This is a
                "in place" argument. Vulnerable paths found by this function are
                appended to this list.
            used_abs_index: Should be True if absolute index in `current_path`.
        """

        # check for loops
        if bb in current_path:
            return

        if MAX_GROUP_SIZE not in bb.transaction_context.group_sizes:
            # GroupSize is checked
            return

        if not used_abs_index:
            used_abs_index = self._accessed_using_absolute_index(bb)

        current_path = current_path + [bb]
        if not bb.next:
            # leaf block
            if used_abs_index:
                # accessed a field using absolute index in this path.
                paths_without_check.append(current_path)
            return
        for next_bb in bb.next:
            self._check_groupsize(next_bb, current_path, paths_without_check, used_abs_index)

    def detect(self) -> "SupportedOutput":
        """Detect execution paths with missing GroupSize check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        paths_without_check: List[List[BasicBlock]] = []
        self._check_groupsize(self.teal.bbs[0], [], paths_without_check, False)

        description = detector_terminal_description(self)
        filename = "missing_group_size"

        results = self.generate_result(paths_without_check, description, filename)
        construct_stack_ast.cache_clear()
        return results
