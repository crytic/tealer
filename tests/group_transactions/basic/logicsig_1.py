# pylint: disable=undefined-variable
# type: ignore[name-defined]
"""
case 1:
    - Single transaction.
    - app_1 and logicsig_1 is executed
    - logicsig_1 checks the rekeyto field
    - app_1 does not do anything.

Expected:
    - The detector should not report it as vulnerable.
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - AssetCloseTo


case 2:
    - Single transaction.
    - Application and LogicSig does not check the RekeyTo field

Expected:
    - The detector should report it as vulnerable
    Vulnerable - RekeyTo
    Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 3:
    - Single transaction.
    - Only application is called
    - has_logic_sig is set to True but the logic_sig contract is not given.

Expected:
    The detector should report the operation as vulnerable. Even if the detector does not the logic sig being executed, the operation should be considered
    vulnerable because a logic sig will be vulnerable to Rekeying.
    Vulnerable - RekeyTo
    Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 4:
    - Single transaction.
    - Application is called
    - has_logic_sig is set to False.

Expected:
    The detector should report the operation as NOT VULNERABLE. Applications are not vulnerable to rekeying.
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 5:
    - Single transaction
    - Application checks the rekeyto field
    - LogicSig checks that application is called

Expected:
    NOT VULNERABLE - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo



case 6:
    - Single transaction
    - Application access the rekeyto field using `Gtxn[Txn.group_index()].rekey_to()`.
    - LogicSig checks the application is called.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 7:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application checks the rekeyto field of 0th transaction and 1st transaction using absolute indices.
        - LogicSig checks the application id
    - Second transaction (pay)(index: 1):
        - LogicSig does not check anything.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 8:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application checks the rekeyto field of 0th transaction using absolute index.
        - LogicSig checks the application id
    - Second transaction (axfer)(index: 1):
        - LogicSig checks it's rekeyto field.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 9:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application checks the rekeyto field of 1st transaction using absolute index.
        - LogicSig checks the application id
    - Second transaction (pay)(index: 1):
        - LogicSig does not check anything.

Expected:
    Vulnerable. - RekeyTo
    The first transaction is vulnerable. The second transaction should not be reported

    Vulnerable - Fee
    The first transaction is vulnerable. The second transaction should not be reported
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 10:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application does not check anything.
        - LogicSig checks the application id
    - Second transaction (pay)(index: 1):
        - LogicSig checks the fields of both transactions using absolute indices.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 11:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application does not check anything.
        - has_logic_sig is True.
    - Second transaction (pay)(index: 1):
        - LogicSig checks the fields of both transactions using absolute indices

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 12:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application does not check anything.
        - has_logic_sig is True.
    - Second transaction (axfer)(index: 1):
        - LogicSig checks the fields of its own transaction field.

Expected:
    Vulnerable - RekeyTo
    Only the first transaction is reported as vulnerable.

    Vulnerable - Fee
    Only the first transaction is reported as vulnerable.
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 13:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application does not check anything.
    - Second transaction (pay)(index: 1):
        - LogicSig does not check anything.

Expected:
    Vulnerable - RekeyTo
    Second transaction is reported as vulnerable

    Vulnerable - Fee
    Second transaction is reported as vulnerable

    Vulnerable - CloseRemainderTo
    Second transaction is reported as vulnerable

    Not Vulnerable - AssetCloseTo

case 14:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application does not check anything.
        - LogicSig does not check anything.
    - Second transaction (axfer)(index: 1):
        - LogicSig does not check anything.

Expected:
    Vulnerable - RekeyTo
    Both First and Second transactions are reported as vulnerable.

    Vulnerable - Fee
    Both First and Second transactions are reported as vulnerable.

    Not Vulnerable - CloseRemainderTo
    Vulnerable - AssetCloseTo
    Second transaction is reported as vulnerable

case 15:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application does not check anything.
        - LogicSig checks the rekeyto field of 0th transaction and 1st transaction using absolute indices
    - Second transaction (axfer)(index: 1):
        - LogicSig does not check anything.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 16:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application does not check anything.
        - LogicSig checks the rekeyto field of 0th transaction using absolute index.
    - Second transaction (axfer)(index: 1):
        - LogicSig checks it's rekeyto field.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 17:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application does not check anything.
        - LogicSig checks the rekeyto field of 1st transaction using absolute index.
    - Second transaction (pay)(index: 1):
        - LogicSig does not check anything.

Expected:
    Vulnerable - RekeyTo
    The first transaction is vulnerable. The second transaction should not be reported

    Vulnerable - Fee
    The first transaction is vulnerable. The second transaction should not be reported

    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 18:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application checks the rekeyto field of 0th transaction using absolute index and 1st transaction using relative index(+4).
        - LogicSig checks the application id
    - Second transaction (axfer):
        - LogicSig does not check anything.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 19:
    - Two transactions
    - First transaction (appl):
        - Application checks the rekeyto field of 1st transaction using relative index(+4).
        - LogicSig checks the application id
    - Second transaction (pay):
        - LogicSig checks rekey field of the previous transaction using (-4) relative index.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 20:
    - Two transactions
    - First transaction (appl):
        - Application checks the rekeyto field of 1st transaction using absolute index.
        - LogicSig checks the application id
    - Second transaction (pay)(index: 1):
        - LogicSig checks rekey field of the first transaction using (+5) relative index.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 21:
    - Two transactions
    - First transaction (appl):
        - Application checks the rekeyto field of 1st transaction using relative index(+2).
        - LogicSig checks the application id
    - Second transaction (pay):
        - LogicSig does not check anything.

Expected:
    Vulnerable - RekeyTo
    The first transaction is vulnerable. The second transaction should not be reported

    Vulnerable - Fee
    The first transaction is vulnerable. The second transaction should not be reported

    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 22:
    - Two transactions
    - First transaction (appl):
        - Application does not check anything.
        - LogicSig checks the application id
    - Second transaction (axfer):
        - LogicSig checks the field of previous transaction using relative index(-1) and its own field directly.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 23:
    - Two transactions
    - First transaction (appl):
        - Application does not check anything.
        - has_logic_sig is True.
    - Second transaction (pay):
        - LogicSig checks the field of previous transaction using relative index(-1) and its own field directly.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 24:
    - Two transactions
    - First transaction (appl):
        - Application does not check anything.
        - has_logic_sig is True.
    - Second transaction (pay):
        - LogicSig checks the fields of its own transaction field.

Expected:
    Vulnerable - RekeyTo.
    Only the first transaction is reported as vulnerable.

    Vulnerable - Fee.
    Only the first transaction is reported as vulnerable.

    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 25:
    - Two transactions
    - First transaction (appl):
        - Application does not check anything.
    - Second transaction (axfer):
        - LogicSig does not check anything.

Expected:
    Vulnerable - RekeyTo.
    Second transaction is reported as vulnerable

    Vulnerable - Fee.
    Second transaction is reported as vulnerable

    Not Vulnerable - CloseRemainderTo
    Vulnerable - AssetCloseTo
    Second transaction is reported


case 26:
    - Two transactions
    - First transaction (appl):
        - Application does not check anything.
        - LogicSig does not check anything.
    - Second transaction (pay):
        - LogicSig does not check anything.

Expected:
    Vulnerable - RekeyTo.
    Both First and Second transactions are reported as vulnerable.

    Vulnerable - Fee.
    Both First and Second transactions are reported as vulnerable.

    Vulnerable - CloseRemainderTo
    Second transaction is reported as vulnerable

    Not Vulnerable - AssetCloseTo

case 27:
    - Two transactions
    - First transaction (appl):
        - Application does not check anything.
        - LogicSig checks the rekeyto field of its own transaction and 1st transaction using relative index(+1)
    - Second transaction (pay):
        - LogicSig does not check anything.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 28:
    - Two transactions
    - First transaction (appl):
        - Application checks the rekeyto field of 1st transaction using relative index(+5).
        - LogicSig checks the application id
    - Second transaction (axfer):
        - LogicSig checks rekey field of the previous transaction using (-4) relative index.

Expected:
    Vulnerable - RekeyTo.
    Second transaction uses the wrong index. First contract will be vulnerable.

    Vulnerable - Fee
    Second transaction uses the wrong index. First contract will be vulnerable.
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 29:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application does not check anything.
        - LogicSig checks the rekeyto field of 1st transaction using relative index(+3).
    - Second transaction (pay):
        - LogicSig does not check anything.

Expected:
    Vulnerable - RekeyTo.
    The first transaction is vulnerable. The second transaction should not be reported

    Vulnerable - Fee.
    The first transaction is vulnerable. The second transaction should not be reported
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 30:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application checks the rekeyto field of 0th transaction using absolute index
        - LogicSig checks the application id and field of 1st transaction using relative index(+4).
    - Second transaction (pay):
        - LogicSig does not check anything.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 31:
    - Two transactions
    - First transaction (appl):
        - Application does not check anything.
        - LogicSig checks the rekeyto field of 1st transaction using relative index(+4).
    - Second transaction (axfer):
        - LogicSig checks rekey field of the previous transaction using (-4) relative index.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo


case 32:
    - Two transactions
    - First transaction (appl):
        - Application does not check anything.
        - LogicSig checks the rekeyto field of 1st transaction using relative index(+5)
    - Second transaction (axfer):
        - LogicSig checks rekey field of the previous transaction using (-4) relative index.

Expected:
    Vulnerable - RekeyTo.
    Second transaction uses the wrong index. First contract will be vulnerable.

    Vulnerable - Fee.
    Second transaction uses the wrong index. First contract will be vulnerable.
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 33:
    - Two transactions
    - First transaction (appl):
        - Application does not check anything.
        - LogicSig checks the rekeyto field of 1st transaction using absolute index.
    - Second transaction (pay)(index: 1):
        - LogicSig checks rekey field of the 0th transaction using (+5) relative index.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 34:
    - Two transactions
    - First transaction (appl):
        - Application does not check anything
        - LogicSig checks the rekeyto field of 1st transaction using relative index(+2).
    - Second transaction (pay):
        - LogicSig does not check anything.

Expected:
    Vulnerable - RekeyTo.
    The first transaction is vulnerable. The second transaction should not be reported

    Vulnerable - Fee.
    The first transaction is vulnerable. The second transaction should not be reported
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 35:
    - Two transactions
    - First transaction (appl)(index: 0):
        - Application does not check anything.
        - LogicSig checks the rekeyto field of 1st transaction using relative index(+3).
    - Second transaction (axfer):
        - LogicSig does not check anything.

Expected:
    Vulnerable - RekeyTo.
    The first transaction is vulnerable. The second transaction should not be reported

    Vulnerable - Fee
    The first transaction is vulnerable. The second transaction should not be reported
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 36:
    - Single transaction (index: 4).
    - Application checks the field using absolute index.
    - LogicSig checks the application id
    - Absolute index is given in the config

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo

case 37:
    - Single transaction (index: 1)
    - Application does not check anything.
    - Logic checks the field using absolute index.
    - Absolute index is given in the config.

Expected:
    Not Vulnerable - RekeyTo
    Not Vulnerable - Fee
    Not Vulnerable - CloseRemainderTo
    Not Vulnerable - AssetCloseTo
"""
from pathlib import Path
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import


