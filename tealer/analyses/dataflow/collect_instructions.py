from collections import defaultdict
from typing import Union, Set, Any, List, Dict, TYPE_CHECKING

from tealer.analyses.dataflow.abstract import AbstractDataflow
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Instruction

if TYPE_CHECKING:
    from tealer.teal.teal import Teal

MAX_ELEMS = 35


class InstructionSet:
    def __init__(self, values: Union[str, Instruction, Set[Instruction]]) -> None:

        if isinstance(values, str):
            assert values in ["TOP", "BOTTOM"]

        if isinstance(values, set) and len(values) > MAX_ELEMS:
            values = "TOP"
        if isinstance(values, Instruction):
            values = {values}

        self.values: Union[str, Set[Instruction]] = values

    @property
    def is_top(self) -> bool:
        return isinstance(self.values, str) and self.values == "TOP"

    @property
    def is_bottom(self) -> bool:
        return isinstance(self.values, str) and self.values == "BOTTOM"

    def union(self, instructions: "InstructionSet") -> "InstructionSet":
        v0 = self.values
        v1 = instructions.values
        if v0 == "TOP" or v1 == "TOP":
            return InstructionSet("TOP")

        if v0 == "BOTTOM":
            return InstructionSet(v1)

        if v1 == "BOTTOM":
            return InstructionSet(v0)

        assert isinstance(v0, set)
        assert isinstance(v1, set)

        return InstructionSet(v0.union(v1))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, InstructionSet):
            if isinstance(self.values, str) and isinstance(other.values, str):
                return self.values == other.values
            if isinstance(self.values, set) and isinstance(other.values, set):
                return self.values == other.values
        return False

    def __str__(self) -> str:
        if isinstance(self.values, str):
            return self.values
        return "[" + ",".join([str(x) for x in self.values]) + "]"


class CollectInstructions(AbstractDataflow[InstructionSet]):
    def __init__(self, teal: "Teal") -> None:
        super().__init__(teal)
        self.bb_in: Dict[BasicBlock, InstructionSet] = defaultdict(lambda: InstructionSet("BOTTOM"))
        self.bb_out: Dict[BasicBlock, InstructionSet] = defaultdict(
            lambda: InstructionSet("BOTTOM")
        )

    def _merge_predecessor(self, bb: BasicBlock) -> InstructionSet:
        s = InstructionSet("BOTTOM")
        for bb_prev in bb.prev:
            s = s.union(self.bb_out[bb_prev])

        return s

    def _is_fix_point(self, bb: BasicBlock, values: InstructionSet) -> bool:
        return self.bb_in[bb] == values

    def _transfer_function(self, bb: BasicBlock) -> InstructionSet:
        bb_out = self.bb_in[bb]

        for ins in bb.instructions:
            bb_out = bb_out.union(InstructionSet(ins))

        return bb_out

    def _store_values_in(self, bb: BasicBlock, values: InstructionSet) -> None:
        self.bb_in[bb] = values

    def _store_values_out(self, bb: BasicBlock, values: InstructionSet) -> None:
        self.bb_out[bb] = values

    def _filter_successors(self, bb: BasicBlock) -> List[BasicBlock]:
        return bb.next

    def result(self) -> Dict[BasicBlock, InstructionSet]:
        return self.bb_out
