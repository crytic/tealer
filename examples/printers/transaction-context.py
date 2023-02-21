# pylint: disable=undefined-variable
# type: ignore[name-defined]
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import


def on_create() -> Expr:
    return Approve()


def op_a() -> Expr:
    return Seq(
        [
            Assert(And(Txn.group_index() == Int(0), Global.group_size() < Int(3))),
            Approve(),
        ]
    )


def op_b() -> Expr:
    return Seq(
        [
            If(
                Global.group_size() <= Int(4),
                If(
                    Global.group_size() == Int(3),
                    Assert(Txn.group_index() == Int(1)),
                    If(
                        Global.group_size() == Int(2),
                        Return(Txn.group_index() == Int(0)),
                    ),
                ),
                Assert(
                    And(
                        Global.group_size() > Int(5),
                        Global.group_size() < Int(11),
                        Txn.group_index() == Int(2),
                    )
                ),
            ),
            Approve(),
        ]
    )


# def approval_program() -> Expr:
#     return Cond(
#         [Txn.application_id() == Int(0), on_create()],
#         [Txn.application_args[Int(0)] == Bytes("a"), op_a()],
#         [Txn.application_args[Int(0)] == Bytes("b"), op_b()],
#     )


def approval_program() -> Expr:
    # return op_2()
    return Seq(
        [
            If(
                Global.group_size() <= Int(4),
                Seq(
                    [
                        Assert(Global.group_size() == Int(3)),
                        Assert(Txn.group_index() == Int(1)),
                    ]
                ),
                Assert(
                    And(
                        Global.group_size() > Int(5),
                        Global.group_size() < Int(11),
                        Txn.group_index() == Int(2),
                    )
                ),
            ),
            Approve(),
        ]
    )


pragma(compiler_version="0.22.0")
application_approval_program = compileTeal(approval_program(), mode=Mode.Application, version=7)

if __name__ == "__main__":
    print(application_approval_program)