def lsig1_case_1() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Txn.rekey_to() == Global.zero_address(),
                    Txn.fee() < Int(10000),
                    Txn.close_remainder_to() == Global.zero_address(),
                    Txn.asset_close_to() == Global.zero_address(),
                    Txn.on_completion() != OnComplete.UpdateApplication,
                    Txn.on_completion() != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_2() -> Expr:
    return Return(Int(1))


def lsig1_case_5() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Txn.application_id() == Int(1337),
                    # Txn.on_completion() == OnComplete.NoOp,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_6() -> Expr:
    return lsig1_case_5()


def lsig1_case_7() -> Expr:
    return lsig1_case_5()


def lsig1_case_8() -> Expr:
    return lsig1_case_5()


def lsig1_case_9() -> Expr:
    return lsig1_case_5()


def lsig1_case_10() -> Expr:
    return lsig1_case_5()


def lsig1_case_14() -> Expr:
    return Return(Int(1))


def lsig1_case_15() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    # int 0; gtxns RekeyTo
                    Gtxn[Int(0)].rekey_to() == Global.zero_address(),
                    Gtxn[1].rekey_to() == Global.zero_address(),
                    Gtxn[Int(0)].fee() < Int(100000),
                    Gtxn[1].fee() < Int(1000),
                    Gtxn[Int(0)].close_remainder_to() == Global.zero_address(),
                    Gtxn[1].close_remainder_to() == Global.zero_address(),
                    Gtxn[Int(0)].asset_close_to() == Global.zero_address(),
                    Gtxn[1].asset_close_to() == Global.zero_address(),
                    Gtxn[0].on_completion() != OnComplete.UpdateApplication,
                    Gtxn[0].on_completion() != OnComplete.DeleteApplication,
                    Gtxn[Int(1)].on_completion() != OnComplete.UpdateApplication,
                    Gtxn[Int(1)].on_completion() != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_16() -> Expr:
    return Seq(
        [
            Assert(Gtxn[0].rekey_to() == Global.zero_address()),
            Assert(Gtxn[0].fee() < Int(10000)),
            Assert(Gtxn[0].close_remainder_to() == Global.zero_address()),
            Assert(Gtxn[0].asset_close_to() == Global.zero_address()),
            Assert(
                And(
                    Gtxn[0].on_completion() != OnComplete.UpdateApplication,
                    Gtxn[0].on_completion() != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_17() -> Expr:
    return Seq(
        [
            Assert(Gtxn[1].rekey_to() == Global.zero_address()),
            Assert(Gtxn[1].fee() < Int(10000)),
            Assert(Gtxn[1].close_remainder_to() == Global.zero_address()),
            Assert(Gtxn[1].asset_close_to() == Global.zero_address()),
            Assert(
                And(
                    Gtxn[1].on_completion() != OnComplete.UpdateApplication,
                    Gtxn[1].on_completion() != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_18() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Txn.application_id() == Int(1337),
                    # Txn.on_completion() == OnComplete.NoOp,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_19() -> Expr:
    return lsig1_case_18()


def lsig1_case_20() -> Expr:
    return lsig1_case_18()


def lsig1_case_21() -> Expr:
    return lsig1_case_18()


def lsig1_case_22() -> Expr:
    return lsig1_case_18()


def lsig1_case_26() -> Expr:
    return Return(Int(1))


def lsig1_case_27() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Txn.rekey_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(1)].rekey_to() == Global.zero_address(),
                    Txn.fee() < Int(10000),
                    Gtxn[Txn.group_index() + Int(1)].fee() < Int(10000),
                    Txn.close_remainder_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(1)].close_remainder_to() == Global.zero_address(),
                    Txn.asset_close_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(1)].asset_close_to() == Global.zero_address(),
                    Txn.on_completion() != OnComplete.UpdateApplication,
                    Txn.on_completion() != OnComplete.DeleteApplication,
                    Gtxn[Txn.group_index() + Int(1)].on_completion()
                    != OnComplete.UpdateApplication,
                    Gtxn[Txn.group_index() + Int(1)].on_completion()
                    != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_28() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Txn.application_id() == Int(1337),
                    # Txn.on_completion() == OnComplete.NoOp,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_29() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Gtxn[Txn.group_index() + Int(3)].rekey_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(3)].fee() < Int(10000),
                    Gtxn[Txn.group_index() + Int(3)].close_remainder_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(3)].asset_close_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(3)].on_completion()
                    != OnComplete.UpdateApplication,
                    Gtxn[Txn.group_index() + Int(3)].on_completion()
                    != OnComplete.UpdateApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_30() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Txn.application_id() == Int(1337),
                    # Txn.on_completion() == OnComplete.NoOp,
                    Gtxn[Txn.group_index() + Int(4)].rekey_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(4)].fee() < Int(10000),
                    Gtxn[Txn.group_index() + Int(4)].asset_close_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(4)].close_remainder_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(4)].on_completion()
                    != OnComplete.UpdateApplication,
                    Gtxn[Txn.group_index() + Int(4)].on_completion()
                    != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_31() -> Expr:
    return lsig1_case_30()


