# pylint: skip-file
# mypy: ignore-errors
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import

from pyteal import *
from typing import Literal

from tealer.detectors.all_detectors import CanUpdate, CanDelete

router = Router(
    name="Example",
    bare_calls=BareCallActions(),
)

"""
Pattern for method config having CallConfig.CALL:
    txn OnCompletion
    int NoOp
    ==
    txn ApplicationID
    int 0
    !=
    &&
    assert

Pattern for method config having CallConfig.CREATE:
    txn OnCompletion
    int NoOp
    ==
    txn ApplicationID
    int 0
    ==
    &&
    assert

Pattern for method config having CallConfig.ALL:
    txn OnCompletion
    int NoOp
    ==
    assert

Tealer cannot calculate the information from first two patterns. For that reason, all of the
methods have CallConfig.ALL.
"""


@router.method(no_op=CallConfig.ALL)
def echo(input: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """
    Method config validations Teal pattern:
        txn OnCompletion
        int NoOp
        ==
        txn ApplicationID
        int 0
        !=
        &&
        assert            // Assert(NoOp, CALL)
    """
    return output.set(input.get())


@router.method(opt_in=CallConfig.ALL)
def deposit() -> Expr:
    return Return()


@router.method(close_out=CallConfig.ALL)
def getBalance() -> Expr:
    return Return()


@router.method(update_application=CallConfig.ALL)
def update() -> Expr:
    return Err()


@router.method(delete_application=CallConfig.ALL)
def delete() -> Expr:
    return Err()


# does not matter even if multiple actions are allowed as it fails for all calls.
@router.method(no_op=CallConfig.CALL, opt_in=CallConfig.CREATE, close_out=CallConfig.ALL)
def some(input: abi.Uint64) -> Expr:
    return Err()


# PyTeal creates intcblock, bytecblock if assemble_constants = True
# int NoOp, OptIn, ... are all replaced by intc_* instructions.
# pragma(compiler_version="0.22.0")
approval_program, clear_state_program, contract = router.compile_program(
    version=7,
    assemble_constants=True,  # use intcblock, bytecblock
    # optimize=OptimizeOptions(scratch_slots=True),
)

router_with_assembled_constants = [
    (approval_program, CanUpdate, []),
    (approval_program, CanDelete, []),
]