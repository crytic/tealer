# pylint: disable=undefined-variable
# type: ignore[name-defined]
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import


router = Router(
    name="HumanSummaryExample",
    bare_calls=BareCallActions(),
)


@Subroutine(TealType.none)
def is_creator() -> Expr:
    return Assert(Txn.sender() == Global.creator_address())


@router.method(no_op=CallConfig.CREATE)
def create() -> Expr:
    return Return()


@router.method(update_application=CallConfig.CALL)
def update_application() -> Expr:
    return is_creator()


@router.method(delete_application=CallConfig.CALL)
def delete_application() -> Expr:
    return is_creator()


@Subroutine(TealType.none)
def greet() -> Expr:
    return Log(Bytes("Hello"))


@router.method(no_op=CallConfig.CALL)
def hello() -> Expr:
    return greet()


pragma(compiler_version="0.22.0")
application_approval_program, _, _ = router.compile_program(version=7)

if __name__ == "__main__":
    print(application_approval_program)