def lsig1_case_32() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Txn.application_id() == Int(1337),
                    # Txn.on_completion() == OnComplete.NoOp,
                    Gtxn[Txn.group_index() + Int(5)].rekey_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(5)].fee() < Int(10000),
                    Gtxn[Txn.group_index() + Int(5)].close_remainder_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(5)].asset_close_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(5)].on_completion()
                    != OnComplete.UpdateApplication,
                    Gtxn[Txn.group_index() + Int(5)].on_completion()
                    != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_33() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Gtxn[1].rekey_to() == Global.zero_address(),
                    Gtxn[1].fee() < Int(10000),
                    Gtxn[1].close_remainder_to() == Global.zero_address(),
                    Gtxn[1].asset_close_to() == Global.zero_address(),
                    Txn.application_id() == Int(1337),
                    # Txn.on_completion() == OnComplete.NoOp,
                    Gtxn[1].on_completion() != OnComplete.UpdateApplication,
                    Gtxn[1].on_completion() != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_34() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Gtxn[Txn.group_index() + Int(2)].rekey_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(2)].fee() < Int(10000),
                    Gtxn[Txn.group_index() + Int(2)].close_remainder_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(2)].asset_close_to() == Global.zero_address(),
                    Txn.application_id() == Int(1337),
                    # Txn.on_completion() == OnComplete.NoOp,
                    Gtxn[Txn.group_index() + Int(2)].on_completion()
                    != OnComplete.UpdateApplication,
                    Gtxn[Txn.group_index() + Int(2)].on_completion()
                    != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_35() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Gtxn[Txn.group_index() + Int(3)].rekey_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(3)].fee() < Int(10000),
                    Gtxn[Txn.group_index() + Int(3)].close_remainder_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(3)].asset_close_to() == Global.zero_address(),
                    Txn.application_id() == Int(1337),
                    # Txn.on_completion() == OnComplete.NoOp,
                    Gtxn[Txn.group_index() + Int(3)].on_completion()
                    != OnComplete.UpdateApplication,
                    Gtxn[Txn.group_index() + Int(3)].on_completion()
                    != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_36() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Txn.application_id() == Int(1337),
                    # Txn.on_completion() == OnComplete.NoOp,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig1_case_37() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Gtxn[1].fee() < Int(10000),
                    Gtxn[1].rekey_to() == Global.zero_address(),
                    Gtxn[1].close_remainder_to() == Global.zero_address(),
                    Gtxn[1].asset_close_to() == Global.zero_address(),
                    Gtxn[1].on_completion() != OnComplete.UpdateApplication,
                    Gtxn[1].on_completion() != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def logic_sig() -> Expr:
    test_case = Btoi(Arg(0))
    return Seq(
        [
            Cond(
                [test_case == Int(1), lsig1_case_1()],
                [test_case == Int(2), lsig1_case_2()],
                # [test_case == Int(3), lsig1_case_3()],
                # [test_case == Int(4), lsig1_case_4()],
                [test_case == Int(5), lsig1_case_5()],
                [test_case == Int(6), lsig1_case_6()],
                [test_case == Int(7), lsig1_case_7()],
                [test_case == Int(8), lsig1_case_8()],
                [test_case == Int(9), lsig1_case_9()],
                [test_case == Int(10), lsig1_case_10()],
                # [test_case == Int(11), lsig1_case_11()],
                # [test_case == Int(12), lsig1_case_12()],
                # [test_case == Int(13), lsig1_case_13()],
                [test_case == Int(14), lsig1_case_14()],
                [test_case == Int(15), lsig1_case_15()],
                [test_case == Int(16), lsig1_case_16()],
                [test_case == Int(17), lsig1_case_17()],
                [test_case == Int(18), lsig1_case_18()],
                [test_case == Int(19), lsig1_case_19()],
                [test_case == Int(20), lsig1_case_20()],
                [test_case == Int(21), lsig1_case_21()],
                [test_case == Int(22), lsig1_case_22()],
                # [test_case == Int(23), lsig1_case_23()],
                # [test_case == Int(24), lsig1_case_24()],
                # [test_case == Int(25), lsig1_case_25()],
                [test_case == Int(26), lsig1_case_26()],
                [test_case == Int(27), lsig1_case_27()],
                [test_case == Int(28), lsig1_case_28()],
                [test_case == Int(29), lsig1_case_29()],
                [test_case == Int(30), lsig1_case_30()],
                [test_case == Int(31), lsig1_case_31()],
                [test_case == Int(32), lsig1_case_32()],
                [test_case == Int(33), lsig1_case_33()],
                [test_case == Int(34), lsig1_case_34()],
                [test_case == Int(35), lsig1_case_35()],
                [test_case == Int(36), lsig1_case_36()],
                [test_case == Int(37), lsig1_case_37()],
            )
        ]
    )


def compile_program(output_file: Path) -> None:
    teal = compileTeal(logic_sig(), mode=Mode.Signature, version=7)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(teal)


if __name__ == "__main__":
    compile_program(Path("logicsig_1.teal"))
