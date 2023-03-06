# pylint: skip-file
# mypy: ignore-errors
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import

from pyteal import *

from tealer.detectors.all_detectors import IsUpdatable, IsDeletable

from tests.pyteal_parsing.control_flow_constructs import (
    some_subroutines,
    call_all_subroutines,
    approval_program as control_flow_constructs_ap,
)

barecalls = BareCallActions(
    no_op=OnCompleteAction(action=Approve(), call_config=CallConfig.CREATE),
    opt_in=OnCompleteAction(action=Approve(), call_config=CallConfig.ALL),
    close_out=OnCompleteAction(action=Approve(), call_config=CallConfig.CALL),
    update_application=OnCompleteAction(call_config=CallConfig.NEVER),
    delete_application=OnCompleteAction(call_config=CallConfig.NEVER),
)

router = Router(
    name="Example",
    bare_calls=barecalls,
)


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


@router.method(update_application=CallConfig.ALL)
def update() -> Expr:
    # method entry point: B13
    # path: B0, B1, B2, B13

    # if execution reaches this method, the application can be updated.
    # Usually, detectors report all enumerated paths.
    # The number of output files can be reduced by truncating the paths to a certain basic block "Bt".
    # The block "Bt" has the property that, all subsequent paths leading from "Bt" are considered vulnerable.
    # In this example ("IsUpdatable") should report all paths that involves executing this method.
    # Instead of reporting every path, the detector will only report path upto the method entry point block.
    return Seq([some_subroutines(Int(1)), Approve()])


@router.method(delete_application=CallConfig.ALL)
def delete() -> Expr:
    # detector output should contain
    return If(
        Int(2) == Int(1) + App.globalGet(Bytes("key")),
        Reject(),
        # IsDeletable reports if execution reach this block
        # path: B0, B1, B2, B3, B11, B56, B57
        Seq([call_all_subroutines(), Approve()]),
    )


@router.method(update_application=CallConfig.CALL)
def update_2() -> Expr:
    return Cond(
        # IsUpdatable reports path for this. This is also a leaf path.
        # path: B0, B1, B2, B3, B4, B9, B63, B73
        [App.globalGet(Bytes("key")), Approve()],
        # IsUpdatable does not report this.
        [App.globalGet(Bytes("key2")), Reject()],
        # IsUpdatable reports all paths that reached this block.
        # IsUpdatable should output 2 files, one for above path and another for all paths leading from this block.
        # path: B0, B1, B2, B3, B4, B9, B63, B64, B65, B67
        [Int(1), call_all_subroutines(), Approve()],
    )


@router.method(update_application=CallConfig.CALL)
def update_3() -> Expr:
    return If(
        App.globalGet(Bytes("key")),
        # IsUpdatable reports path for this. This is also a leaf path.
        # path: B0, B1, B2, B3, B4, B5, B7, B74, B80
        Approve(),
        # IsUpdatable reports all paths that reached this block.
        # IsUpdatable should output 1 file that represents all paths executing this method.
        # path: B0, B1, B2, B3, B4, B5, B7, B74, B75
        Seq([call_all_subroutines(), Approve()]),
    )


# PyTeal creates intcblock, bytecblock if assemble_constants = True
# int NoOp, OptIn, ... are all replaced by intc_* instructions.
# pragma(compiler_version="0.22.0")
approval_program, clear_state_program, contract = router.compile_program(
    version=7,
    assemble_constants=True,  # use intcblock, bytecblock
    # optimize=OptimizeOptions(scratch_slots=True),
)

IS_UPDATABLE_VULNERABLE_PATHS = [
    [0, 1, 2, 3, 4, 5, 7],  # update_3(),
    [0, 1, 2, 3, 4, 9, 63, 64, 65, 67],  # update_2()
    [0, 1, 2, 3, 4, 9, 63, 73],  # update_2()
    # below three paths are not reduced to [0, 1, 2, 13] because
    # [0, 1, 2, 13, 45, 46, 47, 48] is a child path and is not vulnerable
    [0, 1, 2, 13, 45, 46, 47, 49],  # update()
    [0, 1, 2, 13, 45, 46, 51],  # update()
    [0, 1, 2, 13, 45, 53],  # update()
]

IS_DELETABLE_VULNERABLE_PATHS = [[0, 1, 2, 3, 11, 56, 57]]  # delete()

reduced_output_tests = [
    (approval_program, IsUpdatable, IS_UPDATABLE_VULNERABLE_PATHS),
    (approval_program, IsDeletable, IS_DELETABLE_VULNERABLE_PATHS),
]


if __name__ == "__main__":
    print(approval_program)
