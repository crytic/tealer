# pylint: disable=undefined-variable
# type: ignore[name-defined]
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import


@Subroutine(TealType.none)  # type: ignore[misc]
def foo_bar(n: Expr) -> Expr:
    return If((n % Int(2)) == Int(0), Log(Bytes("Foo")), Log(Bytes("Bar")))


router = Router(
    name="SubroutineCFGExample",
    bare_calls=BareCallActions(),
)


@router.method(no_op=CallConfig.ALL)
def method_foo_bar() -> Expr:
    return foo_bar(Int(0))


pragma(compiler_version="0.22.0")
application_approval_program, _, _ = router.compile_program(version=7)

if __name__ == "__main__":
    print(application_approval_program)
