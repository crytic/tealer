"""Detector for finding execution paths missing GroupSize check."""

from typing import List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.global_field import GroupSize
from tealer.teal.instructions.instructions import Return, Int, Global
from tealer.teal.teal import Teal

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput


class MissingGroupSize(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find execution paths missing GroupSize check.

    Algorand supports atomic transactions. Atomic transactions are a
    group of transactions with the property that either all execute
    successfully or None of them. It is necessary to check the group size
    of the transaction based on the application.

    This detector tries to find execution paths that approve the algorand
    transaction("return 1") and doesn't check the CloseRemainderTo field.
    """

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

    def _check_groupsize(
        self,
        bb: BasicBlock,
        current_path: List[BasicBlock],
        # use_gtnx: bool,
        paths_without_check: List[List[BasicBlock]],
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
        """

        # check for loops
        if bb in current_path:
            return

        current_path = current_path + [bb]
        for ins in bb.instructions:

            if isinstance(ins, Global):
                if isinstance(ins.field, GroupSize):
                    return

            if isinstance(ins, Return):
                if len(ins.prev) == 1:
                    prev = ins.prev[0]
                    if isinstance(prev, Int):
                        if prev.value == 0:
                            return

                paths_without_check.append(current_path)

        for next_bb in bb.next:
            self._check_groupsize(next_bb, current_path, paths_without_check)

    def detect(self) -> "SupportedOutput":
        """Detect execution paths with missing GroupSize check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        paths_without_check: List[List[BasicBlock]] = []
        self._check_groupsize(self.teal.bbs[0], [], paths_without_check)

        description = "Lack of groupSize check found"
        filename = "missing_group_size"

        return self.generate_result(paths_without_check, description, filename)
