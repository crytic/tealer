from tealer.teal.instructions import instructions
from tealer.teal.instructions import transaction_field
from tealer.detectors.all_detectors import CanUpdate

from tests.utils import construct_cfg


CAN_UPDATE = """
#pragma version 2
int 0
txn ApplicationID
==
bz not_creation
int 1
return
not_creation:
    txn OnCompletion
    int NoOp
    ==
    bnz handle_noop
    txn OnCompletion
    int OptIn
    ==
    bnz handle_optin
    txn OnCompletion
    int CloseOut
    ==
    bnz handle_closeout
    txn OnCompletion
    int DeleteApplication
    ==
    bnz handle_deleteapp
    int 1
    return
handle_noop:
handle_optin:
handle_closeout:
int 1
return
handle_deleteapp:
err
"""

ins_list = [
    instructions.Pragma(2),
    instructions.Int(0),
    instructions.Txn(transaction_field.ApplicationID()),
    instructions.Eq(),
    instructions.BZ("not_creation"),
    instructions.Int(1),
    instructions.Return(),
    instructions.Label("not_creation"),
    instructions.Txn(transaction_field.OnCompletion()),
    instructions.Int("NoOp"),
    instructions.Eq(),
    instructions.BNZ("handle_noop"),
    instructions.Txn(transaction_field.OnCompletion()),
    instructions.Int("OptIn"),
    instructions.Eq(),
    instructions.BNZ("handle_optin"),
    instructions.Txn(transaction_field.OnCompletion()),
    instructions.Int("CloseOut"),
    instructions.Eq(),
    instructions.BNZ("handle_closeout"),
    instructions.Txn(transaction_field.OnCompletion()),
    instructions.Int("DeleteApplication"),
    instructions.Eq(),
    instructions.BNZ("handle_deleteapp"),
    instructions.Int(1),
    instructions.Return(),
    instructions.Label("handle_noop"),
    instructions.Label("handle_optin"),
    instructions.Label("handle_closeout"),
    instructions.Int(1),
    instructions.Return(),
    instructions.Label("handle_deleteapp"),
    instructions.Err(),
]

ins_partitions = [
    (0, 5),
    (5, 7),
    (7, 12),
    (12, 16),
    (16, 20),
    (20, 24),
    (24, 26),
    (26, 27),
    (27, 28),
    (28, 31),
    (31, 33),
]

bbs_links = [
    (0, 1),
    (0, 2),
    (2, 3),
    (2, 7),
    (3, 4),
    (3, 8),
    (4, 5),
    (4, 9),
    (5, 6),
    (5, 10),
    (7, 8),
    (8, 9),
]

bbs = construct_cfg(ins_list, ins_partitions, bbs_links)

CAN_UPDATE_VULNERABLE_PATHS = [
    [bbs[0], bbs[2], bbs[3], bbs[4], bbs[5], bbs[6]],
]


CAN_UPDATE_LOOP = """
#pragma version 4
int 0
txn ApplicationID
==
bz not_creation
int 1
return
not_creation:
    txn OnCompletion
    int NoOp
    ==
    bnz handle_noop
    txn OnCompletion
    int OptIn
    ==
    bnz handle_optin
    txn OnCompletion
    int CloseOut
    ==
    bnz handle_closeout
    txn OnCompletion
    int DeleteApplication
    ==
    bnz handle_deleteapp
    b loop
handle_noop:
handle_optin:
handle_closeout:
int 1
return
handle_deleteapp:
err
loop:
    load 0
    int 5
    <
    bz end
    load 0
    int 1
    +
    store 0
    b loop
end:
    int 1
    return
"""

ins_list = [
    instructions.Pragma(4),
    instructions.Int(0),
    instructions.Txn(transaction_field.ApplicationID()),
    instructions.Eq(),
    instructions.BZ("not_creation"),
    instructions.Int(1),
    instructions.Return(),
    instructions.Label("not_creation"),
    instructions.Txn(transaction_field.OnCompletion()),
    instructions.Int("NoOp"),
    instructions.Eq(),
    instructions.BNZ("handle_noop"),
    instructions.Txn(transaction_field.OnCompletion()),
    instructions.Int("OptIn"),
    instructions.Eq(),
    instructions.BNZ("handle_optin"),
    instructions.Txn(transaction_field.OnCompletion()),
    instructions.Int("CloseOut"),
    instructions.Eq(),
    instructions.BNZ("handle_closeout"),
    instructions.Txn(transaction_field.OnCompletion()),
    instructions.Int("DeleteApplication"),
    instructions.Eq(),
    instructions.BNZ("handle_deleteapp"),
    instructions.B("loop"),
    instructions.Label("handle_noop"),
    instructions.Label("handle_optin"),
    instructions.Label("handle_closeout"),
    instructions.Int(1),
    instructions.Return(),
    instructions.Label("handle_deleteapp"),
    instructions.Err(),
    instructions.Label("loop"),
    instructions.Load(0),
    instructions.Int(5),
    instructions.Less(),
    instructions.BZ("end"),
    instructions.Load(0),
    instructions.Int(1),
    instructions.Add(),
    instructions.Store(0),
    instructions.B("loop"),
    instructions.Label("end"),
    instructions.Int(1),
    instructions.Return(),
]

ins_partitions = [
    (0, 5),
    (5, 7),
    (7, 12),
    (12, 16),
    (16, 20),
    (20, 24),
    (24, 25),
    (25, 26),
    (26, 27),
    (27, 30),
    (30, 32),
    (32, 37),
    (37, 42),
    (42, 45),
]

bbs_links = [
    (0, 1),
    (0, 2),
    (2, 3),
    (2, 7),
    (3, 4),
    (3, 8),
    (4, 5),
    (4, 9),
    (5, 6),
    (5, 10),
    (7, 8),
    (8, 9),
    (6, 11),
    (11, 12),
    (11, 13),
    (12, 11),
]

bbs = construct_cfg(ins_list, ins_partitions, bbs_links)

CAN_UPDATE_LOOP_VULNERABLE_PATHS = [
    [bbs[0], bbs[2], bbs[3], bbs[4], bbs[5], bbs[6], bbs[11], bbs[13]],
]


can_update_tests = [
    (CAN_UPDATE, CanUpdate, CAN_UPDATE_VULNERABLE_PATHS),
    (CAN_UPDATE_LOOP, CanUpdate, CAN_UPDATE_LOOP_VULNERABLE_PATHS),
]
