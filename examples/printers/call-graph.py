# pylint: disable=undefined-variable
# type: ignore[name-defined]
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import


@Subroutine(TealType.none)
def my_subroutine():
    return Approve()


@Subroutine(TealType.none)
def recursive_subroutine(n: Expr) -> Expr:
    return If(
        n == Int(4),
        Return(),
        recursive_subroutine(n + Int(1)),
    )


@Subroutine(TealType.none)
def main_subroutine() -> Expr:
    return Seq([my_subroutine(), recursive_subroutine(Int(0))])


router = Router(
    name="CallGraphExample",
    bare_calls=BareCallActions(),
)


@router.method(no_op=CallConfig.CALL)
def method_a() -> Expr:
    return Seq([my_subroutine()])


@router.method(no_op=CallConfig.CALL)
def method_b() -> Expr:
    return Seq([main_subroutine()])


@router.method(no_op=CallConfig.CALL)
def method_c() -> Expr:
    return Approve()


pragma(compiler_version="0.22.0")
application_approval_program, _, _ = router.compile_program(version=7)

if __name__ == "__main__":
    print(application_approval_program)
