from typing import List, Tuple
import pytest


from tealer.teal.basic_blocks import BasicBlock
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


ALL_TESTS = [
    (MULTIPLE_RETSUB, MULTIPLE_RETSUB_CFG),
    (SUBROUTINE_BACK_JUMP, SUBROUTINE_BACK_JUMP_CFG),
    (BRANCHING, BRANCHING_CFG),
    (LOOPS, LOOPS_CFG),
]


@pytest.mark.parametrize("test", ALL_TESTS)  # type: ignore
def test_cfg_construction(test: Tuple[str, List[BasicBlock]]) -> None:
    code, cfg = test
    teal = parse_teal(code.strip())
    for bb in cfg:
        print(bb)
    print("*" * 20)
    assert cmp_cfg(teal.bbs, cfg)
