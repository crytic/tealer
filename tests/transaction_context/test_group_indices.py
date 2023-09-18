from typing import List, Tuple
import pytest

from tealer.utils.command_line.common import init_tealer_from_single_contract
from tests.utils import order_basic_blocks


MULTIPLE_RETSUB = """
#pragma version 5
b main
is_even:
    int 2
    %
    bz return_1
    int 0
    txn GroupIndex
    int 2
    ==
    assert
    retsub
return_1:
    txn GroupIndex
    int 3
    <
    assert
    int 1
    retsub
main:
    txn GroupIndex
    int 1
    !=
    assert
    int 4
    callsub is_even
    return
"""

MULTIPLE_RETSUB_GROUP_INDICES = [[0, 2], [0, 2], [2], [0, 2], [0, 2], [0, 2]]

SUBROUTINE_BACK_JUMP = """
#pragma version 5
b main
getmod:
    %
    retsub
is_odd:
    txn GroupIndex
    int 4
    <
    assert
    txn GroupIndex
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

SUBROUTINE_BACK_JUMP_GROUP_INDICES = [
    [0, 1, 3],
    [0, 1, 3],
    [0, 1, 3],
    [0, 1, 3],
    [0, 1, 3],
    [0, 1, 3],
]

BRANCHING = """
#pragma version 4
txn GroupIndex
int 2
>=
assert
txn GroupIndex
int 4
>
bz fin
txn GroupIndex
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

BRANCHING_GROUP_INDICES = [[2, 3, 4], [], [], [], [], [2, 3, 4]]

LOOPS = """
#pragma version 5
txn GroupIndex
int 4
!=
assert
int 0
loop:
    dup
    txn GroupIndex
    int 3
    >=
    bz end
    int 1
    +
    txn GroupIndex
    int 3
    <
    assert
    b loop
end:
    int 2
    txn GroupIndex
    ==
    assert
    int 1
    return
"""

LOOPS_GROUP_INDICES = [[2], [2], [], [2]]

LOOPS_GROUP_SIZES = """
#pragma version 5
txn GroupIndex
int 4
!=
assert
global GroupSize
int 6
<=
int 0
loop:
    dup
    txn GroupIndex
    int 3
    >
    bz end
    int 1
    +
    txn GroupIndex
    int 6
    <
    assert
    b loop
end:
    int 2
    txn GroupIndex
    >
    assert
    int 5
    global GroupSize
    <=
    assert
    int 1
    return
"""

LOOPS_GROUP_SIZES_GROUP_INDICES = [[3], [3], [], [3]]

ALL_TESTS = [
    (MULTIPLE_RETSUB, MULTIPLE_RETSUB_GROUP_INDICES),
    (SUBROUTINE_BACK_JUMP, SUBROUTINE_BACK_JUMP_GROUP_INDICES),
    (BRANCHING, BRANCHING_GROUP_INDICES),
    (LOOPS, LOOPS_GROUP_INDICES),
    (LOOPS_GROUP_SIZES, LOOPS_GROUP_SIZES_GROUP_INDICES),
]


@pytest.mark.parametrize("test", ALL_TESTS)  # type: ignore
def test_group_indices(test: Tuple[str, List[List[int]]]) -> None:
    code, group_indices = test
    tealer = init_tealer_from_single_contract(code.strip(), "test")
    function = tealer.contracts["test"].functions["test"]

    bbs = order_basic_blocks(function.blocks)
    for b, indices in zip(bbs, group_indices):
        assert function.transaction_context(b).group_indices == indices
