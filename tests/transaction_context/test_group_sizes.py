from typing import List, Tuple
import pytest


from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions import instructions
from tealer.teal.instructions import transaction_field
from tealer.teal import global_field
from tealer.teal.parse_teal import parse_teal

from tests.utils import cmp_cfg, construct_cfg, order_basic_blocks


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
    instructions.Global(global_field.GroupSize()),
    instructions.Int(2),
    instructions.Eq(),
    instructions.Assert(),
    instructions.Retsub(),
    instructions.Label("return_1"),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(3),
    instructions.Less(),
    instructions.Assert(),
    instructions.Int(1),
    instructions.Retsub(),
    instructions.Label("main"),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(1),
    instructions.Neq(),
    instructions.Assert(),
    instructions.Int(4),
    instructions.Callsub("is_even"),
    instructions.Return(),
]

ins_partitions = [(0, 2), (2, 6), (6, 12), (12, 19), (19, 26), (26, 27)]
bbs_links = [(0, 4), (4, 1), (1, 2), (1, 3), (2, 5), (3, 5)]

MULTIPLE_RETSUB_CFG_GROUP_SIZES = [[2], [2], [2], [2], [2], [2]]

MULTIPLE_RETSUB_CFG = construct_cfg(ins_list, ins_partitions, bbs_links)


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

ins_list = [
    instructions.Pragma(5),
    instructions.B("main"),
    instructions.Label("getmod"),
    instructions.Modulo(),
    instructions.Retsub(),
    instructions.Label("is_odd"),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(4),
    instructions.Less(),
    instructions.Assert(),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(2),
    instructions.Neq(),
    instructions.Assert(),
    instructions.Int(2),
    instructions.B("getmod"),
    instructions.Label("main"),
    instructions.Int(5),
    instructions.Callsub("is_odd"),
    instructions.Return(),
]

ins_partitions = [(0, 2), (2, 5), (5, 16), (16, 19), (19, 20)]
bbs_links = [(0, 3), (3, 2), (2, 1), (1, 4)]

SUBROUTINE_BACK_JUMP_CFG_GROUP_SIZES = [[1, 3], [1, 3], [1, 3], [1, 3], [1, 3], [1, 3]]
SUBROUTINE_BACK_JUMP_CFG = construct_cfg(ins_list, ins_partitions, bbs_links)

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

ins_list = [
    instructions.Pragma(4),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(2),
    instructions.GreaterE(),
    instructions.Assert(),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(4),
    instructions.Greater(),
    instructions.BZ("fin"),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(1),
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

ins_partitions = [(0, 9), (9, 13), (13, 15), (15, 21), (21, 23), (23, 26)]
bbs_links = [(0, 1), (0, 5), (1, 2), (1, 3), (3, 4), (3, 5)]

BRANCHING_CFG_GROUP_SIZES = [[2, 3, 4], [], [], [], [], [2, 3, 4]]
BRANCHING_CFG = construct_cfg(ins_list, ins_partitions, bbs_links)

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

ins_list = [
    instructions.Pragma(5),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(4),
    instructions.Neq(),
    instructions.Assert(),
    instructions.Int(0),
    instructions.Label("loop"),
    instructions.Dup(),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(3),
    instructions.GreaterE(),
    instructions.BZ("end"),
    instructions.Int(1),
    instructions.Add(),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(3),
    instructions.Less(),
    instructions.Assert(),
    instructions.B("loop"),
    instructions.Label("end"),
    instructions.Int(2),
    instructions.Global(global_field.GroupSize()),
    instructions.Eq(),
    instructions.Assert(),
    instructions.Int(1),
    instructions.Return(),
]

ins_partitions = [(0, 6), (6, 12), (12, 19), (19, 26)]
bbs_links = [(0, 1), (1, 2), (1, 3), (2, 1)]

LOOPS_CFG_GROUP_SIZES = [[2], [2], [], [2]]
LOOPS_CFG = construct_cfg(ins_list, ins_partitions, bbs_links)

cfg_group_sizes = [
    (MULTIPLE_RETSUB_CFG, MULTIPLE_RETSUB_CFG_GROUP_SIZES),
    (SUBROUTINE_BACK_JUMP_CFG, SUBROUTINE_BACK_JUMP_CFG_GROUP_SIZES),
    (BRANCHING_CFG, BRANCHING_CFG_GROUP_SIZES),
    (LOOPS_CFG, LOOPS_CFG_GROUP_SIZES),
]

for cfg, sizes in cfg_group_sizes:
    bb = order_basic_blocks(cfg)
    for b, group_sizes in zip(bb, sizes):  # type: ignore
        b.transaction_context.group_sizes = group_sizes


ALL_TESTS = [
    (MULTIPLE_RETSUB, MULTIPLE_RETSUB_CFG),
    (SUBROUTINE_BACK_JUMP, SUBROUTINE_BACK_JUMP_CFG),
    (BRANCHING, BRANCHING_CFG),
    (LOOPS, LOOPS_CFG),
]


@pytest.mark.parametrize("test", ALL_TESTS)  # type: ignore
def test_group_sizes(test: Tuple[str, List[BasicBlock]]) -> None:
    code, cfg_tested = test
    teal = parse_teal(code.strip())
    for bb_tested in cfg_tested:
        print(bb_tested)
    print("*" * 20)
    assert cmp_cfg(teal.bbs, cfg_tested)

    bbs = order_basic_blocks(teal.bbs)
    cfg_tested = order_basic_blocks(cfg_tested)
    for b1, b2 in zip(bbs, cfg_tested):
        print(b1.transaction_context.group_sizes, b2.transaction_context.group_sizes)
        assert b1.transaction_context.group_sizes == b2.transaction_context.group_sizes


MULTIPLE_RETSUB_CFG_GROUP_INDICES = [[0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1]]
SUBROUTINE_BACK_JUMP_GROUP_INDICES = [
    [0, 1, 2],
    [0, 1, 2],
    [0, 1, 2],
    [0, 1, 2],
    [0, 1, 2],
    [0, 1, 2],
]
BRANCHING_GROUP_INDICES = [[0, 1, 2, 3], [], [], [], [], [0, 1, 2, 3]]
LOOPS_GROUP_INDICES = [[0, 1], [0, 1], [], [0, 1]]

GROUP_INDICES_TESTS = [
    (MULTIPLE_RETSUB, MULTIPLE_RETSUB_CFG_GROUP_INDICES),
    (SUBROUTINE_BACK_JUMP, SUBROUTINE_BACK_JUMP_GROUP_INDICES),
    (BRANCHING, BRANCHING_GROUP_INDICES),
    (LOOPS, LOOPS_GROUP_INDICES),
]


@pytest.mark.parametrize("test", GROUP_INDICES_TESTS)  # type: ignore
def test_group_indices(test: Tuple[str, List[List[int]]]) -> None:
    code, group_indices_list = test
    teal = parse_teal(code.strip())

    bbs = order_basic_blocks(teal.bbs)
    for bb_tested, group_indices in zip(bbs, group_indices_list):
        print(bb_tested.transaction_context.group_indices, group_indices)
        assert bb_tested.transaction_context.group_indices == group_indices
