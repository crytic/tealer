from typing import List, Tuple
import pytest


from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions import instructions
from tealer.teal.parse_teal import parse_teal

from tests.utils import cmp_cfg, construct_cfg


MULTIPLE_RETSUB = """
#pragma version 5
b main
is_even:
    int 2
    %
    bz return_1
    int 0
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
    instructions.Label("is_even"),
    instructions.Int(2),
    instructions.Modulo(),
    instructions.BZ("return_1"),
    instructions.Int(0),
    instructions.Retsub(),
    instructions.Label("return_1"),
    instructions.Int(1),
    instructions.Retsub(),
    instructions.Label("main"),
    instructions.Int(4),
    instructions.Callsub("is_even"),
    instructions.Return(),
]

ins_partitions = [(0, 2), (2, 6), (6, 8), (8, 11), (11, 14), (14, 15)]
bbs_links = [(0, 4), (4, 1), (1, 2), (1, 3), (2, 5), (3, 5)]


MULTIPLE_RETSUB_CFG = construct_cfg(ins_list, ins_partitions, bbs_links)


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

SUBROUTINE_BACK_JUMP_CFG = construct_cfg(ins_list, ins_partitions, bbs_links)


ALL_TESTS = [
    (MULTIPLE_RETSUB, MULTIPLE_RETSUB_CFG),
    (SUBROUTINE_BACK_JUMP, SUBROUTINE_BACK_JUMP_CFG),
]


@pytest.mark.parametrize("test", ALL_TESTS)  # type: ignore
def test_cfg_construction(test: Tuple[str, List[BasicBlock]]) -> None:
    code, cfg = test
    teal = parse_teal(code.strip())
    assert cmp_cfg(teal.bbs, cfg)
