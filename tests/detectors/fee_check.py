from typing import List

from tealer.teal.instructions import instructions, transaction_field
from tealer.detectors.all_detectors import MissingFeeCheck
from tealer.teal import global_field

from tests.utils import construct_cfg


MISSING_FEE_CHECK = """
#pragma version 2
txn Receiver
addr 6ZIOGDXGSQSL4YINHLKCHYRV64FSN4LTUIQ6A4VWYK36FXFF42VI2UV7SM
==
bz wrongreceiver 
txn RekeyTo
global ZeroAddress
==
bz rekeying
txn CloseRemainderTo
global ZeroAddress
==
bz closing_account
txn AssetCloseTo
global ZeroAddress
==
bz closing_asset
global GroupSize
int 1
==
bz unexpected_group_size
int 1
return
wrongreceiver:
rekeying:
closing_account:
closing_asset:
unexpected_group_size:
    err
"""

ins_list = [
    instructions.Pragma(2),
    instructions.Txn(transaction_field.Receiver()),
    instructions.Addr("6ZIOGDXGSQSL4YINHLKCHYRV64FSN4LTUIQ6A4VWYK36FXFF42VI2UV7SM"),
    instructions.Eq(),
    instructions.BZ("wrongreceiver"),
    instructions.Txn(transaction_field.RekeyTo()),
    instructions.Global(global_field.ZeroAddress()),
    instructions.Eq(),
    instructions.BZ("rekeying"),
    instructions.Txn(transaction_field.CloseRemainderTo()),
    instructions.Global(global_field.ZeroAddress()),
    instructions.Eq(),
    instructions.BZ("closing_account"),
    instructions.Txn(transaction_field.AssetCloseTo()),
    instructions.Global(global_field.ZeroAddress()),
    instructions.Eq(),
    instructions.BZ("closing_asset"),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(1),
    instructions.Eq(),
    instructions.BZ("unexpected_group_size"),
    instructions.Int(1),
    instructions.Return(),
    instructions.Label("wrongreceiver"),
    instructions.Label("rekeying"),
    instructions.Label("closing_account"),
    instructions.Label("closing_asset"),
    instructions.Label("unexpected_group_size"),
    instructions.Err(),
]

ins_partitions = [
    (0, 5),
    (5, 9),
    (9, 13),
    (13, 17),
    (17, 21),
    (21, 23),
    (23, 24),
    (24, 25),
    (25, 26),
    (26, 27),
    (27, 29),
]

bbs_links = [
    (0, 1),
    (0, 6),
    (1, 2),
    (1, 7),
    (2, 3),
    (2, 8),
    (3, 4),
    (3, 9),
    (4, 5),
    (4, 10),
    (6, 7),
    (7, 8),
    (8, 9),
    (9, 10),
]

bbs = construct_cfg(ins_list, ins_partitions, bbs_links)

MISSING_FEE_CHECK_VULNERABLE_PATHS = [
    [bbs[0], bbs[1], bbs[2], bbs[3], bbs[4], bbs[5]],
]


MISSING_FEE_CHECK_LOOP = """
#pragma version 4
txn Receiver
addr 6ZIOGDXGSQSL4YINHLKCHYRV64FSN4LTUIQ6A4VWYK36FXFF42VI2UV7SM
==
bz wrongreceiver 
txn RekeyTo
global ZeroAddress
==
bz rekeying
txn CloseRemainderTo
global ZeroAddress
==
bz closing_account
txn AssetCloseTo
global ZeroAddress
==
bz closing_asset
global GroupSize
int 1
==
bz unexpected_group_size
int 0
b loop
wrongreceiver:
rekeying:
closing_account:
closing_asset:
unexpected_group_size:
    err
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
    instructions.Pragma(4),
    instructions.Txn(transaction_field.Receiver()),
    instructions.Addr("6ZIOGDXGSQSL4YINHLKCHYRV64FSN4LTUIQ6A4VWYK36FXFF42VI2UV7SM"),
    instructions.Eq(),
    instructions.BZ("wrongreceiver"),
    instructions.Txn(transaction_field.RekeyTo()),
    instructions.Global(global_field.ZeroAddress()),
    instructions.Eq(),
    instructions.BZ("rekeying"),
    instructions.Txn(transaction_field.CloseRemainderTo()),
    instructions.Global(global_field.ZeroAddress()),
    instructions.Eq(),
    instructions.BZ("closing_account"),
    instructions.Txn(transaction_field.AssetCloseTo()),
    instructions.Global(global_field.ZeroAddress()),
    instructions.Eq(),
    instructions.BZ("closing_asset"),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(1),
    instructions.Eq(),
    instructions.BZ("unexpected_group_size"),
    instructions.Int(0),
    instructions.B("loop"),
    instructions.Label("wrongreceiver"),
    instructions.Label("rekeying"),
    instructions.Label("closing_account"),
    instructions.Label("closing_asset"),
    instructions.Label("unexpected_group_size"),
    instructions.Err(),
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

ins_partitions = [
    (0, 5),
    (5, 9),
    (9, 13),
    (13, 17),
    (17, 21),
    (21, 23),
    (23, 24),
    (24, 25),
    (25, 26),
    (26, 27),
    (27, 29),
    (29, 34),
    (34, 37),
    (37, 40),
]

bbs_links = [
    (0, 1),
    (0, 6),
    (1, 2),
    (1, 7),
    (2, 3),
    (2, 8),
    (3, 4),
    (3, 9),
    (4, 5),
    (4, 10),
    (5, 11),
    (11, 12),
    (11, 13),
    (12, 11),
]

bbs = construct_cfg(ins_list, ins_partitions, bbs_links)

MISSING_FEE_CHECK_LOOP_VULNERABLE_PATHS = [
    [bbs[0], bbs[1], bbs[2], bbs[3], bbs[4], bbs[5], bbs[11], bbs[13]]
]


missing_fee_check_tests = [
    (MISSING_FEE_CHECK, MissingFeeCheck, MISSING_FEE_CHECK_VULNERABLE_PATHS),
    (MISSING_FEE_CHECK_LOOP, MissingFeeCheck, MISSING_FEE_CHECK_LOOP_VULNERABLE_PATHS),
]


CHECKS_IN_ONE_BRANCH = """


