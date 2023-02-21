# pylint: disable=undefined-variable
# type: ignore[name-defined]
from pyteal import *  # pylint: disable=wildcard-import,unused-wildcard-import

router = Router(
    name="CFGExample",
    bare_calls=BareCallActions(),
)


@router.method(no_op=CallConfig.CREATE)
def create() -> Expr:
    return Return()


@router.method(opt_in=CallConfig.CALL)
def opt_in() -> Expr:
    return Return()


pragma(compiler_version="0.22.0")
application_approval_program, _, _ = router.compile_program(version=7)

if __name__ == "__main__":
    print(application_approval_program)
