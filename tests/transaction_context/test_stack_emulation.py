from typing import Tuple, List
import pytest

from tealer.analyses.utils.stack_ast_builder import (
    construct_stack_ast,
    UnknownStackValue,
    KnownStackValue,
    StackValue,
)
from tealer.teal.parse_teal import parse_teal
from tealer.teal.instructions.instructions import (
    Pragma,
    Txn,
    Int,
    Neq,
    Gtxn,
    Addr,
    Eq,
    B,
    Global,
    Label,
    PushInt,
    LessE,
    Mul,
    PushBytes,
    Assert,
    And,
    Or,
    BZ,
    BNZ,
    Return,
)
from tealer.teal.instructions.transaction_field import (
    GroupIndex,
    CloseRemainderTo,
    TypeEnum,
    RekeyTo,
    LastValid,
    Fee,
    Lease,
)
from tealer.teal.global_field import GroupSize, ZeroAddress, MinTxnFee


T1 = """
#pragma version 6
txn GroupIndex
int 0
!=
bnz index_not_0
gtxn 0 CloseRemainderTo  // index must be 0
addr AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEVAL4QAJS7JHB4
==
assert
b process_txn
index_not_0:
global GroupSize    // index is not zero and groupsize is **3**. So, txn index can be 1 or 2
int 3
==
assert
gtxn 1 CloseRemainderTo     // only checks gtxn 1. so, is vulnerable if txn index is 2
global ZeroAddress
==
assert
process_txn:
int 1
return
"""

T1_VALUES = [
    KnownStackValue(ins=Pragma(6), args=[]),
    KnownStackValue(ins=Txn(GroupIndex()), args=[]),
    KnownStackValue(ins=Int(0), args=[]),
    KnownStackValue(
        ins=Neq(),
        args=[
            KnownStackValue(ins=Txn(GroupIndex()), args=[]),
            KnownStackValue(ins=Int(0), args=[]),
        ],
    ),
    KnownStackValue(
        ins=BNZ("index_not_0"),
        args=[
            KnownStackValue(
                ins=Neq(),
                args=[
                    KnownStackValue(ins=Txn(GroupIndex()), args=[]),
                    KnownStackValue(ins=Int(0), args=[]),
                ],
            )
        ],
    ),
    KnownStackValue(ins=Gtxn(0, CloseRemainderTo()), args=[]),
    KnownStackValue(
        ins=Addr("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEVAL4QAJS7JHB4"), args=[]
    ),
    KnownStackValue(
        ins=Eq(),
        args=[
            KnownStackValue(ins=Gtxn(0, CloseRemainderTo()), args=[]),
            KnownStackValue(
                ins=Addr("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEVAL4QAJS7JHB4"), args=[]
            ),
        ],
    ),
    KnownStackValue(
        ins=Assert(),
        args=[
            KnownStackValue(
                ins=Eq(),
                args=[
                    KnownStackValue(ins=Gtxn(0, CloseRemainderTo()), args=[]),
                    KnownStackValue(
                        ins=Addr("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEVAL4QAJS7JHB4"),
                        args=[],
                    ),
                ],
            )
        ],
    ),
    KnownStackValue(ins=B("process_txn"), args=[]),
    KnownStackValue(ins=Label("index_not_0:"), args=[]),
    KnownStackValue(ins=Global(GroupSize()), args=[]),
    KnownStackValue(ins=Int(3), args=[]),
    KnownStackValue(
        ins=Eq(),
        args=[
            KnownStackValue(ins=Global(GroupSize()), args=[]),
            KnownStackValue(ins=Int(3), args=[]),
        ],
    ),
    KnownStackValue(
        ins=Assert(),
        args=[
            KnownStackValue(
                ins=Eq(),
                args=[
                    KnownStackValue(ins=Global(GroupSize()), args=[]),
                    KnownStackValue(ins=Int(3), args=[]),
                ],
            )
        ],
    ),
    KnownStackValue(ins=Gtxn(1, CloseRemainderTo()), args=[]),
    KnownStackValue(ins=Global(ZeroAddress()), args=[]),
    KnownStackValue(
        ins=Eq(),
        args=[
            KnownStackValue(ins=Gtxn(1, CloseRemainderTo()), args=[]),
            KnownStackValue(ins=Global(ZeroAddress()), args=[]),
        ],
    ),
    KnownStackValue(
        ins=Assert(),
        args=[
            KnownStackValue(
                ins=Eq(),
                args=[
                    KnownStackValue(ins=Gtxn(1, CloseRemainderTo()), args=[]),
                    KnownStackValue(ins=Global(ZeroAddress()), args=[]),
                ],
            )
        ],
    ),
    KnownStackValue(ins=Label("process_txn:"), args=[]),
    KnownStackValue(ins=Int(1), args=[]),
    KnownStackValue(ins=Return(), args=[KnownStackValue(ins=Int(1), args=[])]),
]