"""

BASIC_1 = """
#pragma version 6
txn Fee
int 1000
>=                          // Fee >= 1000
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
    txn Fee
    int 10000
    >=                          // Fee >= 10000; Fee can be any value greater than 10000
    bz fail_txn
    
    retsub
"""

BASIC_1_VULNERABLE_PATHS: List[List[int]] = [[0, 1, 4, 5, 2]]

BASIC_2 = """
#pragma version 6
txn Fee
int 1000
>=                          // Fee >= 1000
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
    txn Fee
    int 10000
    <=                          // Fee <= 10000
    bz fail_txn

    retsub
"""

BASIC_2_VULNERABLE_PATHS: List[List[int]] = []


UNKNOWN_FEE = """
#pragma version 6
txn Fee
global MinTxnFee
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

UNKNOWN_FEE_VULNERABLE_PATHS: List[List[int]] = []

BASIC_3 = """
#pragma version 6

callsub perform_validations

process_txn:
    int 1
    return

perform_validations:
    txn GroupIndex
    int 5
    ==
    gtxn 5 Fee
    global MinTxnFee
    int 5
    *
    ==
    &&
    assert
    retsub
"""

BASIC_3_VULNERABLE_PATHS: List[List[int]] = []


LARGE_FEE = """
#pragma version 6       // 0
callsub validate_fee

callsub perform_validations     // 1

process_txn:                    // 2
    int 1
    return

fail_txn:                       // 3
    int 0
    return

perform_validations:            // 4
    int 1
    assert
    retsub

validate_fee:                   // 5
    txn Fee
    int 10000000000             // Fee is much larger than maximum transaction cost
    >
    bnz fail_txn

    retsub                      // 6
"""


LARGE_FEE_VULNERABLE_PATHS: List[List[int]] = [
    [0, 5, 6, 1, 4, 2],
]

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
    gtxn 0 Fee
    int 10000
    <=
    &&
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

MULTIPLE_GROUP_SIZES_VULNERABLE_PATHS: List[List[int]] = []


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

CHECKS_IN_MULTIPLE_SUBROUTINES_VULNERABLE_PATHS: List[List[int]] = []


CHECKS_IN_MULTIPLE_SUBROUTINES_2 = """
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
    global MinTxnFee
    int 3
    *
    <=                  // detection of this pattern is possible because of StackValue emulation/analysis
    assert
    gtxn 1 Fee
    int 1000
    int 4
    *
    <=
    bz fail_txn
    retsub
"""


CHECKS_IN_MULTIPLE_SUBROUTINES_2_VULNERABLE_PATHS: List[List[int]] = []


CHECK_IN_ONE_PATH = """
#pragma version 6
txn RekeyTo
global ZeroAddress
==
global GroupSize
int 1
==
&&
txn Fee
int 0
==
&&
bnz process_txn

fail:
    err

process_txn:
    callsub perform_validations
    int 1
    return

perform_validations:
    int 1
    assert
    retsub
"""

CHECK_IN_ONE_PATH_VULNERABLE_PATHS: List[List[int]] = []

# The commented out test contracts contain a basic block which is part of __main__ CFG and a subroutine.
# TODO: Handle that case
new_missing_fee_tests = [
    # (BASIC_1, MissingFeeCheck, BASIC_1_VULNERABLE_PATHS),
    # (BASIC_2, MissingFeeCheck, BASIC_2_VULNERABLE_PATHS),
    (UNKNOWN_FEE, MissingFeeCheck, UNKNOWN_FEE_VULNERABLE_PATHS),
    (BASIC_3, MissingFeeCheck, BASIC_3_VULNERABLE_PATHS),
    (LARGE_FEE, MissingFeeCheck, LARGE_FEE_VULNERABLE_PATHS),
    # (MULTIPLE_GROUP_SIZES_IN_SUBROUTINES, MissingFeeCheck, MULTIPLE_GROUP_SIZES_VULNERABLE_PATHS),
    (
        CHECKS_IN_MULTIPLE_SUBROUTINES,
        MissingFeeCheck,
        CHECKS_IN_MULTIPLE_SUBROUTINES_VULNERABLE_PATHS,
    ),
    (
        CHECKS_IN_MULTIPLE_SUBROUTINES_2,
        MissingFeeCheck,
        CHECKS_IN_MULTIPLE_SUBROUTINES_2_VULNERABLE_PATHS,
    ),
    (CHECK_IN_ONE_PATH, MissingFeeCheck, CHECK_IN_ONE_PATH_VULNERABLE_PATHS),
]
