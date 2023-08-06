from typing import List, Tuple
import pytest

from tealer.utils.teal_enums import TealerTransactionType
from tealer.utils.algorand_constants import MAX_GROUP_SIZE
from tealer.utils.command_line.common import init_tealer_from_single_contract

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
    [
        TealerTransactionType.ApplNoOp,
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
        TealerTransactionType.ApplCreation,
    ],
    [TealerTransactionType.ApplCreation],
    [
        TealerTransactionType.ApplNoOp,
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
    ],
    [
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
    ],
    [
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
    ],
    [TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplNoOp],
    [TealerTransactionType.ApplNoOp, TealerTransactionType.ApplOptIn],
    [
        TealerTransactionType.ApplNoOp,
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
    ],
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
    [
        TealerTransactionType.ApplNoOp,
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
        TealerTransactionType.ApplCreation,
    ],
    [TealerTransactionType.ApplCreation],
    [
        TealerTransactionType.ApplNoOp,
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
    ],
    [
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
    ],
    [
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
    ],
    [TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
    [TealerTransactionType.ApplNoOp],
    [TealerTransactionType.ApplNoOp, TealerTransactionType.ApplOptIn],
    [
        TealerTransactionType.ApplNoOp,
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
    ],
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
def test_tx_types(test: Tuple[str, List[List[int]], int]) -> None:
    code, tx_types_list, idx = test

    tealer = init_tealer_from_single_contract(code.strip(), "test")
    function = tealer.contracts["test"].functions["test"]

    bbs = order_basic_blocks(function.blocks)
    for b, tx_types in zip(bbs, tx_types_list):
        if idx == -1:
            ctx = function.transaction_context(b)
        else:
            ctx = function.transaction_context(b).gtxn_context(idx)
        assert set(ctx.transaction_types) == set(tx_types)


TEST_GROUP_INDICES = """
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

txn_types_list = [
    [
        TealerTransactionType.ApplNoOp,
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
        TealerTransactionType.ApplDeleteApplication,
        TealerTransactionType.ApplCreation,
    ],
    [TealerTransactionType.ApplCreation],
    [
        TealerTransactionType.ApplNoOp,
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
        TealerTransactionType.ApplDeleteApplication,
    ],
    [
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
        TealerTransactionType.ApplDeleteApplication,
    ],
    [
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
        TealerTransactionType.ApplDeleteApplication,
    ],
    [
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
        TealerTransactionType.ApplDeleteApplication,
    ],
    [
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
        TealerTransactionType.ApplDeleteApplication,
    ],
    [TealerTransactionType.ApplNoOp],
    [
        TealerTransactionType.ApplNoOp,
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
        TealerTransactionType.ApplDeleteApplication,
    ],
    [
        TealerTransactionType.ApplNoOp,
        TealerTransactionType.ApplOptIn,
        TealerTransactionType.ApplCloseOut,
        TealerTransactionType.ApplClearState,
        TealerTransactionType.ApplUpdateApplication,
        TealerTransactionType.ApplDeleteApplication,
    ],
    [],
]

# { for each index: {
#           for each block: {
#               possible transaction types
#       }
# }
gtxn_types_list: List[List[List[TealerTransactionType]]] = [
    [
        [
            TealerTransactionType.ApplNoOp,
            TealerTransactionType.ApplOptIn,
            TealerTransactionType.ApplCloseOut,
            TealerTransactionType.ApplClearState,
            TealerTransactionType.ApplUpdateApplication,
            TealerTransactionType.ApplCreation,
        ],
        [TealerTransactionType.ApplCreation],
        [
            TealerTransactionType.ApplNoOp,
            TealerTransactionType.ApplOptIn,
            TealerTransactionType.ApplCloseOut,
            TealerTransactionType.ApplClearState,
            TealerTransactionType.ApplUpdateApplication,
        ],
        [
            TealerTransactionType.ApplOptIn,
            TealerTransactionType.ApplCloseOut,
            TealerTransactionType.ApplClearState,
            TealerTransactionType.ApplUpdateApplication,
        ],
        [
            TealerTransactionType.ApplCloseOut,
            TealerTransactionType.ApplClearState,
            TealerTransactionType.ApplUpdateApplication,
        ],
        [TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
        [TealerTransactionType.ApplClearState, TealerTransactionType.ApplUpdateApplication],
        [TealerTransactionType.ApplNoOp],
        [TealerTransactionType.ApplNoOp, TealerTransactionType.ApplOptIn],
        [
            TealerTransactionType.ApplNoOp,
            TealerTransactionType.ApplOptIn,
            TealerTransactionType.ApplCloseOut,
        ],
        [],
    ],
]

gtxn_types_list += [[[]] * 11 for _ in range(MAX_GROUP_SIZE - 1)]


ALL_TESTS_GTXN = [
    (TEST_GROUP_INDICES, txn_types_list, gtxn_types_list),
]


@pytest.mark.parametrize("test", ALL_TESTS_GTXN)  # type: ignore
def test_tx_types_gtxn(
    test: Tuple[
        str,
        List[List[TealerTransactionType]],
        List[List[List[TealerTransactionType]]],
    ],
) -> None:
    code, ex_txn_types_list, ex_gtxn_types_list = test

    tealer = init_tealer_from_single_contract(code.strip(), "test")
    function = tealer.contracts["test"].functions["test"]

    bbs = order_basic_blocks(function.blocks)
    print("number of blocks:", len(bbs))
    for block_num, b in enumerate(bbs):
        print(block_num, b)
        assert set(function.transaction_context(b).transaction_types) == set(
            ex_txn_types_list[block_num]
        )
        print(block_num, b)
        for txn_ind in range(MAX_GROUP_SIZE):
            ctx = function.transaction_context(b).gtxn_context(txn_ind)
            print("txn_ind =", txn_ind)
            assert set(ctx.transaction_types) == set(ex_gtxn_types_list[txn_ind][block_num])
