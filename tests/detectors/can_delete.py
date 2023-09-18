from typing import List, Tuple, Type

from tealer.teal.instructions import instructions
from tealer.teal.instructions import transaction_field
from tealer.detectors.abstract_detector import AbstractDetector
from tealer.detectors.all_detectors import IsDeletable, CanCloseAccount, CanCloseAsset

from tests.utils import construct_cfg


CAN_DELETE = """
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
    int UpdateApplication
    ==
    bnz handle_updateapp
    int 1
    return
handle_noop:
handle_optin:
handle_closeout:
int 1
return
handle_updateapp:
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
    instructions.Int("UpdateApplication"),
    instructions.Eq(),
    instructions.BNZ("handle_updateapp"),
    instructions.Int(1),
    instructions.Return(),
    instructions.Label("handle_noop"),
    instructions.Label("handle_optin"),
    instructions.Label("handle_closeout"),
    instructions.Int(1),
    instructions.Return(),
    instructions.Label("handle_updateapp"),
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

CAN_DELETE_VULNERABLE_PATHS = [
    [bbs[0], bbs[2], bbs[3], bbs[4], bbs[5], bbs[6]],
]


CAN_DELETE_LOOP = """
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
    int UpdateApplication
    ==
    bnz handle_updateapp
    b loop
handle_noop:
handle_optin:
handle_closeout:
int 1
return
handle_updateapp:
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
    instructions.Int("UpdateApplication"),
    instructions.Eq(),
    instructions.BNZ("handle_updateapp"),
    instructions.B("loop"),
    instructions.Label("handle_noop"),
    instructions.Label("handle_optin"),
    instructions.Label("handle_closeout"),
    instructions.Int(1),
    instructions.Return(),
    instructions.Label("handle_updateapp"),
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

CAN_DELETE_LOOP_VULNERABLE_PATHS = [
    [bbs[0], bbs[2], bbs[3], bbs[4], bbs[5], bbs[6], bbs[11], bbs[13]],
]


can_delete_tests = [
    (CAN_DELETE, IsDeletable, CAN_DELETE_VULNERABLE_PATHS),
    (CAN_DELETE_LOOP, IsDeletable, CAN_DELETE_LOOP_VULNERABLE_PATHS),
]


CAN_DELETE_GROUP_INDEX_0 = """
#pragma version 6
txn GroupIndex
int 0
==
assert
int 0
gtxn 0 ApplicationID
==
bz not_creation
int 1
return
not_creation:
    gtxn 0 OnCompletion
    int NoOp
    ==
    bnz handle_noop
    gtxn 0 OnCompletion
    int OptIn
    ==
    bnz handle_optin
    gtxn 0 OnCompletion
    int CloseOut
    ==
    bnz handle_closeout
    gtxn 0 OnCompletion
    int UpdateApplication
    ==
    bnz handle_updateapp
    int 1
    return
handle_noop:
handle_optin:
handle_closeout:
int 1
return
handle_updateapp:
err
"""

CAN_DELETE_GROUP_INDEX_0_VULNERABLE_PATHS: List[List[int]] = [[0, 2, 3, 4, 5, 6]]

CAN_DELETE_GROUP_INDEX_1 = """
#pragma version 6
global GroupSize
int 1
==
assert
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
    gtxn 0 OnCompletion
    int OptIn
    ==
    bnz handle_optin
    gtxn 0 OnCompletion
    int CloseOut
    ==
    bnz handle_closeout
    gtxn 0 OnCompletion
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

CAN_DELETE_GROUP_INDEX_1_VULNERABLE_PATHS: List[List[int]] = []

CAN_DELETE_GROUP_INDEX_2 = """
#pragma version 6
global GroupSize
int 2
==
assert
int 0
txn ApplicationID
==
bz not_creation
int 1
return
not_creation:
    gtxn 1 OnCompletion
    int NoOp
    ==
    bnz handle_noop
    gtxn 1 OnCompletion
    int OptIn
    ==
    bnz handle_optin
    gtxn 1 OnCompletion
    int CloseOut
    ==
    bz handle_closeout
    gtxn 0 OnCompletion
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

CAN_DELETE_GROUP_INDEX_2_VULNERABLE_PATHS: List[List[int]] = [
    [0, 2, 3, 4, 9],
    [0, 2, 3, 8, 9],
    [0, 2, 7, 8, 9],
]

new_can_delete_tests: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    (CAN_DELETE_GROUP_INDEX_0, IsDeletable, CAN_DELETE_GROUP_INDEX_0_VULNERABLE_PATHS),
    (CAN_DELETE_GROUP_INDEX_1, IsDeletable, CAN_DELETE_GROUP_INDEX_1_VULNERABLE_PATHS),
    (CAN_DELETE_GROUP_INDEX_2, IsDeletable, CAN_DELETE_GROUP_INDEX_2_VULNERABLE_PATHS),
    (CAN_DELETE, CanCloseAccount, []),
    (CAN_DELETE_LOOP, CanCloseAccount, []),
    (CAN_DELETE_GROUP_INDEX_0, CanCloseAccount, []),
    (CAN_DELETE_GROUP_INDEX_1, CanCloseAccount, []),
    (CAN_DELETE_GROUP_INDEX_2, CanCloseAccount, []),
    (CAN_DELETE, CanCloseAsset, []),
    (CAN_DELETE_LOOP, CanCloseAsset, []),
    (CAN_DELETE_GROUP_INDEX_0, CanCloseAsset, []),
    (CAN_DELETE_GROUP_INDEX_1, CanCloseAsset, []),
    (CAN_DELETE_GROUP_INDEX_2, CanCloseAsset, []),
]
