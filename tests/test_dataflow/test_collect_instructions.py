from typing import Tuple

import pytest

from tealer.analyses.dataflow.collect_instructions import CollectInstructions
from tealer.teal.instructions.instructions import Return
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
    int 4
    callsub is_even
    return
"""

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

ALL_TESTS = [(MULTIPLE_RETSUB, 27), (SUBROUTINE_BACK_JUMP, 20), (BRANCHING, 22), (LOOPS, 26)]


@pytest.mark.parametrize("test", ALL_TESTS)
def test_group_indices(test: Tuple[str, int]) -> None:
    teal = parse_teal(test[0])

    ci = CollectInstructions(teal)
    ci.run_analysis()
    bb_out = ci.result()

    # We assume that the return node is always the last in instructions
    # This might not hold if we change the parsing
    return_node = teal.instructions[-1]
    assert isinstance(return_node, Return)
    assert return_node.bb

    values = bb_out[return_node.bb].values
    assert isinstance(values, set)
    assert len(values) == test[1]