T2 = """
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
||
txn CloseRemainderTo
global ZeroAddress
==
||
txn Fee
int 2
global MinTxnFee
*
<=
||
assert
int 1
return
"""

T2_VALUES = [
    KnownStackValue(ins=Pragma(4), args=[]),
    KnownStackValue(ins=Txn(TypeEnum()), args=[]),
    KnownStackValue(ins=Int(2), args=[]),
    KnownStackValue(
        ins=Eq(),
        args=[KnownStackValue(ins=Txn(TypeEnum()), args=[]), KnownStackValue(ins=Int(2), args=[])],
    ),
    KnownStackValue(ins=Txn(RekeyTo()), args=[]),
    KnownStackValue(ins=Global(ZeroAddress()), args=[]),
    KnownStackValue(
        ins=Eq(),
        args=[
            KnownStackValue(ins=Txn(RekeyTo()), args=[]),
            KnownStackValue(ins=Global(ZeroAddress()), args=[]),
        ],
    ),
    KnownStackValue(
        ins=And(),
        args=[
            KnownStackValue(
                ins=Eq(),
                args=[
                    KnownStackValue(ins=Txn(TypeEnum()), args=[]),
                    KnownStackValue(ins=Int(2), args=[]),
                ],
            ),
            KnownStackValue(
                ins=Eq(),
                args=[
                    KnownStackValue(ins=Txn(RekeyTo()), args=[]),
                    KnownStackValue(ins=Global(ZeroAddress()), args=[]),
                ],
            ),
        ],
    ),
    KnownStackValue(ins=Txn(LastValid()), args=[]),
    KnownStackValue(ins=PushInt(16600000), args=[]),
    KnownStackValue(
        ins=Eq(),
        args=[
            KnownStackValue(ins=Txn(LastValid()), args=[]),
            KnownStackValue(ins=PushInt(16600000), args=[]),
        ],
    ),
    KnownStackValue(
        ins=And(),
        args=[
            KnownStackValue(
                ins=And(),
                args=[
                    KnownStackValue(
                        ins=Eq(),
                        args=[
                            KnownStackValue(ins=Txn(TypeEnum()), args=[]),
                            KnownStackValue(ins=Int(2), args=[]),
                        ],
                    ),
                    KnownStackValue(
                        ins=Eq(),
                        args=[
                            KnownStackValue(ins=Txn(RekeyTo()), args=[]),
                            KnownStackValue(ins=Global(ZeroAddress()), args=[]),
                        ],
                    ),
                ],
            ),
            KnownStackValue(
                ins=Eq(),
                args=[
                    KnownStackValue(ins=Txn(LastValid()), args=[]),
                    KnownStackValue(ins=PushInt(16600000), args=[]),
                ],
            ),
        ],
    ),
    KnownStackValue(ins=Txn(Fee()), args=[]),
    KnownStackValue(ins=Global(MinTxnFee()), args=[]),
    KnownStackValue(
        ins=LessE(),
        args=[
            KnownStackValue(ins=Txn(Fee()), args=[]),
            KnownStackValue(ins=Global(MinTxnFee()), args=[]),
        ],
    ),
    KnownStackValue(
        ins=And(),
        args=[
            KnownStackValue(
                ins=And(),
                args=[
                    KnownStackValue(
                        ins=And(),
                        args=[
                            KnownStackValue(
                                ins=Eq(),
                                args=[
                                    KnownStackValue(ins=Txn(TypeEnum()), args=[]),
                                    KnownStackValue(ins=Int(2), args=[]),
                                ],
                            ),
                            KnownStackValue(
                                ins=Eq(),
                                args=[
                                    KnownStackValue(ins=Txn(RekeyTo()), args=[]),
                                    KnownStackValue(ins=Global(ZeroAddress()), args=[]),
                                ],
                            ),
                        ],
                    ),
                    KnownStackValue(
                        ins=Eq(),
                        args=[
                            KnownStackValue(ins=Txn(LastValid()), args=[]),
                            KnownStackValue(ins=PushInt(16600000), args=[]),
                        ],
                    ),
                ],
            ),
            KnownStackValue(
                ins=LessE(),
                args=[
                    KnownStackValue(ins=Txn(Fee()), args=[]),
                    KnownStackValue(ins=Global(MinTxnFee()), args=[]),
                ],
            ),
        ],
    ),
    KnownStackValue(ins=Txn(Lease()), args=[]),
    KnownStackValue(
        ins=PushBytes("0x0000000000000000000000000000000000000000000000000000000000000001"), args=[]
    ),
    KnownStackValue(
        ins=Eq(),
        args=[
            KnownStackValue(ins=Txn(Lease()), args=[]),
            KnownStackValue(
                ins=PushBytes("0x0000000000000000000000000000000000000000000000000000000000000001"),
                args=[],
            ),
        ],
    ),
    KnownStackValue(
        ins=And(),
        args=[
            KnownStackValue(
                ins=And(),
                args=[
                    KnownStackValue(
                        ins=And(),
                        args=[
                            KnownStackValue(
                                ins=And(),
                                args=[
                                    KnownStackValue(
                                        ins=Eq(),
                                        args=[
                                            KnownStackValue(ins=Txn(TypeEnum()), args=[]),
                                            KnownStackValue(ins=Int(2), args=[]),
                                        ],
                                    ),
                                    KnownStackValue(
                                        ins=Eq(),
                                        args=[
                                            KnownStackValue(ins=Txn(RekeyTo()), args=[]),
                                            KnownStackValue(ins=Global(ZeroAddress()), args=[]),
                                        ],
                                    ),
                                ],
                            ),
                            KnownStackValue(
                                ins=Eq(),
                                args=[
                                    KnownStackValue(ins=Txn(LastValid()), args=[]),
                                    KnownStackValue(ins=PushInt(16600000), args=[]),
                                ],
                            ),
                        ],
                    ),
                    KnownStackValue(
                        ins=LessE(),
                        args=[
                            KnownStackValue(ins=Txn(Fee()), args=[]),
                            KnownStackValue(ins=Global(MinTxnFee()), args=[]),
                        ],
                    ),
                ],
            ),
            KnownStackValue(
                ins=Eq(),
                args=[
                    KnownStackValue(ins=Txn(Lease()), args=[]),
                    KnownStackValue(
                        ins=PushBytes(
                            "0x0000000000000000000000000000000000000000000000000000000000000001"
                        ),
                        args=[],
                    ),
                ],
            ),
        ],
    ),
    KnownStackValue(
        ins=BZ("main_l2"),
        args=[
            KnownStackValue(
                ins=And(),
                args=[
                    KnownStackValue(
                        ins=And(),
                        args=[
                            KnownStackValue(
                                ins=And(),
                                args=[
                                    KnownStackValue(
                                        ins=And(),
                                        args=[
                                            KnownStackValue(
                                                ins=Eq(),
                                                args=[
                                                    KnownStackValue(ins=Txn(TypeEnum()), args=[]),
                                                    KnownStackValue(ins=Int(2), args=[]),
                                                ],
                                            ),
                                            KnownStackValue(
                                                ins=Eq(),
                                                args=[
                                                    KnownStackValue(ins=Txn(RekeyTo()), args=[]),
                                                    KnownStackValue(
                                                        ins=Global(ZeroAddress()), args=[]
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    KnownStackValue(
                                        ins=Eq(),
                                        args=[
                                            KnownStackValue(ins=Txn(LastValid()), args=[]),
                                            KnownStackValue(ins=PushInt(16600000), args=[]),
                                        ],
                                    ),
                                ],
                            ),
                            KnownStackValue(
                                ins=LessE(),
                                args=[
                                    KnownStackValue(ins=Txn(Fee()), args=[]),
                                    KnownStackValue(ins=Global(MinTxnFee()), args=[]),
                                ],
                            ),
                        ],
                    ),
                    KnownStackValue(
                        ins=Eq(),
                        args=[
                            KnownStackValue(ins=Txn(Lease()), args=[]),
                            KnownStackValue(
                                ins=PushBytes(
                                    "0x0000000000000000000000000000000000000000000000000000000000000001"
                                ),
                                args=[],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
    KnownStackValue(ins=Int(1), args=[]),
    KnownStackValue(ins=Return(), args=[KnownStackValue(ins=Int(1), args=[])]),
    KnownStackValue(ins=Label("main_l2:"), args=[]),
    KnownStackValue(ins=Txn(RekeyTo()), args=[]),
    KnownStackValue(ins=Global(ZeroAddress()), args=[]),
    KnownStackValue(
        ins=Eq(),
        args=[
            KnownStackValue(ins=Txn(RekeyTo()), args=[]),
            KnownStackValue(ins=Global(ZeroAddress()), args=[]),
        ],
    ),
    KnownStackValue(
        ins=Or(),
        args=[
            UnknownStackValue(),
            KnownStackValue(
                ins=Eq(),
                args=[
                    KnownStackValue(ins=Txn(RekeyTo()), args=[]),
                    KnownStackValue(ins=Global(ZeroAddress()), args=[]),
                ],
            ),
        ],
    ),
    KnownStackValue(ins=Txn(CloseRemainderTo()), args=[]),
    KnownStackValue(ins=Global(ZeroAddress()), args=[]),
    KnownStackValue(
        ins=Eq(),
        args=[
            KnownStackValue(ins=Txn(CloseRemainderTo()), args=[]),
            KnownStackValue(ins=Global(ZeroAddress()), args=[]),
        ],
    ),
    KnownStackValue(
        ins=Or(),
        args=[
            KnownStackValue(
                ins=Or(),
                args=[
                    UnknownStackValue(),
                    KnownStackValue(
                        ins=Eq(),
                        args=[
                            KnownStackValue(ins=Txn(RekeyTo()), args=[]),
                            KnownStackValue(ins=Global(ZeroAddress()), args=[]),
                        ],
                    ),
                ],
            ),
            KnownStackValue(
                ins=Eq(),
                args=[
                    KnownStackValue(ins=Txn(CloseRemainderTo()), args=[]),
                    KnownStackValue(ins=Global(ZeroAddress()), args=[]),
                ],
            ),
        ],
    ),
    KnownStackValue(ins=Txn(Fee()), args=[]),
    KnownStackValue(ins=Int(2), args=[]),
    KnownStackValue(ins=Global(MinTxnFee()), args=[]),
    KnownStackValue(
        ins=Mul(),
        args=[
            KnownStackValue(ins=Int(2), args=[]),
            KnownStackValue(ins=Global(MinTxnFee()), args=[]),
        ],
    ),
    KnownStackValue(
        ins=LessE(),
        args=[
            KnownStackValue(ins=Txn(Fee()), args=[]),
            KnownStackValue(
                ins=Mul(),
                args=[
                    KnownStackValue(ins=Int(2), args=[]),
                    KnownStackValue(ins=Global(MinTxnFee()), args=[]),
                ],
            ),
        ],
    ),
    KnownStackValue(
        ins=Or(),
        args=[
            KnownStackValue(
                ins=Or(),
                args=[
                    KnownStackValue(
                        ins=Or(),
                        args=[
                            UnknownStackValue(),
                            KnownStackValue(
                                ins=Eq(),
                                args=[
                                    KnownStackValue(ins=Txn(RekeyTo()), args=[]),
                                    KnownStackValue(ins=Global(ZeroAddress()), args=[]),
                                ],
                            ),
                        ],
                    ),
                    KnownStackValue(
                        ins=Eq(),
                        args=[
                            KnownStackValue(ins=Txn(CloseRemainderTo()), args=[]),
                            KnownStackValue(ins=Global(ZeroAddress()), args=[]),
                        ],
                    ),
                ],
            ),
            KnownStackValue(
                ins=LessE(),
                args=[
                    KnownStackValue(ins=Txn(Fee()), args=[]),
                    KnownStackValue(
                        ins=Mul(),
                        args=[
                            KnownStackValue(ins=Int(2), args=[]),
                            KnownStackValue(ins=Global(MinTxnFee()), args=[]),
                        ],
                    ),
                ],
            ),
        ],
    ),
    KnownStackValue(
        ins=Assert(),
        args=[
            KnownStackValue(
                ins=Or(),
                args=[
                    KnownStackValue(
                        ins=Or(),
                        args=[
                            KnownStackValue(
                                ins=Or(),
                                args=[
                                    UnknownStackValue(),
                                    KnownStackValue(
                                        ins=Eq(),
                                        args=[
                                            KnownStackValue(ins=Txn(RekeyTo()), args=[]),
                                            KnownStackValue(ins=Global(ZeroAddress()), args=[]),
                                        ],
                                    ),
                                ],
                            ),
                            KnownStackValue(
                                ins=Eq(),
                                args=[
                                    KnownStackValue(ins=Txn(CloseRemainderTo()), args=[]),
                                    KnownStackValue(ins=Global(ZeroAddress()), args=[]),
                                ],
                            ),
                        ],
                    ),
                    KnownStackValue(
                        ins=LessE(),
                        args=[
                            KnownStackValue(ins=Txn(Fee()), args=[]),
                            KnownStackValue(
                                ins=Mul(),
                                args=[
                                    KnownStackValue(ins=Int(2), args=[]),
                                    KnownStackValue(ins=Global(MinTxnFee()), args=[]),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
    KnownStackValue(ins=Int(1), args=[]),
    KnownStackValue(
        ins=Return(),
        args=[
            KnownStackValue(ins=Int(1), args=[]),
        ],
    ),
]


ALL_NEW_TESTS = [
    (T1, T1_VALUES),
    (T2, T2_VALUES),
]


def cmp_stack_values(ex_v: StackValue, t_v: StackValue) -> bool:
    if isinstance(ex_v, UnknownStackValue):
        print("t_v", t_v)
        return isinstance(t_v, UnknownStackValue)
    if isinstance(t_v, UnknownStackValue):
        print("t_v", t_v)
        return isinstance(ex_v, UnknownStackValue)
    if ex_v.instruction.__class__ != t_v.instruction.__class__:
        return False
    if len(ex_v.args) != len(t_v.args):
        return False
    for ex_arg, t_arg in zip(ex_v.args, t_v.args):
        if not cmp_stack_values(ex_arg, t_arg):
            return False
    return True


@pytest.mark.parametrize("test", ALL_NEW_TESTS)  # type: ignore
def test_just_detectors(test: Tuple[str, List[KnownStackValue]]) -> None:
    code, expected_stack_values = test
    teal = parse_teal(code.strip())
    test_values: List[KnownStackValue] = []
    for bi in teal.bbs:
        values = construct_stack_ast(bi)
        for ins in bi.instructions:
            test_values.append(values[ins])
    assert len(expected_stack_values) == len(test_values)
    for ex_v, t_v in zip(expected_stack_values, test_values):
        print(str(t_v.instruction), t_v.instruction.line)
        assert cmp_stack_values(ex_v, t_v)


if __name__ == "__main__":
    teal_obj = parse_teal(T2)
    for bb in teal_obj.bbs:
        print(bb)
        result = construct_stack_ast(bb)
        for i in bb.instructions:
            print(i, result[i])
        print("----------" * 10)
