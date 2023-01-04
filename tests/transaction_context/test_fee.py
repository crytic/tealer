from typing import List, Tuple
import pytest

from tealer.teal.parse_teal import parse_teal
from tealer.utils.algorand_constants import MAX_UINT64, MAX_GROUP_SIZE

from tests.utils import order_basic_blocks

BASIC = """
#pragma version 6
txn Fee
int 1000
<=
assert
txn GroupIndex
int 0
==
bz fail_txn
callsub perform_validations
process_txn:
int 1
return
fail_txn:
int 0
return
perform_validations:
int 1
assert
retsub
"""

txn_fees = [1000, 1000, 1000, 0, 1000]
gtxn_fees = [[1000, 1000, 1000, 0, 1000], *[[0] * 5 for _ in range(MAX_GROUP_SIZE - 1)]]

BASIC_LISTS = [txn_fees, gtxn_fees]

NO_CHECKS = """
#pragma version 6
callsub perform_validations
process_txn:
int 1
return
perform_validations:
int 1
assert
retsub
"""

txn_fees = [MAX_UINT64] * 3
gtxn_fees = [[MAX_UINT64] * 3 for _ in range(MAX_GROUP_SIZE)]

NO_CHECKS_LISTS = [txn_fees, gtxn_fees]

GTXN_0 = """
#pragma version 6
txn GroupIndex
int 0
==
bz fail_txn

gtxn 0 Fee
int 1000
>=
bnz fail_txn

callsub perform_validations

process_txn:
    int 1
    return

fail_txn:
    int 0
    return

perform_validations:
    int 1
    assert
    retsub
"""

txn_fees = [MAX_UINT64] * 6
txn_fees[4] = 0  # fail_txn block
gtxn_fees = [
    [
        999,
        999,
        999,
        999,
        0,
        999,
    ],
    *[[0] * 6 for _ in range(MAX_GROUP_SIZE - 1)],
]

GTXN_0_LISTS = [txn_fees, gtxn_fees]

CHECK_IN_SUBROUTINE = """
#pragma version 6
callsub validate_fee
callsub perform_validations

process_txn:
int 1
return

fail_txn:
int 0
return

perform_validations:
int 1
assert
retsub

validate_fee:
    txn Fee
    int 1000
    >
    bnz fail_txn
    retsub
"""

txn_fees = [1000, 1000, 1000, 0, 1000, 1000, 1000]
gtxn_fees = [list(txn_fees) for _ in range(MAX_GROUP_SIZE)]

CHECK_IN_SUBROUTINE_LISTS = [txn_fees, gtxn_fees]

MULTIPLE_GROUP_SIZES_IN_SUBROUTINES = """
#pragma version 6
txn Fee
int 10000
>=
bnz fail_txn
callsub validate_fee
callsub perform_validations

process_txn:
    int 1
    return

fail_txn:
    int 0
    return

perform_validations:
    int 1
    assert
    retsub

validate_fee:
    global GroupSize
    int 2
    ==
    bnz group_size_2

    global GroupSize
    int 1
    ==
    assert
    gtxn 0 Fee
    int 10000
    <=
    assert
    retsub

    group_size_2:
        gtxn 0 Fee
        int 1000
        <
        assert
        gtxn 1 Fee
        int 1000
        <
        bz fail_txn

    retsub
"""

txn_fees = [9999] * 10
txn_fees[4] = 0  # fail_txn block
gtxn_fees = [
    [9999, 9999, 9999, 9999, 0, 9999, 9999, 9999, 999, 999],
    [999, 999, 999, 999, 0, 999, 999, 0, 999, 999, 999],
    *[[0] * 10 for _ in range(MAX_GROUP_SIZE - 2)],
]


MULTIPLE_GROUP_SIZES_IN_SUBROUTINES_LISTS = [txn_fees, gtxn_fees]


CHECKS_IN_MULTIPLE_SUBROUTINES = """
#pragma version 6
global GroupSize
int 2
==
bnz group_size_2

global GroupSize
int 1
==
assert
callsub validate_fee_group_size_1
b process_txn

group_size_2:
    callsub validate_fee_group_size_2
    b process_txn

process_txn:
    callsub perform_validations
    int 1
    return

fail_txn:
    int 0
    return

perform_validations:
    int 1
    assert
    retsub

validate_fee_group_size_1:
    gtxn 0 Fee
    int 10000
    <
    assert
    retsub

validate_fee_group_size_2:
    gtxn 0 Fee
    int 1000
    <=
    assert
    gtxn 1 Fee
    int 1000
    <=
    bz fail_txn
    retsub
"""

txn_fees = [MAX_UINT64] * 12
txn_fees[7] = 0  # fail_txn block
gtxn_fees = [
    # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    [9999, 9999, 9999, 1000, 1000, 9999, 9999, 0, 9999, 9999, 1000, 1000],
    [1000, 0, 0, 1000, 1000, 1000, 1000, 0, 1000, 0, 1000, 1000, 1000],
    *[[0] * 12 for _ in range(MAX_GROUP_SIZE - 2)],
]


CHECKS_IN_MULTIPLE_SUBROUTINES_LISTS = [txn_fees, gtxn_fees]


CHECK_IN_ONE_PATH = """
#pragma version 6
txn RekeyTo
global ZeroAddress
==
bnz rekey_zero

global GroupSize
int 1
==
assert
txn Fee
int 0
==
assert
b process_txn

rekey_zero:
b process_txn

process_txn:
    callsub perform_validations
    int 1
    return

perform_validations:
    int 1
    assert
    retsub
"""

txn_fees = [MAX_UINT64] * 6
txn_fees[1] = 0
gtxn_fees = [list(txn_fees) for _ in range(MAX_GROUP_SIZE)]


CHECK_IN_ONE_PATH_LISTS = [txn_fees, gtxn_fees]


ALL_TESTS = [
    (BASIC, *BASIC_LISTS),
    (NO_CHECKS, *NO_CHECKS_LISTS),
    (GTXN_0, *GTXN_0_LISTS),
    (CHECK_IN_SUBROUTINE, *CHECK_IN_SUBROUTINE_LISTS),
    (MULTIPLE_GROUP_SIZES_IN_SUBROUTINES, *MULTIPLE_GROUP_SIZES_IN_SUBROUTINES_LISTS),
    (CHECKS_IN_MULTIPLE_SUBROUTINES, *CHECKS_IN_MULTIPLE_SUBROUTINES_LISTS),
    (CHECK_IN_ONE_PATH, *CHECK_IN_ONE_PATH_LISTS),
]


@pytest.mark.parametrize("test", ALL_TESTS)  # type: ignore
def test_tx_types_gtxn(test: Tuple[str, List[int], List[List[int]]]) -> None:
    code, max_fees_list, gtxn_fees_list = test

    teal = parse_teal(code.strip())

    bbs = order_basic_blocks(teal.bbs)
    for i, b in enumerate(bbs):
        print(i, repr(b), b.transaction_context.max_fee)
        assert b.transaction_context.max_fee == max_fees_list[i]
        for ind in range(MAX_GROUP_SIZE):
            ctx = b.transaction_context.gtxn_context(ind)
            print(f"D: {ind}, {i}", ctx.max_fee, gtxn_fees_list[ind][i])
            assert ctx.max_fee == gtxn_fees_list[ind][i]
