# pylint: disable=undefined-variable
# type: ignore[name-defined]
from pathlib import Path
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import


def lsig2_case_7() -> Expr:
    return Return(Int(1))


def lsig2_case_8() -> Expr:
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


def lsig2_case_9() -> Expr:
    return Return(Int(1))


def lsig2_case_10() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Gtxn[0].rekey_to() == Global.zero_address(),
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


def lsig2_case_11() -> Expr:
    return lsig2_case_10()


def lsig2_case_12() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Gtxn[1].rekey_to() == Global.zero_address(),
                    Gtxn[1].fee() < Int(10000),
                    Gtxn[1].close_remainder_to() == Global.zero_address(),
                    Gtxn[1].asset_close_to() == Global.zero_address(),
                )
            ),
            Assert(
                And(
                    Gtxn[1].on_completion() != OnComplete.UpdateApplication,
                    Gtxn[1].on_completion() != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig2_case_13() -> Expr:
    return Return(Int(1))


def lsig2_case_14() -> Expr:
    return Return(Int(1))


def lsig2_case_15() -> Expr:
    return Return(Int(1))


def lsig2_case_16() -> Expr:
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


def lsig2_case_17() -> Expr:
    return Return(Int(1))


def lsig2_case_18() -> Expr:
    return Return(Int(1))


def lsig2_case_19() -> Expr:
    return Seq(
        [
            Assert(Gtxn[Txn.group_index() - Int(4)].rekey_to() == Global.zero_address()),
            Assert(Gtxn[Txn.group_index() - Int(4)].fee() < Int(10000)),
            Assert(Gtxn[Txn.group_index() - Int(4)].close_remainder_to() == Global.zero_address()),
            Assert(Gtxn[Txn.group_index() - Int(4)].asset_close_to() == Global.zero_address()),
            Assert(
                And(
                    Gtxn[Txn.group_index() - Int(4)].on_completion()
                    != OnComplete.UpdateApplication,
                    Gtxn[Txn.group_index() - Int(4)].on_completion()
                    != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig2_case_20() -> Expr:
    return Seq(
        [
            Assert(Gtxn[Txn.group_index() + Int(5)].rekey_to() == Global.zero_address()),
            Assert(Gtxn[Txn.group_index() + Int(5)].fee() < Int(10000)),
            Assert(Gtxn[Txn.group_index() + Int(5)].close_remainder_to() == Global.zero_address()),
            Assert(Gtxn[Txn.group_index() + Int(5)].asset_close_to() == Global.zero_address()),
            Assert(
                And(
                    Gtxn[Txn.group_index() + Int(5)].on_completion()
                    != OnComplete.UpdateApplication,
                    Gtxn[Txn.group_index() + Int(5)].on_completion()
                    != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig2_case_21() -> Expr:
    return Return(Int(1))


def lsig2_case_22() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Gtxn[Txn.group_index() - Int(1)].rekey_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() - Int(1)].fee() < Int(10000),
                    Gtxn[Txn.group_index() - Int(1)].close_remainder_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() - Int(1)].asset_close_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() - Int(1)].on_completion()
                    != OnComplete.UpdateApplication,
                    Gtxn[Txn.group_index() - Int(1)].on_completion()
                    != OnComplete.DeleteApplication,
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


def lsig2_case_23() -> Expr:
    return lsig2_case_22()


def lsig2_case_24() -> Expr:
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


def lsig2_case_25() -> Expr:
    return Return(Int(1))


def lsig2_case_26() -> Expr:
    return Return(Int(1))


def lsig2_case_27() -> Expr:
    return Return(Int(1))


def lsig2_case_28() -> Expr:
    return Seq(
        [
            Assert(Gtxn[Txn.group_index() - Int(4)].rekey_to() == Global.zero_address()),
            Assert(Gtxn[Txn.group_index() - Int(4)].fee() < Int(10000)),
            Assert(Gtxn[Txn.group_index() - Int(4)].close_remainder_to() == Global.zero_address()),
            Assert(Gtxn[Txn.group_index() - Int(4)].asset_close_to() == Global.zero_address()),
            Assert(
                And(
                    Gtxn[Txn.group_index() - Int(4)].on_completion()
                    != OnComplete.UpdateApplication,
                    Gtxn[Txn.group_index() - Int(4)].on_completion()
                    != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig2_case_29() -> Expr:
    return Return(Int(1))


def lsig2_case_30() -> Expr:
    return Return(Int(1))


def lsig2_case_31() -> Expr:
    return Seq(
        [
            Assert(Gtxn[Txn.group_index() - Int(4)].rekey_to() == Global.zero_address()),
            Assert(Gtxn[Txn.group_index() - Int(4)].fee() < Int(10000)),
            Assert(Gtxn[Txn.group_index() - Int(4)].close_remainder_to() == Global.zero_address()),
            Assert(Gtxn[Txn.group_index() - Int(4)].asset_close_to() == Global.zero_address()),
            Assert(
                And(
                    Gtxn[Txn.group_index() - Int(4)].on_completion()
                    != OnComplete.UpdateApplication,
                    Gtxn[Txn.group_index() - Int(4)].on_completion()
                    != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig2_case_32() -> Expr:
    return Seq(
        [
            Assert(Gtxn[Txn.group_index() - Int(4)].rekey_to() == Global.zero_address()),
            Assert(Gtxn[Txn.group_index() - Int(4)].fee() < Int(10000)),
            Assert(Gtxn[Txn.group_index() - Int(4)].close_remainder_to() == Global.zero_address()),
            Assert(Gtxn[Txn.group_index() - Int(4)].asset_close_to() == Global.zero_address()),
            Assert(
                And(
                    Gtxn[Txn.group_index() - Int(4)].on_completion()
                    != OnComplete.UpdateApplication,
                    Gtxn[Txn.group_index() - Int(4)].on_completion()
                    != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig2_case_33() -> Expr:
    return Seq(
        [
            Assert(Gtxn[Txn.group_index() + Int(5)].rekey_to() == Global.zero_address()),
            Assert(Gtxn[Txn.group_index() + Int(5)].fee() < Int(10000)),
            Assert(Gtxn[Txn.group_index() + Int(5)].close_remainder_to() == Global.zero_address()),
            Assert(Gtxn[Txn.group_index() + Int(5)].asset_close_to() == Global.zero_address()),
            Assert(
                And(
                    Gtxn[Txn.group_index() + Int(5)].on_completion()
                    != OnComplete.UpdateApplication,
                    Gtxn[Txn.group_index() + Int(5)].on_completion()
                    != OnComplete.DeleteApplication,
                )
            ),
            Return(Int(1)),
        ]
    )


def lsig2_case_34() -> Expr:
    return Return(Int(1))


def lsig2_case_35() -> Expr:
    return Return(Int(1))


def logic_sig() -> Expr:
    test_case = Btoi(Arg(0))
    return Seq(
        [
            Cond(
                # [test_case == Int(1), lsig2_case_1()],
                # [test_case == Int(2), lsig2_case_2()],
                # [test_case == Int(3), lsig2_case_3()],
                # [test_case == Int(4), lsig2_case_4()],
                # [test_case == Int(5), lsig2_case_5()],
                # [test_case == Int(6), lsig2_case_6()],
                [test_case == Int(7), lsig2_case_7()],
                [test_case == Int(8), lsig2_case_8()],
                [test_case == Int(9), lsig2_case_9()],
                [test_case == Int(10), lsig2_case_10()],
                [test_case == Int(11), lsig2_case_11()],
                [test_case == Int(12), lsig2_case_12()],
                [test_case == Int(13), lsig2_case_13()],
                [test_case == Int(14), lsig2_case_14()],
                [test_case == Int(15), lsig2_case_15()],
                [test_case == Int(16), lsig2_case_16()],
                [test_case == Int(17), lsig2_case_17()],
                [test_case == Int(18), lsig2_case_18()],
                [test_case == Int(19), lsig2_case_19()],
                [test_case == Int(20), lsig2_case_20()],
                [test_case == Int(21), lsig2_case_21()],
                [test_case == Int(22), lsig2_case_22()],
                [test_case == Int(23), lsig2_case_23()],
                [test_case == Int(24), lsig2_case_24()],
                [test_case == Int(25), lsig2_case_25()],
                [test_case == Int(26), lsig2_case_26()],
                [test_case == Int(27), lsig2_case_27()],
                [test_case == Int(28), lsig2_case_28()],
                [test_case == Int(29), lsig2_case_29()],
                [test_case == Int(30), lsig2_case_30()],
                [test_case == Int(31), lsig2_case_31()],
                [test_case == Int(32), lsig2_case_32()],
                [test_case == Int(33), lsig2_case_33()],
                [test_case == Int(34), lsig2_case_34()],
                [test_case == Int(35), lsig2_case_35()],
            )
        ]
    )


def compile_program(output_file: Path) -> None:
    teal = compileTeal(logic_sig(), mode=Mode.Signature, version=7)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(teal)


if __name__ == "__main__":
    compile_program(Path("logicsig_2.teal"))
