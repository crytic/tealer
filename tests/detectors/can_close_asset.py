from tealer.teal.instructions import instructions, transaction_field
from tealer.detectors.all_detectors import CanCloseAsset
from tealer.teal import global_field

from tests.utils import construct_cfg


CAN_CLOSE_ASSET = """
#pragma version 2
txn Receiver
addr 6ZIOGDXGSQSL4YINHLKCHYRV64FSN4LTUIQ6A4VWYK36FXFF42VI2UV7SM
==
bz wrongreceiver 
txn Fee
int 10000
<
bz highfee
txn RekeyTo
global ZeroAddress
==
bz rekeying
txn CloseRemainderTo
global ZeroAddress
==
bz closing_account
global GroupSize
int 1
==
bz unexpected_group_size
int 1
return
wrongreceiver:
highfee:
rekeying:
closing_account:
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
    instructions.Txn(transaction_field.RekeyTo()),
    instructions.Global(global_field.ZeroAddress()),
    instructions.Eq(),
    instructions.BZ("rekeying"),
    instructions.Txn(transaction_field.CloseRemainderTo()),
    instructions.Global(global_field.ZeroAddress()),
    instructions.Eq(),
    instructions.BZ("closing_account"),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(1),
    instructions.Eq(),
    instructions.BZ("unexpected_group_size"),
    instructions.Int(1),
    instructions.Return(),
    instructions.Label("wrongreceiver"),
    instructions.Label("highfee"),
    instructions.Label("rekeying"),
    instructions.Label("closing_account"),
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

CAN_CLOSE_ASSET_VULNERABLE_PATHS = [
    [bbs[0], bbs[1], bbs[2], bbs[3], bbs[4], bbs[5]],
]


CAN_CLOSE_ASSET_LOOP = """
#pragma version 4
txn Receiver
addr 6ZIOGDXGSQSL4YINHLKCHYRV64FSN4LTUIQ6A4VWYK36FXFF42VI2UV7SM
==
bz wrongreceiver 
txn Fee
int 10000
<
bz highfee
txn RekeyTo
global ZeroAddress
==
bz rekeying
txn CloseRemainderTo
global ZeroAddress
==
bz closing_account
global GroupSize
int 1
==
bz unexpected_group_size
int 0
b loop
wrongreceiver:
highfee:
rekeying:
closing_account:
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
    instructions.Txn(transaction_field.Fee()),
    instructions.Int(10000),
    instructions.Less(),
    instructions.BZ("highfee"),
    instructions.Txn(transaction_field.RekeyTo()),
    instructions.Global(global_field.ZeroAddress()),
    instructions.Eq(),
    instructions.BZ("rekeying"),
    instructions.Txn(transaction_field.CloseRemainderTo()),
    instructions.Global(global_field.ZeroAddress()),
    instructions.Eq(),
    instructions.BZ("closing_account"),
    instructions.Global(global_field.GroupSize()),
    instructions.Int(1),
    instructions.Eq(),
    instructions.BZ("unexpected_group_size"),
    instructions.Int(0),
    instructions.B("loop"),
    instructions.Label("wrongreceiver"),
    instructions.Label("highfee"),
    instructions.Label("rekeying"),
    instructions.Label("closing_account"),
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
    (6, 7),
    (7, 8),
    (8, 9),
    (9, 10),
    (5, 11),
    (11, 12),
    (11, 13),
    (12, 11),
]

bbs = construct_cfg(ins_list, ins_partitions, bbs_links)

CAN_CLOSE_ASSET_LOOP_VULNERABLE_PATHS = [
    [bbs[0], bbs[1], bbs[2], bbs[3], bbs[4], bbs[5], bbs[11], bbs[13]]
]


can_close_asset_tests = [
    (CAN_CLOSE_ASSET, CanCloseAsset, CAN_CLOSE_ASSET_VULNERABLE_PATHS),
    (CAN_CLOSE_ASSET_LOOP, CanCloseAsset, CAN_CLOSE_ASSET_LOOP_VULNERABLE_PATHS),
]
