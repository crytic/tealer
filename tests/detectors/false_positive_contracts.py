from typing import List, Tuple, Type

from tealer.detectors.abstract_detector import AbstractDetector
from tealer.detectors.all_detectors import (
    CanCloseAccount,
    MissingRekeyTo,
    CanCloseAsset,
    CanUpdate,
    CanDelete,
    MissingFeeCheck,
)


# fp for RekeyTo, AssetCloseTo, CloseRemainderTo
# reason: 1. && connected 2. index is checked and then fields of txn at that index
# reason 2 is solved
fp1_index_gtxn = """
txn GroupIndex
int 1
==
gtxn 1 AssetCloseTo
global ZeroAddress
==
&&
gtxn 1 CloseRemainderTo
global ZeroAddress
==
&&
gtxn 1 RekeyTo
global ZeroAddress
==
&&
assert
int 1
return
"""

FP1_TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    (fp1_index_gtxn, MissingRekeyTo, []),
    (fp1_index_gtxn, CanCloseAccount, []),
    (fp1_index_gtxn, CanCloseAsset, []),
]


# fp for UpdateApplication, DeleteApplication
# reason: 1. && connected, 2. intcblock
fp2_and_connected = """
#pragma version 4
intcblock 0
txn OnCompletion
intc_0
==
txna ApplicationArgs 0
pushbytes 0x5698b72d
==
&&
bnz main_l5
err

main_l5:
int 1
return
"""

FP2_TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    (fp2_and_connected, CanUpdate, []),
    (fp2_and_connected, CanDelete, []),
]


# fp for UpdateApplication, DeleteApplication
# reason: || (or) connected
fp3_or_connected = """
#pragma version 4
txn OnCompletion
int UpdateApplication
==
txn OnCompletion
int DeleteApplication
==
||
txn OnCompletion
int CloseOut
==
||
bnz fail

success:
int 1
return

fail:
err
"""

FP3_TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    (fp3_or_connected, CanUpdate, []),
    (fp3_or_connected, CanDelete, []),
]


# fp for DeleteApplication
# reason: `int 0` and `return` instructions are not sequential.
fp4_separate_return = """
#pragma version 6
txn OnCompletion
int DeleteApplication
==
bnz fail
int 1
return
fail:
int 0
b return_ins
return_ins:
return
"""

FP4_TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    (fp4_separate_return, CanDelete, [])
]


# fp for RekeyTo, Fee
# reason: && connected.
fp5_and_connected_with_branch = """
#pragma version 4
txn TypeEnum
int 2
==
txn RekeyTo
global ZeroAddress
==
&&
txn LastValid
pushint 16600000
==
&&
txn Fee
global MinTxnFee
<=
&&
txn Lease
pushbytes 0x0000000000000000000000000000000000000000000000000000000000000001
==
&&
bz main_l2
int 1
return
main_l2:
txn RekeyTo
global ZeroAddress
==
txn CloseRemainderTo
global ZeroAddress
==
&&
txn Fee
int 2
global MinTxnFee
*
<=
&&
assert
int 1
return
"""

FP5_TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    (fp5_and_connected_with_branch, MissingRekeyTo, []),
    (fp5_and_connected_with_branch, MissingFeeCheck, []),
]


