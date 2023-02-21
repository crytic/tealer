from typing import List, Tuple
import pytest


from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions import instructions
from tealer.teal.parse_teal import parse_teal

from tests.utils import cmp_cfg, construct_cfg


MULTIPLE_RETSUB = """
#pragma version 5
b main
push_zero:
    int 0
    retsub
is_even:
    int 2
    %
    bz return_1
    callsub push_zero
    retsub
return_1:
    int 1
    retsub
main:
    int 4
    callsub is_even
    return
"""

ins_list = [
    instructions.Pragma(5),
    instructions.B("main"),
    instructions.Label("push_zero"),
    instructions.Int(0),
    instructions.Retsub(),
    instructions.Label("is_even"),
    instructions.Int(2),
    instructions.Modulo(),
    instructions.BZ("return_1"),
    instructions.Callsub("push_zero"),
    instructions.Retsub(),
    instructions.Label("return_1"),
    instructions.Int(1),
    instructions.Retsub(),
    instructions.Label("main"),
    instructions.Int(4),
    instructions.Callsub("is_even"),
    instructions.Return(),
]

ins_partitions = [(0, 2), (2, 5), (5, 9), (9, 10), (10, 11), (11, 14), (14, 17), (17, 18)]
bbs_links = [(0, 6), (6, 2), (2, 3), (2, 5), (3, 1), (1, 4), (4, 7), (5, 7)]

bbs = construct_cfg(ins_list, ins_partitions, bbs_links)
MULTIPLE_RETSUB_SUBROUTINES = [
    [bbs[1]],  # push_zero
    [bbs[2], bbs[3], bbs[4], bbs[5]],  # is_even
]


SUBROUTINE_BACK_JUMP = """
#pragma version 5
b main
getmod:
    %
    retsub
is_odd:
    int 2
    b getmod
main:
    int 5
    callsub is_odd
    return
"""

ins_list = [
    instructions.Pragma(5),
    instructions.B("main"),
    instructions.Label("getmod"),
    instructions.Modulo(),
    instructions.Retsub(),
    instructions.Label("is_odd"),
    instructions.Int(2),
    instructions.B("getmod"),
    instructions.Label("main"),
    instructions.Int(5),
    instructions.Callsub("is_odd"),
    instructions.Return(),
]

ins_partitions = [(0, 2), (2, 5), (5, 8), (8, 11), (11, 12)]
bbs_links = [(0, 3), (3, 2), (2, 1), (1, 4)]

bbs = construct_cfg(ins_list, ins_partitions, bbs_links)
SUBROUTINE_BACK_JUMP_SUBROUTINES = [[bbs[1], bbs[2]]]  # is_odd

ALL_TESTS = [
    (MULTIPLE_RETSUB, MULTIPLE_RETSUB_SUBROUTINES),
    (SUBROUTINE_BACK_JUMP, SUBROUTINE_BACK_JUMP_SUBROUTINES),
]


@pytest.mark.parametrize("test", ALL_TESTS)  # type: ignore
def test_subroutine_identification(test: Tuple[str, List[List[BasicBlock]]]) -> None:
    code, expected_subroutines = test
    teal = parse_teal(code.strip())
    subroutines = teal.subroutines
    assert len(subroutines) == len(expected_subroutines)
    subroutines = sorted(subroutines, key=lambda x: x[0].idx)
    expected_subroutines = sorted(expected_subroutines, key=lambda x: x[0].idx)

    for sub, ex_sub in zip(subroutines, expected_subroutines):
        assert cmp_cfg(sub, ex_sub)
