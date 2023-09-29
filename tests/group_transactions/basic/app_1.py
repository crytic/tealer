# pylint: disable=undefined-variable
# type: ignore[name-defined]
from pathlib import Path
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import


def app1_case_1() -> Expr:
    return Return(Int(1))


def app1_case_2() -> Expr:
    return Return(Int(1))


def app1_case_3() -> Expr:
    return Return(Int(1))


def app1_case_4() -> Expr:
    return Return(Int(1))


def app1_case_5() -> Expr:
    return Seq([Assert(Txn.rekey_to() == Global.zero_address()), Return(Int(1))])


def app1_case_6() -> Expr:
    return Seq(
        [Assert(Gtxn[Txn.group_index()].rekey_to() == Global.zero_address()), Return(Int(1))]
    )


def app1_case_7() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Gtxn[0].rekey_to() == Global.zero_address(),
                    Gtxn[1].rekey_to() == Global.zero_address(),
                )
            ),
            Return(Int(1)),
        ]
    )


def app1_case_8() -> Expr:
    return Seq([Assert(Gtxn[0].rekey_to() == Global.zero_address()), Return(Int(1))])


def app1_case_9() -> Expr:
    return Seq([Assert(Gtxn[1].rekey_to() == Global.zero_address()), Return(Int(1))])


def app1_case_10() -> Expr:
    return Return(Int(1))


def app1_case_11() -> Expr:
    return Return(Int(1))


def app1_case_12() -> Expr:
    return Return(Int(1))


def app1_case_13() -> Expr:
    return Return(Int(1))


def app1_case_14() -> Expr:
    return Return(Int(1))


def app1_case_15() -> Expr:
    return Return(Int(1))


def app1_case_16() -> Expr:
    return Return(Int(1))


def app1_case_17() -> Expr:
    return Return(Int(1))


def app1_case_18() -> Expr:
    return Seq(
        [
            Assert(
                And(
                    Gtxn[0].rekey_to() == Global.zero_address(),
                    Gtxn[Txn.group_index() + Int(4)].rekey_to() == Global.zero_address(),
                )
            ),
            Return(Int(1)),
        ]
    )


def app1_case_19() -> Expr:
    return Seq(
        [
            Assert(Gtxn[Txn.group_index() + Int(4)].rekey_to() == Global.zero_address()),
            Return(Int(1)),
        ]
    )


def app1_case_20() -> Expr:
    return Seq(
        [
            Assert(Gtxn[1].rekey_to() == Global.zero_address()),
            Return(Int(1)),
        ]
    )


def app1_case_21() -> Expr:
    return Seq(
        [
            Assert(Gtxn[Txn.group_index() + Int(2)].rekey_to() == Global.zero_address()),
            Return(Int(1)),
        ]
    )


def app1_case_22() -> Expr:
    return Return(Int(1))


def app1_case_23() -> Expr:
    return Return(Int(1))


def app1_case_24() -> Expr:
    return Return(Int(1))


def app1_case_25() -> Expr:
    return Return(Int(1))


def app1_case_26() -> Expr:
    return Return(Int(1))


def app1_case_27() -> Expr:
    return Return(Int(1))


def app1_case_28() -> Expr:
    return Seq(
        [
            Assert(Gtxn[Txn.group_index() + Int(5)].rekey_to() == Global.zero_address()),
            Return(Int(1)),
        ]
    )


def app1_case_29() -> Expr:
    return Return(Int(1))


def app1_case_30() -> Expr:
    return Seq([Assert(Gtxn[0].rekey_to() == Global.zero_address()), Return(Int(1))])


def app1_case_31() -> Expr:
    return Return(Int(1))


def app1_case_32() -> Expr:
    return Return(Int(1))


def app1_case_33() -> Expr:
    return Return(Int(1))


def app1_case_34() -> Expr:
    return Return(Int(1))


def app1_case_35() -> Expr:
    return Return(Int(1))


def app1_case_36() -> Expr:
    return Seq([Assert(Gtxn[4].rekey_to() == Global.zero_address()), Return(Int(1))])


def app1_case_37() -> Expr:
    return Return(Int(1))


def approval_program() -> Expr:
    test_case = Btoi(Txn.application_args[Int(0)])
    return Seq(
        [
            Assert(Txn.on_completion() == OnComplete.NoOp),
            Cond(
                [test_case == Int(1), app1_case_1()],
                [test_case == Int(2), app1_case_2()],
                [test_case == Int(3), app1_case_3()],
                [test_case == Int(4), app1_case_4()],
                [test_case == Int(5), app1_case_5()],
                [test_case == Int(6), app1_case_6()],
                [test_case == Int(7), app1_case_7()],
                [test_case == Int(8), app1_case_8()],
                [test_case == Int(9), app1_case_9()],
                [test_case == Int(10), app1_case_10()],
                [test_case == Int(11), app1_case_11()],
                [test_case == Int(12), app1_case_12()],
                [test_case == Int(13), app1_case_13()],
                [test_case == Int(14), app1_case_14()],
                [test_case == Int(15), app1_case_15()],
                [test_case == Int(16), app1_case_16()],
                [test_case == Int(17), app1_case_17()],
                [test_case == Int(18), app1_case_18()],
                [test_case == Int(19), app1_case_19()],
                [test_case == Int(20), app1_case_20()],
                [test_case == Int(21), app1_case_21()],
                [test_case == Int(22), app1_case_22()],
                [test_case == Int(23), app1_case_23()],
                [test_case == Int(24), app1_case_24()],
                [test_case == Int(25), app1_case_25()],
                [test_case == Int(26), app1_case_26()],
                [test_case == Int(27), app1_case_27()],
                [test_case == Int(28), app1_case_28()],
                [test_case == Int(29), app1_case_29()],
                [test_case == Int(30), app1_case_30()],
                [test_case == Int(31), app1_case_31()],
                [test_case == Int(32), app1_case_32()],
                [test_case == Int(33), app1_case_33()],
                [test_case == Int(34), app1_case_34()],
                [test_case == Int(35), app1_case_35()],
                [test_case == Int(36), app1_case_36()],
                [test_case == Int(37), app1_case_37()],
            ),
        ]
    )


def compile_program(output_file: Path) -> None:
    teal = compileTeal(approval_program(), mode=Mode.Application, version=7)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(teal)


if __name__ == "__main__":
    compile_program(Path("app_1.teal"))
