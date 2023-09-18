from typing import Tuple, Dict, List, Any

import pytest

from tealer.analyses.dataflow.stack_value import StackValueAnalysis, Stack, StackValue
from tealer.teal import global_field
from tealer.teal.instructions import instructions
from tealer.teal.parse_teal import parse_teal

MULTIPLE_RETSUB = """
#pragma version 5
b main
is_even:
    int 2
    %
    bz return_1
    int 0
    global GroupSize
    int 2
    ==
    assert
    retsub
return_1:
    global GroupSize
    int 3
    <
    assert
    int 1
    retsub
main:
    global GroupSize
    int 1
    !=
    assert
    int 4æ
    callsub is_even
    return
"""

MULTIPLE_RETSUB_EXCEPTED = {
    11: Stack([StackValue({0}), StackValue({global_field.GroupSize()}), StackValue({2})]),
    17: Stack([StackValue({global_field.GroupSize()}), StackValue({3})]),
    24: Stack([StackValue({global_field.GroupSize()}), StackValue({1})]),
}

SUBROUTINE_BACK_JUMP = """
#pragma version 5
b main
getmod:
    %
    retsub
is_odd:
    global GroupSize
    int 4
    <
    assert
    global GroupSize
    int 2
    !=
    assert
    int 2
    b getmod
main:
    int 5
    callsub is_odd
    return
"""

SUBROUTINE_BACK_JUMP_EXCEPTED = {
    10: Stack([StackValue({global_field.GroupSize()}), StackValue({4})]),
    14: Stack([StackValue({global_field.GroupSize()}), StackValue({2})]),
}

BRANCHING = """
#pragma version 4
global GroupSize
int 2
>=
assert
global GroupSize
int 4
>
bz fin
global GroupSize
int 1
==
bnz check_second_arg
int 0
return
check_second_arg:
txn ApplicationArgs 1
btoi
int 100
>
bnz fin
int 0
return
fin:
int 1
return
"""

BRANCHING_EXCEPTED = {
    5: Stack([StackValue({global_field.GroupSize()}), StackValue({2})]),
    9: Stack([StackValue({global_field.GroupSize()}), StackValue({4})]),
    13: Stack([StackValue({global_field.GroupSize()}), StackValue({1})]),
    21: Stack([StackValue({100})]),
}

LOOPS = """
#pragma version 5
global GroupSize
int 4
!=
assert
int 0
loop:
    dup
    global GroupSize
    int 3
    >=
    bz end
    int 1
    +
    global GroupSize
    int 3
    <
    assert
    b loop
end:
    int 2
    global GroupSize
    ==
    assert
    int 1
    return
"""

LOOPS_EXCEPTED = {
    5: Stack([StackValue({global_field.GroupSize()}), StackValue({4})]),
    12: Stack([StackValue({global_field.GroupSize()}), StackValue({3})]),
    18: Stack([StackValue({global_field.GroupSize()}), StackValue({3})]),
    24: Stack([StackValue({2}), StackValue({global_field.GroupSize()})]),
}

ALL_TESTS = [
    (MULTIPLE_RETSUB, MULTIPLE_RETSUB_EXCEPTED),
    (SUBROUTINE_BACK_JUMP, SUBROUTINE_BACK_JUMP_EXCEPTED),
    (BRANCHING, BRANCHING_EXCEPTED),
    (LOOPS, LOOPS_EXCEPTED),
]


@pytest.mark.parametrize("test", ALL_TESTS)  # type: ignore
def test_group_indices(test: Tuple[str, Dict[int, List[Any]]]) -> None:
    teal = parse_teal(test[0])

    ci = StackValueAnalysis(teal)
    ci.run_analysis()

    for ins in teal.instructions:
        if isinstance(
            ins,
            (
                instructions.Greater,
                instructions.GreaterE,
                instructions.Less,
                instructions.LessE,
                instructions.Eq,
                instructions.Neq,
            ),
        ):
            excepted = test[1][ins.line]
            assert excepted == ci.ins_in[ins]


def print_stack(code: str) -> None:
    teal = parse_teal(code)

    sv = StackValueAnalysis(teal)
    sv.run_analysis()
    print(code)

    for ins in teal.instructions:
        if isinstance(
            ins,
            (
                instructions.Greater,
                instructions.GreaterE,
                instructions.Less,
                instructions.LessE,
                instructions.Eq,
                instructions.Neq,
            ),
        ):
            print("###")
            print(ins)
            print(f"Before: {sv.ins_in[ins]}")
            print(f"After: {sv.ins_out[ins]}")
            print()


if __name__ == "__main__":
    print_stack(MULTIPLE_RETSUB)
    print_stack(SUBROUTINE_BACK_JUMP)
    print_stack(BRANCHING)
    print_stack(LOOPS)
