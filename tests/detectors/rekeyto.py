from typing import List

from tealer.teal.instructions import instructions, transaction_field
from tealer.teal import global_field
from tealer.detectors.all_detectors import MissingRekeyTo

from tests.utils import construct_cfg


MISSING_REKEYTO = """
#pragma version 2
global GroupSize
int 2
gtxn 0 TypeEnum
int axfer
==
&&
gtxn 1 TypeEnum
int pay
==
&&
gtxn 0 RekeyTo
global ZeroAddress
==
&&
bz failed
int 1
return
failed:
    err
"""

ins_list = [
    instructions.Pragma(2),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(2),
    instructions.Gtxn(0, transaction_field.TypeEnum()),
    instructions.Int("axfer"),
    instructions.Eq(),
    instructions.And(),
    instructions.Gtxn(1, transaction_field.TypeEnum()),
    instructions.Int("pay"),
    instructions.Eq(),
    instructions.And(),
    instructions.Gtxn(0, transaction_field.RekeyTo()),
    instructions.Global(global_field.ZeroAddress()),
    instructions.Eq(),
    instructions.And(),
    instructions.BZ("failed"),
    instructions.Int(1),
    instructions.Return(),
    instructions.Label("failed"),
    instructions.Err(),
]

ins_partitions = [(0, 16), (16, 18), (18, 20)]
bbs_links = [(0, 1), (0, 2)]

bbs = construct_cfg(ins_list, ins_partitions, bbs_links)

MISSING_REKEYTO_VULNERABLE_PATHS = [
    [
        bbs[0],
        bbs[1],
    ],  # doesn't check for 2nd transaction. missing Gtxn 1 RekeyTo == Global ZeroAddress
]


MISSING_REKEYTO_LOOP = """
#pragma version 4
global GroupSize
int 2
gtxn 0 TypeEnum
int axfer
==
&&
gtxn 1 TypeEnum
int pay
==
&&
gtxn 0 RekeyTo
global ZeroAddress
==
&&
bz failed
b loop
failed:
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
    instructions.Global(global_field.GroupSize()),
    instructions.Int(2),
    instructions.Gtxn(0, transaction_field.TypeEnum()),
    instructions.Int("axfer"),
    instructions.Eq(),
    instructions.And(),
    instructions.Gtxn(1, transaction_field.TypeEnum()),
    instructions.Int("pay"),
    instructions.Eq(),
    instructions.And(),
    instructions.Gtxn(0, transaction_field.RekeyTo()),
    instructions.Global(global_field.ZeroAddress()),
    instructions.Eq(),
    instructions.And(),
    instructions.BZ("failed"),
    instructions.B("loop"),
    instructions.Label("failed"),
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

ins_partitions = [(0, 16), (16, 17), (17, 19), (19, 24), (24, 27), (27, 30)]
bbs_links = [(0, 1), (0, 2), (1, 3), (3, 4), (3, 5), (4, 3)]

bbs = construct_cfg(ins_list, ins_partitions, bbs_links)

MISSING_REKEYTO_LOOP_VULNERABLE_PATHS = [
    [bbs[0], bbs[1], bbs[3], bbs[5]]  # missing Gtxn 1 RekeyTo == Global ZeroAddress.
]


MISSING_REKEYTO_STATELESS = """
#pragma version 2
txn Receiver
addr 6ZIOGDXGSQSL4YINHLKCHYRV64FSN4LTUIQ6A4VWYK36FXFF42VI2UV7SM
==
bz wrongreceiver
txn Fee
int 10000
<
bz highfee
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
highfee:
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
    instructions.Txn(transaction_field.Fee()),
    instructions.Int(10000),
    instructions.Less(),
    instructions.BZ("highfee"),
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
    instructions.Label("highfee"),
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

MISSING_REKEYTO_STATELESS_VULNERABLE_PATHS = [
    [bbs[0], bbs[1], bbs[2], bbs[3], bbs[4], bbs[5]],
]


