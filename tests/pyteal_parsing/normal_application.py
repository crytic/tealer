# pylint: skip-file
# pylint: disable=undefined-variable
# type: ignore[name-defined]
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import


@Subroutine(TealType.uint64)
def add_upto_n(n: ScratchVar) -> Expr:
    i = ScratchVar()
    result = ScratchVar()
    return Seq(
        [
            result.store(Int(0)),
            For(i.store(Int(0)), i.load() < n.load(), i.store(i.load() + Int(1))).Do(
                result.store(result.load() + i.load())
            ),
            Return(result.load()),
        ]
    )


def on_creation() -> Expr:
    x = ScratchVar()
    return Seq([x.store(Int(10)), Pop(add_upto_n(x)), Return(Int(1))])


def approval_program() -> Expr:
    return Cond(
        [Txn.application_id() == Int(0), on_creation()],
        [Txn.on_completion() == OnComplete.DeleteApplication, Reject()],
        [Txn.on_completion() == OnComplete.UpdateApplication, Reject()],
        [Txn.on_completion() == OnComplete.CloseOut, Approve()],
        [Txn.on_completion() == OnComplete.OptIn, Approve()],
    )


def clear_program() -> Expr:
    return Return(Int(1))


normal_application_approval_program = compileTeal(
    approval_program(),
    mode=Mode.Application,
    version=7,
    optimize=OptimizeOptions(scratch_slots=False),
    assembleConstants=True,
)

_clear_program = compileTeal(
    clear_program(), mode=Mode.Application, version=7, optimize=OptimizeOptions(scratch_slots=False)
)

if __name__ == "__main__":
    print(normal_application_approval_program)
