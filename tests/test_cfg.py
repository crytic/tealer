from typing import List, Tuple, Dict
import pytest


from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.subroutine import Subroutine
from tealer.teal.instructions import instructions
from tealer.teal.instructions import transaction_field
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
bbs_links = [(0, 4), (4, 5), (1, 2), (1, 3)]

bbs_edges_new = [(0, 4), (4, 5), (1, 2), (1, 3)]


MULTIPLE_RETSUB_CFG = construct_cfg(ins_list, ins_partitions, bbs_links)

MULTIPLE_RETSUB_CFG_NEW = construct_cfg(ins_list, ins_partitions, bbs_edges_new)

bbs = MULTIPLE_RETSUB_CFG_NEW
MULTIPLE_RETSUB_MAIN_NEW = Subroutine("__main__", bbs[0], [bbs[0], bbs[4], bbs[5]])
MULTIPLE_RETSUB_SUBROUTINES_NEW = {
    "is_even": Subroutine("is_even", bbs[1], [bbs[1], bbs[2], bbs[3]])
}

MULTIPLE_RETSUB_SUBROUTINES_NEW["is_even"].caller_blocks = [bbs[4]]

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

bbs_edges_new = [(0, 3), (3, 4), (2, 1)]

SUBROUTINE_BACK_JUMP_CFG = construct_cfg(ins_list, ins_partitions, bbs_links)
SUBROUTINE_BACK_JUMP_CFG_NEW = construct_cfg(ins_list, ins_partitions, bbs_edges_new)

bbs = SUBROUTINE_BACK_JUMP_CFG_NEW
SUBROUTINE_BACK_JUMP_MAIN_NEW = Subroutine("__main__", bbs[0], [bbs[0], bbs[3], bbs[4]])
SUBROUTINE_BACK_JUMP_SUBROUTINES_NEW = {"is_odd": Subroutine("is_odd", bbs[2], [bbs[1], bbs[2]])}
SUBROUTINE_BACK_JUMP_SUBROUTINES_NEW["is_odd"].caller_blocks = [bbs[3]]


BRANCHING = """
#pragma version 2
txn NumAppArgs
int 2
==
bz fin
byte "myarg"
txn ApplicationArgs 0
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

ins_list = [
    instructions.Pragma(2),
    instructions.Txn(transaction_field.NumAppArgs()),
    instructions.Int(2),
    instructions.Eq(),
    instructions.BZ("fin"),
    instructions.Byte('"myarg"'),
    instructions.Txn(transaction_field.ApplicationArgs(0)),
    instructions.Eq(),
    instructions.BNZ("check_second_arg"),
    instructions.Int(0),
    instructions.Return(),
    instructions.Label("check_second_arg"),
    instructions.Txn(transaction_field.ApplicationArgs(1)),
    instructions.Btoi(),
    instructions.Int(100),
    instructions.Greater(),
    instructions.BNZ("fin"),
    instructions.Int(0),
    instructions.Return(),
    instructions.Label("fin"),
    instructions.Int(1),
    instructions.Return(),
]

ins_partitions = [(0, 5), (5, 9), (9, 11), (11, 17), (17, 19), (19, 22)]
bbs_links = [(0, 1), (0, 5), (1, 2), (1, 3), (3, 4), (3, 5)]

BRANCHING_CFG = construct_cfg(ins_list, ins_partitions, bbs_links)
BRANCHING_CFG_NEW = construct_cfg(ins_list, ins_partitions, bbs_links)

bbs = BRANCHING_CFG_NEW
BRANCHING_MAIN_NEW = Subroutine(
    "__main__", bbs[0], [bbs[0], bbs[1], bbs[2], bbs[3], bbs[4], bbs[5]]
)
BRANCHING_SUBROUTINES_NEW: Dict[str, Subroutine] = {}


LOOPS = """
int 0
loop:
    dup
    int 5
    <
    bz end
    int 1
    +
    b loop
end:
    int 1
    return