missing_rekeyto_tests = [
    (MISSING_REKEYTO, MissingRekeyTo, MISSING_REKEYTO_VULNERABLE_PATHS),
    (MISSING_REKEYTO_LOOP, MissingRekeyTo, MISSING_REKEYTO_LOOP_VULNERABLE_PATHS),
    (MISSING_REKEYTO_STATELESS, MissingRekeyTo, MISSING_REKEYTO_STATELESS_VULNERABLE_PATHS),
]


MISSING_REKEYTO_GROUP_INDEX_0 = """
#pragma version 6
txn GroupIndex
int 0
!=
bnz index_not_0
gtxn 0 RekeyTo  // index must be 0
global ZeroAddress
==
assert
b process_txn
index_not_0:
global GroupSize // index is not zero and groupsize is 2. So, txn index must be 1
int 2
==
assert
gtxn 1 RekeyTo
global ZeroAddress
==
assert
process_txn:
int 1
return
"""

MISSING_REKEYTO_GROUP_INDEX_0_VULNERABLE_PATHS: List[List[int]] = []  # not vulnerable


MISSING_REKEYTO_GROUP_INDEX_1 = """
#pragma version 6
txn GroupIndex
int 0
!=
bnz index_not_0
gtxn 0 RekeyTo  // index must be 0
addr AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEVAL4QAJS7JHB4
==
assert
b process_txn
index_not_0:
global GroupSize    // index is not zero and groupsize is **3**. So, txn index can be 1 or 2
int 3
==
assert
gtxn 1 RekeyTo     // only checks gtxn 1. so, is vulnerable if txn index is 2
global ZeroAddress
==
assert
process_txn:
int 1
return
"""

MISSING_REKEYTO_GROUP_INDEX_1_VULNERABLE_PATHS: List[List[int]] = [[0, 2, 3]]


MISSING_REKEYTO_GROUP_INDEX_2 = """
#pragma version 6
global GroupSize
int 2
!=
bnz group_size_is_not_2
gtxn 0 RekeyTo  // group size is 2. so check index 0 and 1.
addr SKSOWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEVAL4QAJS7JHB4
==
assert
gtxn 1 RekeyTo
global ZeroAddress
==
assert
b process_txn
group_size_is_not_2:
global GroupSize    // group_size is not 2
int 3
<
assert              // group_size is less than 3 and is not 2. So, it must be 1 => index must be 0
gtxn 0 RekeyTo    
global ZeroAddress
!=
bnz fail_txn
process_txn:
int 1
return
fail_txn:
err
"""

MISSING_REKEYTO_GROUP_INDEX_2_VULNERABLE_PATHS: List[List[int]] = []  # not vulnerable


MISSING_REKEYTO_GROUP_INDEX_3 = """
#pragma version 6
global GroupSize
int 2
!=
bnz group_size_is_not_2
gtxn 0 RekeyTo  // group size is 2. so check index 0 and 1.
global ZeroAddress
==
assert
gtxn 1 RekeyTo
global ZeroAddress
==
assert
b process_txn
group_size_is_not_2:
global GroupSize    // group_size is not 2
int 3
==
assert              // group_size is 3. check at indices 0, 1, 2
gtxn 0 RekeyTo    
global ZeroAddress
==
bz fail_txn
gtxn 2 RekeyTo
global ZeroAddress
==
bz fail_txn
gtxn 1 RekeyTo
global ZeroAddress
==
bz fail_txn
process_txn:
int 1
return
fail_txn:
err
"""

MISSING_REKEYTO_GROUP_INDEX_3_VULNERABLE_PATHS: List[List[int]] = []  # not vulnerable

new_missing_rekeyto_tests = [
    (MISSING_REKEYTO_GROUP_INDEX_0, MissingRekeyTo, MISSING_REKEYTO_GROUP_INDEX_0_VULNERABLE_PATHS),
    (MISSING_REKEYTO_GROUP_INDEX_1, MissingRekeyTo, MISSING_REKEYTO_GROUP_INDEX_1_VULNERABLE_PATHS),
    (MISSING_REKEYTO_GROUP_INDEX_2, MissingRekeyTo, MISSING_REKEYTO_GROUP_INDEX_2_VULNERABLE_PATHS),
    (MISSING_REKEYTO_GROUP_INDEX_3, MissingRekeyTo, MISSING_REKEYTO_GROUP_INDEX_3_VULNERABLE_PATHS),
]
