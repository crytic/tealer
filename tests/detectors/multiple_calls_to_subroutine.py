# pylint: skip-file
# mypy: ignore-errors
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import

from tealer.detectors.all_detectors import IsUpdatable

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


method_returns_using_approve = Router(
    name="MethodReturnsUsingApprove",
    bare_calls=BareCallActions(
        no_op=OnCompleteAction(action=Approve(), call_config=CallConfig.CREATE),
    ),
)


@method_returns_using_approve.method(update_application=CallConfig.CALL)
def update_application_3() -> Expr:
    return Approve()


method_returns_using_approve_program, _, _ = method_returns_using_approve.compile_program(
    version=7,
)

method_returns_using_approve_program_teal = """
#pragma version 7       // B0
txn NumAppArgs
int 0
==
bnz main_l4

txna ApplicationArgs 0          // B1
method "update_application_3()void"
==
bnz main_l3

err             // B2

main_l3:            // B3
txn OnCompletion
int UpdateApplication
==
txn ApplicationID
int 0
!=
&&
assert
callsub updateapplication3_0

int 1       // B4
return

main_l4:    // B5
txn OnCompletion
int NoOp
==
bnz main_l6

err         // B6

main_l6:        // B7
txn ApplicationID
int 0
==
assert
int 1
return

// update_application_3
updateapplication3_0:   // B8
int 1
return
"""

# Each of router methods have a corresponding subroutine in the compiled code.
# `updateapplication3_0` subroutine for update_application_3() method in above example.
# PyTeal implicitly adds instructions `int 1; return;` after the call to the subroutine of the method.
# See block B4 in above code.
# PyTeal adds those instructions even if the subroutine uses `return` instead of `retsub`.
# This is a problem for Tealer. Because, B4 is considered as a return point to `callsub` instruction.
# B4 does not have any predecessors and execution is not reachable.
# During the TransactionFieldAnalysis, information of return point block is used to calculate information for callsub block.
# And because B4 is not reachable, it will have empty set for possible values. In backward propagation, information from B4
# is intersected with information of B3 resulting in empty set of possible values for B3 as well. This propagates across the CFG
# and blocks will have incorrect information.

# This bug is now fixed.

method_returns_using_approve_program_paths = [[0, 1, 3, 8]]

method_returns_using_approve_2 = Router(
    name="MethodReturnsUsingApprove",
    bare_calls=BareCallActions(
        no_op=OnCompleteAction(action=Approve(), call_config=CallConfig.CREATE),
    ),
)


@method_returns_using_approve_2.method(update_application=CallConfig.CALL)
def update_application_3() -> Expr:
    # return in one path of the subroutine.
    # And retsub in another path of the subroutine.
    return If(Txn.application_args[0] == Bytes("Update"), Approve(), Return())


method_returns_using_approve_2_program, _, _ = method_returns_using_approve_2.compile_program(
    version=7
)

method_returns_using_approve_2_program_paths = [
    [0, 1, 3, 8, 9, 4],
    [0, 1, 3, 8, 10],
]

multiple_calls_to_subroutine_tests = [
    (working_approval_program, IsUpdatable, working_approval_program_paths),
    (false_negative_program, IsUpdatable, false_negative_program_paths),
    (method_returns_using_approve_program, IsUpdatable, method_returns_using_approve_program_paths),
    (
        method_returns_using_approve_2_program,
        IsUpdatable,
        method_returns_using_approve_2_program_paths,
    ),
]

if __name__ == "__main__":
    print(working_approval_program)
    print(false_negative_program)
    print(method_returns_using_approve_program)
    print(method_returns_using_approve_2_program)
