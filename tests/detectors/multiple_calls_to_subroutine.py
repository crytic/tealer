# pylint: skip-file
# mypy: ignore-errors
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import

from tealer.detectors.all_detectors import CanUpdate

router = Router(
    name="Test",
    bare_calls=BareCallActions(
        no_op=OnCompleteAction(action=Approve(), call_config=CallConfig.ALL),
    ),
)


@router.method(update_application=CallConfig.ALL)
def update_application() -> Expr:
    return Seq(
        [
            # IsUpdatable should report this path and will do so.
            # Assert(Global.creator_address() == Txn.sender()),
            Return(),
        ]
    )


working_approval_program, _, _ = router.compile_program(
    version=7,
)

false_negative_router = Router(
    name="FalseNegative",
    bare_calls=BareCallActions(
        no_op=OnCompleteAction(action=Approve(), call_config=CallConfig.CREATE),
    ),
)


@Subroutine(TealType.none)
def temp_sub() -> Expr:
    return Pop(Bytes("Call this subroutine twice"))


@false_negative_router.method(update_application=CallConfig.CALL)
def update_application_2() -> Expr:
    return Seq(
        [
            # IsUpdatable should report this path and but does not report it.
            # reason:
            #   1. When temp_sub is called for the first time, it's blocks are added
            #       to the path.
            #   2. And To avoid loops, detectors check that basic block they are processing
            #       is not already present in the `path`.
            #   3. When temp_sub is called for the second time, detectors think that it is a back edge/loop
            #       because `temp_sub` basic blocks are already added to the path on the first call.
            #
            #   TLDR; detectors do not report vulnerable paths, if there atleast 2 calls to the same subroutine in the path.
            # Above bug is fixed and tests should pass
            temp_sub(),
            temp_sub(),
            Return(),
        ]
    )


false_negative_program, _, _ = false_negative_router.compile_program(
    version=7,
)

working_approval_program_paths = [[0, 1, 3, 8, 4]]
false_negative_program_paths = [[0, 1, 3, 9, 8, 10, 8, 11, 4]]

multiple_calls_to_subroutine_tests = [
    (working_approval_program, CanUpdate, working_approval_program_paths),
    (false_negative_program, CanUpdate, false_negative_program_paths),
]

if __name__ == "__main__":
    print(working_approval_program)
    # print(false_negative_program)
