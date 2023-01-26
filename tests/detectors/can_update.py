from typing import List

from tealer.teal.instructions import instructions
from tealer.teal.instructions import transaction_field
from tealer.detectors.all_detectors import CanUpdate, CanDelete

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


CAN_UPDATE_GROUP_INDEX_0 = """
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

CAN_UPDATE_GROUP_INDEX_0_VULNERABLE_PATHS: List[List[int]] = []

CAN_UPDATE_GROUP_INDEX_1 = """
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

CAN_UPDATE_GROUP_INDEX_1_VULNERABLE_PATHS: List[List[int]] = []

CAN_UPDATE_GROUP_INDEX_2 = """
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

CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS: List[List[int]] = [
    [0, 2, 3, 4, 9],
    [0, 2, 3, 8, 9],
    [0, 2, 7, 8, 9],
]

CAN_UPDATE_GROUP_INDEX_2_X_0 = """
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
    gtxn 1 OnCompletion
    int OptIn
    ==
    ||
    gtxn 1 OnCompletion
    int CloseOut
    ==
    ||                      // (Eq || Eq) || Eq)
    bnz success             // gtxn 1 is one of NoOp, OptIn, CloseOut. gtxn 0 can be UpdateApplication
    gtxn 1 OnCompletion
    int UpdateApplication
    ==
    gtxn 1 OnCompletion
    int DeleteApplication
    ==
    ||
    bnz handle_updateapp        // pattern: (Eq<> || Eq<>)
    int 1
    return
success:
int 1
return
handle_updateapp:
err
"""

CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_0: List[List[int]] = [
    [0, 2, 3, 4],
    [0, 2, 5],
]

CAN_UPDATE_GROUP_INDEX_2_X_1 = """
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
    gtxn 0 OnCompletion
    int NoOp
    ==
    gtxn 0 OnCompletion
    int OptIn
    ==
    ||
    !
    !
    gtxn 0 OnCompletion
    int CloseOut
    ==
    ||
    gtxn 1 OnCompletion
    int NoOp
    ==
    gtxn 1 OnCompletion
    int OptIn
    !=
    !
    ||
    &&                              // gtxn 0 is NoOp or OptIn or CloseOut and gtxn 1 is NoOp or OptIn.
    bnz success                     // Pattern:    (!!(== || ==) || ==) && (== || !(!=))
    gtxn 1 OnCompletion
    int UpdateApplication
    ==
    gtxn 1 OnCompletion
    int DeleteApplication
    ==
    ||
    bnz handle_updateapp
    int 1
    return
success:
int 1
return
handle_updateapp:
err
"""

CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_1: List[List[int]] = [
    [0, 2, 3, 4],
]

CAN_UPDATE_GROUP_INDEX_2_X_2 = """
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
    gtxn 0 OnCompletion
    int NoOp
    ==
    !
    gtxn 0 OnCompletion
    int OptIn
    ==
    !
    &&
    !                       // !(&&(!x, !y)) => x || y
    gtxn 0 OnCompletion
    int CloseOut
    ==
    ||
    gtxn 1 OnCompletion
    int NoOp
    ==
    gtxn 1 OnCompletion
    int OptIn
    !=
    !
    ||
    &&                          // Pattern: (!(&&(!x, !y)) || ==) && (== || !(!=))
    bnz success                 // gtxn 0 is NoOp or OptIn or CloseOut and gtxn 1 is NoOp or OptIn. max group size is 2
    gtxn 1 OnCompletion
    int UpdateApplication
    ==
    gtxn 1 OnCompletion
    int DeleteApplication
    ==
    ||
    bnz handle_updateapp
    int 1
    return
success:
int 1
return
handle_updateapp:
err
"""

CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_2: List[List[int]] = [
    [0, 2, 3, 4],
]

CAN_UPDATE_GROUP_INDEX_2_X_3 = """
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
    gtxn 0 OnCompletion
    int NoOp
    ==
    !
    gtxn 0 OnCompletion
    int OptIn
    ==
    !
    &&
    !                       // !(!x && !y) => x || y
    gtxn 0 OnCompletion
    int CloseOut
    ==
    ||
    gtxn 1 OnCompletion
    int NoOp
    ==
    gtxn 1 OnCompletion
    int OptIn
    !=
    !
    ||
    &&
    bnz success                 // gtxn 0 is NoOp or OptIn or CloseOut and gtxn 1 is NoOp or OptIn.
    gtxn 1 OnCompletion
    int UpdateApplication
    !=
    gtxn 1 OnCompletion
    int DeleteApplication
    !=
    &&
    !                           // !(!x && !y) => x || y. True if gtxn 1 is UpdateApplication or DeleteApplication
    gtxn 0 OnCompletion
    int UpdateApplication
    ==
    gtxn 0 OnCompletion
    int DeleteApplication
    !=
    !
    ||                          // True if gtxn 0 is UpdateApplication or DeleteApplication.
    ||
    bnz handle_updateapp
    int 1
    return
