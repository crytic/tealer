# pylint: skip-file
# pylint: disable=undefined-variable
# type: ignore[name-defined]

"""
Template for pyteal test:

File containing the pyteal code
```
# pylint: disable=undefined-variable
# type: ignore[name-defined]
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import

def approval_program() -> Expr:
    return Return(Int(1))

def clear_program() -> Expr:
    return Return(Int(1))

approval_program_str = compileTeal(
    approval_program(),
    mode=Mode.Application,
    version=7,
    optimize=OptimizeOptions(scratch_slots=False),
)

_clear_program = compileTeal(
    clear_program(), mode=Mode.Application, version=7, optimize=OptimizeOptions(scratch_slots=False)
)
```

Test file that imports the pyteal code
```
# type: ignore[unreachable]
import sys
import pytest

from tealer.teal.instructions import instructions
from tealer.teal.parse_teal import parse_teal

if not sys.version_info >= (3, 10):
    pytest.skip(reason="PyTeal based tests require python >= 3.10", allow_module_level=True)

# pylint: disable=wrong-import-position
# Place import statements after the version check
from tests.pyteal_parsing.normal_application import normal_application_approval_program
```
"""

from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import


@Subroutine(TealType.none)  # type: ignore[misc]
def foo_bar(n: Expr) -> Expr:
    return While(n < Int(10)).Do(
        If(n < Int(5))
        .Then(
            Log(Bytes("Foo")),
        )
        .Else(
            Log(Bytes("Bar")),
        )
    )


@Subroutine(TealType.none)  # type: ignore[misc]
def break_continue(n: ScratchVar) -> Expr:
    i = ScratchVar()
    return While(Int(1)).Do(
        If(n.load() % Int(11) == Int(0)).Then(Break()),
        For(
            i.store(n.load()),
            i.load() < Int(25),
            i.store(i.load() + Int(3)),
        ).Do(If(n.load() % Int(4) == Int(0)).Then(Continue()), Log(Itob(i.load()))),
        n.store(n.load() + i.load() - Int(1)),
    )


@Subroutine(TealType.uint64)  # type: ignore[misc]
def factorial(n: Expr) -> Expr:
    # Note: Recursion is not supported if the subroutine takes ScratchVar type argument
    return If(
        n == Int(0),  # condition
        Return(Int(1)),  # then expression
        Return(n * factorial(n - Int(1))),  # else expression
    )


def call_all_subroutines() -> Expr:
    n = ScratchVar()
    return Pop(
        Seq(
            [
                Pop(
                    factorial(Int(10))
                ),  # All Expressions in the Seq must return TealType.none. Last expression is a exception.
                foo_bar(Int(1)),
                n.store(Int(0)),
                break_continue(n),  # ScratchVar types are taken as references.
                factorial(Int(5)),  # Last expression can return a value
            ]
        )  # Seq returns value of the last expression. Pop it to return none.
    )


def some_subroutines(c: Expr) -> Expr:
    n = ScratchVar()
    return Cond(
        [c == Int(0), Pop(factorial(Int(7)))],  # All branches should return same type
        [
            c == Int(1),
            Seq(
                n.store(Int(1)),
                foo_bar(n.load()),
            ),
        ],
        [c == Int(2), Seq([n.store(Int(0)), break_continue(n)])],
    )


def approval_program() -> Expr:
    return Seq(
        [
            call_all_subroutines(),
            some_subroutines(Int(1)),
            Approve(),
        ]
    )


control_flow_ap = compileTeal(
    approval_program(),
    mode=Mode.Application,
    version=7,
    optimize=OptimizeOptions(scratch_slots=True),
)

if __name__ == "__main__":
    print(control_flow_ap)
