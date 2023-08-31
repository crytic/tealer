from typing import Tuple, Dict
import pytest

from tealer.teal.subroutine import Subroutine
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
bbs_links = [(0, 6), (2, 3), (2, 5), (3, 4), (6, 7)]

bbs = construct_cfg(ins_list, ins_partitions, bbs_links)
MULTIPLE_RETSUB_MAIN = Subroutine("", bbs[0], [bbs[0], bbs[6], bbs[7]])
MULTIPLE_RETSUB_SUBROUTINES = {
    "push_zero": Subroutine("push_zero", bbs[1], [bbs[1]]),
    "is_even": Subroutine("is_even", bbs[2], [bbs[2], bbs[3], bbs[4], bbs[5]]),
}

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
bbs_links = [(0, 3), (3, 4), (2, 1)]

bbs = construct_cfg(ins_list, ins_partitions, bbs_links)
SUBROUTINE_BACK_JUMP_MAIN = Subroutine("", bbs[0], [bbs[0], bbs[3], bbs[4]])
SUBROUTINE_BACK_JUMP_SUBROUTINES = {"is_odd": Subroutine("is_odd", bbs[2], [bbs[1], bbs[2]])}

ALL_TESTS = [
    (MULTIPLE_RETSUB, MULTIPLE_RETSUB_MAIN, MULTIPLE_RETSUB_SUBROUTINES),
    (SUBROUTINE_BACK_JUMP, SUBROUTINE_BACK_JUMP_MAIN, SUBROUTINE_BACK_JUMP_SUBROUTINES),
]


@pytest.mark.parametrize("test", ALL_TESTS)  # type: ignore
def test_subroutine_identification(test: Tuple[str, Subroutine, Dict[str, Subroutine]]) -> None:
    code, expected_main, expected_subroutines = test
    teal = parse_teal(code.strip())
    test_main = teal.main

    assert cmp_cfg([test_main.entry], [expected_main.entry])
    assert cmp_cfg(test_main.blocks, expected_main.blocks)

    subroutines = teal.subroutines
    assert len(subroutines.keys()) == len(expected_subroutines.keys())
    assert sorted(subroutines.keys()) == sorted(expected_subroutines.keys())
    for ex_name in expected_subroutines:
        subroutine = subroutines[ex_name]
        expected_subroutine = expected_subroutines[ex_name]
        assert subroutine.name == expected_subroutine.name
        assert cmp_cfg([subroutine.entry], [expected_subroutine.entry])
        assert cmp_cfg(subroutine.blocks, expected_subroutine.blocks)
    assert len(subroutines) == len(expected_subroutines)