# fp for Fee, CloseRemainderTo, AssetCloseTo detectors
# Reason: 1. && connected. 2. AssetCloseTo is only checked for axfer type transactions, 3. CloseRemainderTo is only checked for pay type transactions
fp6_multiple_group_sizes = """
#pragma version 5
global GroupSize
int 2
==
bnz groupsize_2
global GroupSize
int 3
==
bnz groupsize_3
global GroupSize
int 4
==
gtxn 0 Fee
global MinTxnFee
==
&&
gtxn 1 Fee
global MinTxnFee
==
&&
gtxn 2 Fee
load 7
==
&&
gtxn 3 Fee
int 0
==
&&
gtxn 0 Sender
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 1 Sender
txn Sender
==
&&
gtxn 2 Sender
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 3 Sender
txn Sender
==
&&
gtxn 0 Amount
int 250000
==
&&
gtxn 1 AssetAmount
int 0
==
&&
gtxn 2 AssetAmount
int 1
>=
&&
gtxn 3 Amount
int 0
==
&&
gtxn 0 CloseRemainderTo
global ZeroAddress
==
&&
gtxn 1 AssetCloseTo
global ZeroAddress
==
&&
gtxn 2 AssetCloseTo
global ZeroAddress
==
&&
gtxn 3 CloseRemainderTo
global ZeroAddress
==
&&
gtxn 0 Receiver
txn Sender
==
&&
gtxn 1 AssetReceiver
txn Sender
==
&&
gtxn 2 AssetReceiver
txn Sender
==
&&
gtxn 3 Receiver
addr GDN6PPITDEXNCQ2BS2DUKVDPJZM7K6LKO6QBWP2US555NUE4Q5TY7HAVSQ
==
&&
gtxn 0 TypeEnum
int pay
==
&&
gtxn 1 TypeEnum
int axfer
==
&&
gtxn 2 TypeEnum
int axfer
==
&&
gtxn 3 TypeEnum
int pay
==
&&
gtxn 1 XferAsset
int 1337
==
&&
gtxn 2 XferAsset
int 1337
==
&&
assert
int 1
return
groupsize_3:
global GroupSize
int 3
==
gtxn 0 Fee
global MinTxnFee
==
&&
gtxn 1 Fee
global MinTxnFee
==
&&
gtxn 2 Fee
global MinTxnFee
==
&&
gtxn 0 Sender
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 1 Sender
txn Sender
==
&&
gtxn 2 Sender
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 0 Amount
int 250000
==
&&
gtxn 1 AssetAmount
int 0
==
&&
gtxn 2 AssetAmount
int 1
>=
&&
gtxn 0 CloseRemainderTo
global ZeroAddress
==
&&
gtxn 1 AssetCloseTo
global ZeroAddress
==
&&
gtxn 2 AssetCloseTo
global ZeroAddress
==
&&
gtxn 0 Receiver
txn Sender
==
&&
gtxn 1 AssetReceiver
txn Sender
==
&&
gtxn 2 AssetReceiver
txn Sender
==
&&
gtxn 0 TypeEnum
int pay
==
&&
gtxn 1 TypeEnum
int axfer
==
&&
gtxn 2 TypeEnum
int axfer
==
&&
gtxn 1 XferAsset
int 1337
==
&&
gtxn 2 XferAsset
int 1337
==
&&
bz groupsize_3_2
int 1
return
groupsize_3_2:
global GroupSize
int 3
==
gtxn 0 Fee
global MinTxnFee
==
&&
gtxn 1 Fee
global MinTxnFee
==
&&
gtxn 2 Fee
global MinTxnFee
==
&&
gtxn 0 Sender
txn Sender
==
&&
gtxn 1 Sender
txn Sender
==
&&
gtxn 2 Sender
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 0 AssetAmount
int 0
==
&&
gtxn 1 Amount
int 0
==
&&
gtxn 2 Amount
int 0
==
&&
gtxn 0 AssetCloseTo
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 1 CloseRemainderTo
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 2 CloseRemainderTo
global ZeroAddress
==
&&
gtxn 0 AssetReceiver
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 1 Receiver
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 2 Receiver
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 0 TypeEnum
int axfer
==
&&
gtxn 1 TypeEnum
int pay
==
&&
gtxn 2 TypeEnum
int pay
==
&&
gtxn 0 XferAsset
int 1337
==
&&
assert
int 1
return
groupsize_2:
global GroupSize
int 2
==
txn Fee
global MinTxnFee
==
&&
gtxn 0 Sender
txn Sender
==
&&
gtxn 1 Sender
txn Sender
==
&&
gtxn 0 AssetAmount
int 0
==
&&
gtxn 1 Amount
int 50000
==
&&
gtxn 0 AssetCloseTo
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 1 CloseRemainderTo
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 0 AssetReceiver
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 1 Receiver
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
&&
gtxn 0 TypeEnum
int axfer
==
&&
gtxn 1 TypeEnum
int pay
==
&&
gtxn 0 XferAsset
int 1337
==
&&
bz fail
int 1
return
fail:
int 0
return
"""

FP6_TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    (fp6_multiple_group_sizes, CanCloseAccount, []),
    (fp6_multiple_group_sizes, CanCloseAsset, []),
    (fp6_multiple_group_sizes, MissingFeeCheck, []),
]


# fp for AssetCloseTo
# reason: Only axfer type txns can have assetcloseto
fp7_txn_type_1 = """
#pragma version 7
txn TypeEnum
int pay
==
assert
int 1
return
"""

FP7_TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    (fp7_txn_type_1, CanCloseAsset, []),
]

# fp for CloseRemainderTo
# reason: Only pay type txns can have CloseRemainderTo
fp8_txn_type_2 = """
#pragma version 7
txn TypeEnum
int axfer
==
assert
int 1
return
"""

FP8_TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    (fp8_txn_type_2, CanCloseAccount, []),
]


# fp for RekeyTo, CloseRemainderTo, AssetCloseTo, Fee
# reason: Applications are not vulnerable to RekeyTo, CloseRemainderTo, AssetCloseTo
fp9_txn_type_3 = """
#pragma version 7
txn OnCompletion
int OptIn
==
assert
int 1
return
"""

FP9_TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    (fp9_txn_type_3, MissingRekeyTo, []),
    (fp9_txn_type_3, CanCloseAccount, []),
    (fp9_txn_type_3, CanCloseAsset, []),
    (fp9_txn_type_3, MissingFeeCheck, []),
]


FP_TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = (
    FP1_TESTS
    + FP2_TESTS
    + FP3_TESTS
    + FP4_TESTS
    + FP5_TESTS
    + FP6_TESTS
    + FP7_TESTS
    + FP8_TESTS
    + FP9_TESTS
)