success:
int 1
return
handle_updateapp:
err
"""

CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_3: List[List[int]] = []

CAN_UPDATE_GROUP_INDEX_2_X_4 = """
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
    gtxn 0 OnCompletion
    int NoOp
    ==
    ||                      // depends on a unknown value
    gtxn 0 OnCompletion
    int OptIn
    ==
    ||
    gtxn 0 OnCompletion
    int CloseOut
    ==
    ||                          // gtxn 0 does not have to be NoOp, OptIn, CloseOut. 
    gtxn 1 OnCompletion
    int NoOp
    ==
    gtxn 1 OnCompletion
    int OptIn
    ==
    ||
    &&
    bnz success                 // gtxn 1 is NoOp or OptIn.
    gtxn 1 OnCompletion
    int UpdateApplication
    !=
    gtxn 1 OnCompletion
    int DeleteApplication
    !=
    &&
    !                           // !(!x && !y) => x || y. True if gtxn 1 is UpdateApplication or DeleteApplication
    gtxn 0 OnCompletion
    int UpdateApplication
    ==
    gtxn 0 OnCompletion
    int DeleteApplication
    !=
    !
    ||                          // True if gtxn 0 is UpdateApplication or DeleteApplication.
    ||
    bnz handle_updateapp
    int 1
    return
success:
int 1
return
handle_updateapp:
err
"""

CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_4: List[List[int]] = [
    [0, 2, 5],  # gtxn 0 can be UpdateApplication or DeleteApplication and reach "success:" block
]

CAN_UPDATE_GROUP_INDEX_2_X_5 = """
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
    gtxn 0 OnCompletion
    int NoOp
    ==
    ||                      // depends on a independent value. GTXN_0_TransactionType is different from GTXN_1_TransactionType
    gtxn 0 OnCompletion
    int OptIn
    ==
    ||
    gtxn 0 OnCompletion
    int CloseOut
    ==
    ||                          // gtxn 0 does not have to be NoOp, OptIn, CloseOut. 
    gtxn 1 OnCompletion
    int NoOp
    ==
    gtxn 1 OnCompletion
    int OptIn
    ==
    ||
    &&
    bnz success                 // gtxn 1 is NoOp or OptIn.
    gtxn 1 OnCompletion
    int UpdateApplication
    !=
    gtxn 1 OnCompletion
    int DeleteApplication
    !=
    &&
    !                           // !(!x && !y) => x || y. True if gtxn 1 is UpdateApplication or DeleteApplication
    gtxn 0 OnCompletion
    int UpdateApplication
    ==
    gtxn 0 OnCompletion
    int DeleteApplication
    !=
    !
    ||                          // True if gtxn 0 is UpdateApplication or DeleteApplication.
    ||
    bnz handle_updateapp
    int 1
    return
success:
int 1
return
handle_updateapp:
err
"""

CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_5: List[List[int]] = [
    [0, 2, 5],  # gtxn 0 can be UpdateApplication or DeleteApplication and reach "success:" block
]

CAN_UPDATE_GROUP_INDEX_2_X_6 = """
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
    gtxn 0 OnCompletion
    int NoOp
    ==
    ||                      // depends on a independent value. GTXN_0_TransactionType is different from GTXN_1_TransactionType
    gtxn 0 OnCompletion
    int OptIn
    ==
    ||
    gtxn 0 OnCompletion
    int CloseOut
    ==
    ||                          // gtxn 0 does not have to be NoOp, OptIn, CloseOut. 
    gtxn 1 OnCompletion
    int NoOp
    ==
    gtxn 1 OnCompletion
    int OptIn
    ==
    ||
    &&
    bnz success                 // gtxn 1 is NoOp or OptIn.
    gtxn 1 OnCompletion
    int UpdateApplication
    !=
    gtxn 1 OnCompletion
    int DeleteApplication
    !=
    &&
    !                           // !(!x && !y) => x || y. True if gtxn 1 is UpdateApplication or DeleteApplication
    gtxn 0 OnCompletion
    int UpdateApplication
    ==
    gtxn 0 OnCompletion
    int DeleteApplication
    !=
    !
    ||                          // True if gtxn 0 is UpdateApplication or DeleteApplication.
    ||
    bnz handle_updateapp
    int 1
    return
success:
    gtxn 0 OnCompletion
    int UpdateApplication
    !=
    gtxn 0 OnCompletion
    int DeleteApplication
    !=
    &&
    assert
    int 1
    return
handle_updateapp:
    err
