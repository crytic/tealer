
from tealer.utils.teal_enums import TealerTransactionType
from typing import List, Tuple
import pytest

from tealer.teal.parse_teal import parse_teal

from tests.utils import order_basic_blocks


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

CAN_UPDATE_TX_TYPES = [
    [TealerTransactionType.ApplNoOp, TealerTransactionType.ApplOptIn, TealerTransactionType.ApplCloseOut, TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication, TealerTransactionType.ApplCreation],
    [TealerTransactionType.ApplCreation],
    [TealerTransactionType.ApplNoOp, TealerTransactionType.ApplOptIn, TealerTransactionType.ApplCloseOut, TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplOptIn, TealerTransactionType.ApplCloseOut, TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplCloseOut, TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplNoOp],
    [TealerTransactionType.ApplNoOp, TealerTransactionType.ApplOptIn],
    [TealerTransactionType.ApplNoOp, TealerTransactionType.ApplOptIn, TealerTransactionType.ApplCloseOut],
    [],
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
    b loop
handle_noop:
handle_optin:
handle_closeout:
int 1
return
loop:
    txn OnCompletion
    int DeleteApplication
    !=
    assert
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

CAN_UPDATE_LOOP_TX_TYPES = [
    [TealerTransactionType.ApplNoOp, TealerTransactionType.ApplOptIn, TealerTransactionType.ApplCloseOut, TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication, TealerTransactionType.ApplCreation],
    [TealerTransactionType.ApplCreation],
    [TealerTransactionType.ApplNoOp, TealerTransactionType.ApplOptIn, TealerTransactionType.ApplCloseOut, TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplOptIn, TealerTransactionType.ApplCloseOut, TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplCloseOut, TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplNoOp],
    [TealerTransactionType.ApplNoOp, TealerTransactionType.ApplOptIn],
    [TealerTransactionType.ApplNoOp, TealerTransactionType.ApplOptIn, TealerTransactionType.ApplCloseOut],
    [TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
]

SUBROUTINE = """
#pragma version 5
b main
push_zero:
    int 0
    retsub
is_even:
    int 2
    %
    bz return_1
    callsub push_zero
    retsub
return_1:
    int 1
    retsub
main:
    int 4
    bz path_1
    b path_2
path_1:
   txn OnCompletion
   int UpdateApplication
   ==
   assert
   callsub is_even
   int 1
   return
path_2:
   txn OnCompletion
   int DeleteApplication
   ==
   assert
   callsub is_even
   int 1
   int 1
   return
"""

SUBROUTINE_TX_TYPES = [
    [TealerTransactionType.ApplUpdateApplication, TealerTransactionType.ApplDeleteApplication],
    [TealerTransactionType.ApplUpdateApplication, TealerTransactionType.ApplDeleteApplication],
    [TealerTransactionType.ApplUpdateApplication, TealerTransactionType.ApplDeleteApplication],
    [TealerTransactionType.ApplUpdateApplication, TealerTransactionType.ApplDeleteApplication],
    [TealerTransactionType.ApplUpdateApplication, TealerTransactionType.ApplDeleteApplication],
    [TealerTransactionType.ApplUpdateApplication, TealerTransactionType.ApplDeleteApplication],
    [TealerTransactionType.ApplUpdateApplication, TealerTransactionType.ApplDeleteApplication],
    [TealerTransactionType.ApplDeleteApplication],
    [TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplDeleteApplication],
    [TealerTransactionType.ApplDeleteApplication],
]


CAN_UPDATE_GTXN_0 = """
#pragma version 2
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

CAN_UPDATE_LOOP_GTXN_0 = """
#pragma version 4
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
    b loop
handle_noop:
handle_optin:
handle_closeout:
int 1
return
loop:
    gtxn 0 OnCompletion
    int DeleteApplication
    !=
    assert
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


ALL_TESTS_TXN = [
    (CAN_UPDATE, CAN_UPDATE_TX_TYPES, -1),
    (CAN_UPDATE_LOOP, CAN_UPDATE_LOOP_TX_TYPES, -1),
    (SUBROUTINE, SUBROUTINE_TX_TYPES, -1),
    (CAN_UPDATE_GTXN_0, CAN_UPDATE_TX_TYPES, 0),
    (CAN_UPDATE_LOOP_GTXN_0, CAN_UPDATE_LOOP_TX_TYPES, 0),
]

@pytest.mark.parametrize("test", ALL_TESTS_TXN)  # type: ignore
def test_tx_types(test: Tuple[str, List[List[int]]]) -> None:
    code, tx_types_list, idx = test
    teal = parse_teal(code.strip())

    bbs = order_basic_blocks(teal.bbs)
    for b, tx_types in zip(bbs, tx_types_list):
        if idx == -1:
            ctx = b.transaction_context
        else:
            ctx = b.transaction_context.gtxn_context(idx)
        assert set(ctx.transaction_types) == set(tx_types)

