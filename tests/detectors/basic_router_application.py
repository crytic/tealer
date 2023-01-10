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


@router.method(no_op=CallConfig.CALL)
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


@router.method(no_op=CallConfig.CALL, opt_in=CallConfig.CREATE)
def deposit() -> Expr:
    """
    Allow execution of this method if and only if:
        - OnCompletion is NoOp AND `txn ApplicationID != 0`(Not a creation txn, so a Call)
        Or
        - OnCompletion is OptIn AND `txn ApplicationID == 0`(Creation Txn)

    Execution will fail for all other OnCompletion actions

    Method config validations Teal pattern:
        txn OnCompletion
        int NoOp
        ==
        txn ApplicationID
        int 0
        !=
        &&                      // (NoOp && CALL)
        txn OnCompletion
        int OptIn
        ==
        txn ApplicationID
        int 0
        ==
        &&                      // (OptIn && CREATE)
        ||
        assert                  // Assert((NoOp && CALL) || (OptIn && CREATE))
    """
    return Return()


@router.method(no_op=CallConfig.ALL, opt_in=CallConfig.CALL, close_out=CallConfig.CALL)
def getBalance() -> Expr:
    """
    Allow execution of this method if and only if:
        - OnCompletion is NoOp; `txn ApplicationID` is not accessed/checked for CallConfig.ALL
        Or
        - OnCompletion is OptIn AND `txn ApplicationID == 0` (Creation Txn)
        Or
        - OnCompletion is CloseOut AND `txn ApplicationID != 0`  (Not a creation txn -> Call)

    Method config validations Teal pattern:
        txn OnCompletion
        int NoOp
        ==                      // (NoOp && ALL) => (NoOp)
        txn OnCompletion
        int OptIn
        ==
        txn ApplicationID
        int 0
        !=
        &&                      // (OptIn && CALL)
        ||
        txn OnCompletion
        int CloseOut
        ==
        txn ApplicationID       // Code is repeated for every CALL check; No optimizations
        int 0
        !=
        &&                      // (CloseOut && CALL)
        ||
        assert                  // Assert((NoOp && ALL) || (OptIn && CALL) || (CloseOut && CALL))
    """
    return Return()


pragma(compiler_version="0.20.1")
basic_router_approval_program, clear_state_program, contract = router.compile_program(
    version=7,  # optimize=OptimizeOptions(scratch_slots=True)
)

basic_router_tests = [
    (basic_router_approval_program, CanUpdate, []),
    (basic_router_approval_program, CanDelete, []),
]
