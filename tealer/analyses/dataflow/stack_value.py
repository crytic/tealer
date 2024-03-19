from collections import defaultdict
from typing import Union, Set, Any, List, Dict, TYPE_CHECKING, Type, Callable, Tuple

from tealer.analyses.dataflow.abstract import AbstractDataflow
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.global_field import GlobalField
from tealer.teal.instructions import instructions
from tealer.teal.instructions.instructions import Instruction
from tealer.teal.instructions.transaction_field import TransactionField

if TYPE_CHECKING:
    from tealer.teal.teal import Teal

MAX_ELEMS_PER_STACK_VALUE = 35
MAX_STACK_DEPTH = 100


# pylint: disable=too-few-public-methods
class TOP:
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, TOP)

    def __str__(self) -> str:
        return "TOP"


# pylint: disable=too-few-public-methods
class BOTTOM:
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, BOTTOM)

    def __str__(self) -> str:
        return "BOTTOM"


VALUES_TRACKED = Union[Set[Union[GlobalField, TransactionField, int, str]], TOP, BOTTOM]


class StackValue:
    """
    StackValue represent an abstract value on the stack
    It can be either a set of int/str/fields, or TOP/BOTTOM
    The set's size is limited to MAX_ELEMS_PER_STACK_VALUE, if above, it becomes TOP

    """

    def __init__(self, values: VALUES_TRACKED):
        if isinstance(values, set) and len(values) > MAX_ELEMS_PER_STACK_VALUE:
            values = TOP()
        self.values = values

    def union(self, other_stack_value: "StackValue") -> "StackValue":
        self_values = self.values
        other_values = other_stack_value.values
        if isinstance(self_values, TOP) or isinstance(other_values, TOP):
            return StackValue(TOP())
        if isinstance(self_values, BOTTOM):
            return StackValue(other_values)
        if isinstance(other_values, BOTTOM):
            return StackValue(self_values)
        assert isinstance(self_values, set)
        assert isinstance(other_values, set)
        return StackValue(self_values | other_values)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, StackValue):
            return self.values == other.values
        return False

    def __str__(self) -> str:
        values = self.values
        if isinstance(values, (TOP, BOTTOM)):
            return str(values)
        assert isinstance(values, set)
        return str({str(x) for x in values})


class Stack:
    """
    Represent an abstract stack
    The length is limited by MAX_STACK_DEPTH
    self.values contains the abstract element

    If there is two paths merged, where one path push 1 (concrete stack [1])
    and the other push 3; (concrete stack [3])
    then the abstract stack is
    [ [1;3] ]x
    Ie: the top can either be 1 or 3

    If we pop beyond the known values, we return TOP().
    As a result, if the most left elements are TOP in the stack, we can stop tracking them

    If there is two paths merged, and the stack size has a different size, then
    we use TOP for the elements in the difference. Ex:
    - one path push 1; push 2; (concrete stack [2;1])
    - and the other push 3; (concrete stack [3])
    - then the abstract stack is
    - [ [TOP] ; [1;3] ]
    Ie: the top can either be 1 or 3, and the second one is TOP
    Because the most left element of the stack can be removed, this can be simplied as
    [ [1;3] ]



    """

    def __init__(self, values: List[StackValue]) -> None:
        if len(values) > MAX_STACK_DEPTH:
            values = values[:-MAX_STACK_DEPTH]

        while values and values[0] == StackValue(TOP()):
            values.pop()

        self.values = values

    def union(self, stack: "Stack") -> "Stack":

        v1 = self.values
        v2 = stack.values

        min_length = min(len(v1), len(v2))
        v1 = v1[:-min_length]
        v2 = v2[:-min_length]

        v3 = []
        for i in range(min_length):
            v3.append(v1[i].union(v2[i]))

        return Stack(v3)

    def pop(self, number: int) -> Tuple["Stack", List[StackValue]]:
        if number == 0:
            return Stack(self.values), []
        if len(self.values) < number:
            diff = number - len(self.values)
            poped_values = list(self.values)
            return Stack([]), [StackValue(TOP()) for _ in range(diff)] + poped_values

        poped_values = self.values[:-number]
        return Stack(self.values[: len(self.values) - number]), poped_values

    def push(self, pushed_values: List[StackValue]) -> "Stack":
        return Stack(self.values + pushed_values)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Stack):
            return self.values == other.values
        return False

    def __str__(self) -> str:
        return str([str(x) for x in self.values])


# pylint: disable=unused-argument
def handle_int(ins: Instruction, stack: Stack) -> List[StackValue]:
    assert isinstance(ins, instructions.Int)
    return [StackValue({ins.value})]


# pylint: disable=unused-argument
def handle_pushint(ins: Instruction, stack: Stack) -> List[StackValue]:
    assert isinstance(ins, instructions.PushInt)
    return [StackValue({ins.value})]


# pylint: disable=unused-argument
def handle_txn(ins: Instruction, stack: Stack) -> List[StackValue]:
    assert isinstance(ins, instructions.Txn)
    return [StackValue({ins.field})]


# pylint: disable=unused-argument
def handle_global(ins: Instruction, stack: Stack) -> List[StackValue]:
    assert isinstance(ins, instructions.Global)
    return [StackValue({ins.field})]


special_handling: Dict[Type[Instruction], Callable[[Instruction, Stack], List[StackValue]]] = {
    instructions.Int: handle_int,
    instructions.PushInt: handle_pushint,
    instructions.Txn: handle_txn,
    instructions.Global: handle_global,
}


class StackValueAnalysis(AbstractDataflow[Stack]):
    def __init__(self, teal: "Teal") -> None:
        super().__init__(teal)
        self.bb_in: Dict[BasicBlock, Stack] = defaultdict(lambda: Stack([StackValue(BOTTOM())]))
        self.bb_out: Dict[BasicBlock, Stack] = defaultdict(lambda: Stack([]))

        self.ins_in: Dict[Instruction, Stack] = defaultdict(lambda: Stack([]))
        self.ins_out: Dict[Instruction, Stack] = defaultdict(lambda: Stack([]))

    def _merge_predecessor(self, bb: BasicBlock) -> Stack:
        s = Stack([])
        for bb_prev in bb.prev:
            s = s.union(self.bb_out[bb_prev])
        return s

    def _is_fix_point(self, bb: BasicBlock, values: Stack) -> bool:
        return self.bb_in[bb] == values

    def _transfer_function(self, bb: BasicBlock) -> Stack:
        bb_out = self.bb_in[bb]

        for ins in bb.instructions:
            self.ins_in[ins] = Stack(bb_out.values)
            if type(ins) in special_handling:
                pushed_elems = special_handling[type(ins)](ins, bb_out)
            else:
                pushed_elems = [StackValue(TOP()) for _ in range(ins.stack_push_size)]
            bb_out, _ = bb_out.pop(ins.stack_pop_size)
            bb_out = bb_out.push(pushed_elems)
            self.ins_out[ins] = Stack(bb_out.values)

        return bb_out

    def _store_values_in(self, bb: BasicBlock, values: Stack) -> None:
        self.bb_in[bb] = values

    def _store_values_out(self, bb: BasicBlock, values: Stack) -> None:
        self.bb_out[bb] = values

    def _filter_successors(self, bb: BasicBlock) -> List[BasicBlock]:
        return bb.next

    def result(self) -> Dict[BasicBlock, Stack]:
        return self.bb_out