"""

ins_list = [
    instructions.Int(0),
    instructions.Label("loop"),
    instructions.Dup(),
    instructions.Int(5),
    instructions.Less(),
    instructions.BZ("end"),
    instructions.Int(1),
    instructions.Add(),
    instructions.B("loop"),
    instructions.Label("end"),
    instructions.Int(1),
    instructions.Return(),
]

ins_partitions = [(0, 1), (1, 6), (6, 9), (9, 12)]
bbs_links = [(0, 1), (1, 2), (1, 3), (2, 1)]

LOOPS_CFG = construct_cfg(ins_list, ins_partitions, bbs_links)
LOOPS_CFG_NEW = construct_cfg(ins_list, ins_partitions, bbs_links)

bbs = LOOPS_CFG_NEW
LOOPS_MAIN_NEW = Subroutine("__main__", bbs[0], [bbs[0], bbs[1], bbs[2], bbs[3]])
LOOPS_SUBROUTINES_NEW: Dict[str, Subroutine] = {}


SWITCH_N_MATCH = """
#pragma version 8
int 1
switch label1 label2
int 1
int 2
int 1
match label1 label2
int 0
return
label1:
int 2
return
label2:
int 3
return
"""

ins_list = [
    instructions.Pragma(8),
    instructions.Int(1),
    instructions.Switch(["label1", "label2"]),
    instructions.Int(1),
    instructions.Int(2),
    instructions.Int(1),
    instructions.Match(["label1", "label2"]),
    instructions.Int(0),
    instructions.Return(),
    instructions.Label("label1"),
    instructions.Int(2),
    instructions.Return(),
    instructions.Label("label2"),
    instructions.Int(3),
    instructions.Return(),
]

ins_partitions = [(0, 3), (3, 7), (7, 9), (9, 12), (12, 15)]
bbs_links = [(0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)]

SWITCH_N_MATCH_CFG = construct_cfg(ins_list, ins_partitions, bbs_links)
SWITCH_N_MATCH_CFG_NEW = construct_cfg(ins_list, ins_partitions, bbs_links)

bbs = SWITCH_N_MATCH_CFG_NEW
SWITCH_N_MATCH_MAIN_NEW = Subroutine("__main__", bbs[0], [bbs[0], bbs[1], bbs[2], bbs[3], bbs[4]])
SWITCH_N_MATCH_SUBROUTINES_NEW: Dict[str, Subroutine] = {}


ALL_TESTS = [
    (MULTIPLE_RETSUB, MULTIPLE_RETSUB_CFG),
    (SUBROUTINE_BACK_JUMP, SUBROUTINE_BACK_JUMP_CFG),
    (BRANCHING, BRANCHING_CFG),
    (LOOPS, LOOPS_CFG),
    (SWITCH_N_MATCH, SWITCH_N_MATCH_CFG),
]

ALL_TESTS_NEW = [
    (
        MULTIPLE_RETSUB,
        MULTIPLE_RETSUB_CFG_NEW,
        MULTIPLE_RETSUB_MAIN_NEW,
        MULTIPLE_RETSUB_SUBROUTINES_NEW,
    ),
    (
        SUBROUTINE_BACK_JUMP,
        SUBROUTINE_BACK_JUMP_CFG_NEW,
        SUBROUTINE_BACK_JUMP_MAIN_NEW,
        SUBROUTINE_BACK_JUMP_SUBROUTINES_NEW,
    ),
    (BRANCHING, BRANCHING_CFG_NEW, BRANCHING_MAIN_NEW, BRANCHING_SUBROUTINES_NEW),
    (LOOPS, LOOPS_CFG_NEW, LOOPS_MAIN_NEW, LOOPS_SUBROUTINES_NEW),
    (
        SWITCH_N_MATCH,
        SWITCH_N_MATCH_CFG_NEW,
        SWITCH_N_MATCH_MAIN_NEW,
        SWITCH_N_MATCH_SUBROUTINES_NEW,
    ),
]


@pytest.mark.parametrize("test", ALL_TESTS)  # type: ignore
def test_cfg_construction(test: Tuple[str, List[BasicBlock]]) -> None:
    code, cfg = test
    teal = parse_teal(code.strip())
    for bb in cfg:
        print(bb)
    for bb in teal.bbs:
        print(bb)
    print("*" * 20)
    assert cmp_cfg(teal.bbs, cfg)


@pytest.mark.parametrize("test", ALL_TESTS_NEW)  # type: ignore
def test_cfg_construction_new(
    test: Tuple[str, List[BasicBlock], Subroutine, Dict[str, Subroutine]]
) -> None:
    code, expected_cfg, expected_main, expected_subroutines = test
    teal = parse_teal(code.strip())
    for bb in expected_cfg:
        print(bb)
    for bb in teal.bbs:
        print(bb)
    print("*" * 20)
    assert cmp_cfg(teal.bbs, expected_cfg)
    test_main = teal.main
    test_subroutines = teal.subroutines

    assert cmp_cfg([test_main.entry], [expected_main.entry])
    assert cmp_cfg(test_main.blocks, expected_main.blocks)

    assert len(test_subroutines.keys()) == len(expected_subroutines.keys())
    assert sorted(test_subroutines.keys()) == sorted(expected_subroutines.keys())
    for ex_name in expected_subroutines:
        test_subroutine = test_subroutines[ex_name]
        expected_subroutine = expected_subroutines[ex_name]
        assert test_subroutine.name == expected_subroutine.name
        assert cmp_cfg([test_subroutine.entry], [expected_subroutine.entry])
        assert cmp_cfg(test_subroutine.blocks, expected_subroutine.blocks)
        assert cmp_cfg(test_subroutine.caller_blocks, expected_subroutine.caller_blocks)
    assert len(test_subroutines) == len(expected_subroutines)
