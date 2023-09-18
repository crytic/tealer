# pylint: skip-file
# mypy: ignore-errors
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import

from pyteal import *

from tealer.detectors.all_detectors import CanCloseAsset, CanCloseAccount

router = Router(
    name="Example",
    bare_calls=BareCallActions(),
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

    Args:
        input: Input argument
        output: Return value of the echo method.

    Returns:
        Body of the echo method as PyTeal expr.
    """
    return output.set(input.get())


# pragma(compiler_version="0.22.0")
application_approval_program, _, _ = router.compile_program(
    version=7,
    assemble_constants=True,  # use intcblock, bytecblock
    # optimize=OptimizeOptions(scratch_slots=True),
)


@Subroutine(TealType.none)
def process_txn() -> Expr:
    return Pop(Bytes("ExecuteTransaction"))


def axfer_approval_program():
    @Subroutine(TealType.none)
    def validate_txn() -> Expr:
        return Seq(
            [
                Assert(Global.group_size() == Int(1)),
                Assert(Txn.fee() <= Global.min_txn_fee()),
                Assert(Txn.type_enum() == TxnType.AssetTransfer),
                Assert(Txn.asset_close_to() == Global.zero_address()),
            ]
        )

    return Seq(
        [
            validate_txn(),
            process_txn(),
            Return(Int(1)),
        ]
    )


axfer_approval_program_teal = compileTeal(axfer_approval_program(), mode=Mode.Signature, version=7)


def payment_approval_program():
    @Subroutine(TealType.none)
    def validate_txn() -> Expr:
        return Seq(
            [
                Assert(Global.group_size() == Int(1)),
                Assert(Txn.fee() <= Global.min_txn_fee()),
                Assert(Txn.type_enum() == TxnType.Payment),
                Assert(Txn.close_remainder_to() == Global.zero_address()),
            ]
        )

    return Seq(
        [
            validate_txn(),
            process_txn(),
            Return(Int(1)),
        ]
    )


payment_approval_program_teal = compileTeal(
    payment_approval_program(), mode=Mode.Signature, version=7
)


def axfer_payment_approval_program():
    return (
        If(Arg(Int(0)) == Bytes("Payment In Algo"))
        .Then(
            payment_approval_program(),
        )
        .Else(
            axfer_approval_program(),
        )
    )


axfer_payment_approval_program_teal = compileTeal(
    axfer_payment_approval_program(), mode=Mode.Signature, version=7
)


def different_group_sizes_approval_program():
    group_size_3 = Seq(
        [
            Assert(Global.group_size() == Int(3)),
            Assert(Gtxn[0].fee() <= Global.min_txn_fee()),
            Assert(Gtxn[0].type_enum() == TxnType.Payment),
            Assert(Gtxn[0].close_remainder_to() == Global.zero_address()),
            Assert(Gtxn[1].fee() <= Global.min_txn_fee()),
            Assert(Gtxn[1].type_enum() == TxnType.KeyRegistration),
            Assert(Gtxn[2].fee() <= Global.min_txn_fee()),
            Assert(Gtxn[2].type_enum() == TxnType.AssetConfig),
            Assert(Gtxn[2].close_remainder_to() == Global.zero_address()),
            Return(Int(1)),
        ]
    )

    group_size_2 = Seq(
        [
            Assert(Global.group_size() == Int(2)),
            Assert(Gtxn[0].fee() <= Global.min_txn_fee()),
            Assert(Gtxn[0].type_enum() == TxnType.AssetTransfer),
            Assert(Gtxn[0].asset_close_to() == Txn.sender()),
            Assert(Gtxn[1].fee() <= Global.min_txn_fee()),
            Assert(Gtxn[1].type_enum() == TxnType.AssetFreeze),
            Return(Int(1)),
        ]
    )

    return (
        If(Arg(Int(0)) == Bytes("First Operation"))
        .Then(
            group_size_2,
        )
        .Else(group_size_3)
    )


different_group_sizes_approval_program_teal = compileTeal(
    different_group_sizes_approval_program(), mode=Mode.Signature, version=7
)


txn_type_based_tests = [
    (application_approval_program, CanCloseAccount, []),
    (application_approval_program, CanCloseAsset, []),
    (axfer_approval_program_teal, CanCloseAccount, []),
    (axfer_approval_program_teal, CanCloseAsset, []),
    (payment_approval_program_teal, CanCloseAccount, []),
    (payment_approval_program_teal, CanCloseAsset, []),
    (axfer_payment_approval_program_teal, CanCloseAccount, []),
    (axfer_payment_approval_program_teal, CanCloseAsset, []),
    (different_group_sizes_approval_program_teal, CanCloseAccount, []),
    (different_group_sizes_approval_program_teal, CanCloseAsset, []),
]