"""

CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_6: List[List[int]] = [
    # gtxn 0 can be UpdateApplication or DeleteApplication and reach "success:" block
    # success block checks for gtxn 0 UpdateApplication and DeleteApplication
]

CAN_UPDATE_GROUP_INDEX_2_X_7 = """
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
    gtxn 0 OnCompletion
    int NoOp
    ==
    ||                      // depends on a independent value. GTXN_0_TransactionType is different from GTXN_1_TransactionType
    gtxn 0 OnCompletion
    int OptIn
    ==
    ||
    gtxn 0 OnCompletion
    int CloseOut
    ==
    ||                          // gtxn 0 does not have to be NoOp, OptIn, CloseOut. 
    gtxn 1 OnCompletion
    int NoOp
    ==
    gtxn 1 OnCompletion
    int OptIn
    ==
    ||
    &&
    bnz success                 // gtxn 1 is NoOp or OptIn.
    gtxn 1 OnCompletion
    int UpdateApplication
    !=
    gtxn 1 OnCompletion
    int DeleteApplication
    !=
    &&
    !                           // !(!x && !y) => x || y. True if gtxn 1 is UpdateApplication or DeleteApplication
    gtxn 0 OnCompletion
    int UpdateApplication
    ==
    gtxn 0 OnCompletion
    int DeleteApplication
    !=
    !
    ||                          // True if gtxn 0 is UpdateApplication or DeleteApplication.
    ||
    bnz handle_updateapp
    int 1
    return
success:
gtxn 0 OnCompletion
int UpdateApplication
!=
txn Fee
int 10000
<
&&                          // gtxn 0 Completion should not be UpdateApplication for this to be true
gtxn 0 OnCompletion
int UpdateApplication
!=
txn Note
byte "Note"
==
&&                          // gtxn 0 Completion should not be UpdateApplication for this to be true
||                          // r = ( x && a ) || ( x && b), x must be True for r to be True, x here is `Neq(gtxn 0 OnCompletion, UpdateApplication)`
assert
int 1
return
handle_updateapp:
err
"""

CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_7: List[List[int]] = [
    # gtxn 0 can be UpdateApplication or DeleteApplication and reach "success:" block
    # success block checks for gtxn 0 OnCompletion is not UpdateApplication
]

CAN_DELETE_GROUP_INDEX_2_VULNERABLE_PATHS_X_7: List[List[int]] = [
    # gtxn 0 can be UpdateApplication or DeleteApplication and reach "success:" block
    # success block checks for gtxn 0 OnCompletion is not UpdateApplication but not DeleteApplication
    [0, 2, 5],
]

new_can_update_tests = [
    (CAN_UPDATE_GROUP_INDEX_0, CanUpdate, CAN_UPDATE_GROUP_INDEX_0_VULNERABLE_PATHS),
    (CAN_UPDATE_GROUP_INDEX_1, CanUpdate, CAN_UPDATE_GROUP_INDEX_1_VULNERABLE_PATHS),
    (CAN_UPDATE_GROUP_INDEX_2, CanUpdate, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS),
    (CAN_UPDATE_GROUP_INDEX_2_X_0, CanUpdate, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_0),
    (CAN_UPDATE_GROUP_INDEX_2_X_0, CanDelete, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_0),
    (CAN_UPDATE_GROUP_INDEX_2_X_1, CanUpdate, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_1),
    (CAN_UPDATE_GROUP_INDEX_2_X_2, CanDelete, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_1),
    (CAN_UPDATE_GROUP_INDEX_2_X_2, CanUpdate, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_2),
    (CAN_UPDATE_GROUP_INDEX_2_X_2, CanDelete, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_2),
    (CAN_UPDATE_GROUP_INDEX_2_X_3, CanUpdate, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_3),
    (CAN_UPDATE_GROUP_INDEX_2_X_3, CanDelete, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_3),
    (CAN_UPDATE_GROUP_INDEX_2_X_4, CanUpdate, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_4),
    (CAN_UPDATE_GROUP_INDEX_2_X_4, CanDelete, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_4),
    (CAN_UPDATE_GROUP_INDEX_2_X_5, CanUpdate, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_5),
    (CAN_UPDATE_GROUP_INDEX_2_X_5, CanDelete, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_5),
    (CAN_UPDATE_GROUP_INDEX_2_X_6, CanUpdate, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_6),
    (CAN_UPDATE_GROUP_INDEX_2_X_6, CanDelete, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_6),
    (CAN_UPDATE_GROUP_INDEX_2_X_7, CanUpdate, CAN_UPDATE_GROUP_INDEX_2_VULNERABLE_PATHS_X_7),
    (CAN_UPDATE_GROUP_INDEX_2_X_7, CanDelete, CAN_DELETE_GROUP_INDEX_2_VULNERABLE_PATHS_X_7),
]
