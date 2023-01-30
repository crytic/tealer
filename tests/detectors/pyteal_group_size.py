# pylint: skip-file
# mypy: ignore-errors
from typing import List
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import


from tealer.detectors.all_detectors import MissingGroupSize


@Subroutine(TealType.none)
def transfer_wrapped_algo(_receiver: Expr, _amount: Expr) -> Expr:
    return Pop(Bytes("Inner txn to transfer assets"))


@Subroutine(TealType.none)
def transfer_algo(_receiver: Expr, _amount: Expr) -> Expr:
    return Pop(Bytes("Inner txn to transfer Algos"))


def mint_wrapped_algo() -> Expr:
    validations = Assert(
        And(
            Gtxn[0].receiver() == Global.current_application_address(),
            Gtxn[0].type_enum() == TxnType.Payment,
        )
    )
    transfer_op = transfer_wrapped_algo(Txn.sender(), Gtxn[0].amount())
    return Seq([validations, transfer_op, Approve()])


def burn_wrapped_algo() -> Expr:
    validations = Assert(
        And(
            # Gtxn[Int(x)] => int x; gtxn ...
            Gtxn[Int(0)].receiver() == Global.current_application_address(),
            Gtxn[Int(0)].type_enum() == TxnType.AssetTransfer,
            Gtxn[Int(0)].xfer_asset() == Int(1337),
        )
    )
    transfer_op = transfer_algo(Txn.sender(), Gtxn[0].asset_amount())
    return Seq([validations, transfer_op, Approve()])


def mint_wrapped_algo_fixed() -> Expr:
    validations = Assert(
        And(
            # Gtxn[Int(x)] => int x; gtxn ...
            Gtxn[Int(0)].receiver() == Global.current_application_address(),
            Gtxn[0].type_enum() == TxnType.Payment,
            Global.group_size() == Int(2),
        )
    )
    transfer_op = transfer_wrapped_algo(Txn.sender(), Gtxn[0].amount())
    return Seq([validations, transfer_op, Approve()])


def burn_wrapped_algo_fixed() -> Expr:
    index = Txn.group_index() - Int(1)
    validations = Assert(
        And(
            Gtxn[index].receiver() == Global.current_application_address(),
            Gtxn[index].type_enum() == TxnType.AssetTransfer,
            Gtxn[index].xfer_asset() == Int(1337),
        )
    )
    transfer_op = transfer_algo(Txn.sender(), Gtxn[index].asset_amount())
    return Seq([validations, transfer_op, Approve()])


def wrapped_approval_program_1() -> Expr:
    return Cond(
        [Txn.application_args[0] == Bytes("mint"), mint_wrapped_algo()],
        [Txn.application_args[0] == Bytes("burn"), burn_wrapped_algo()],
    )


def wrapped_approval_program_2() -> Expr:
    return Cond(
        [Txn.application_args[0] == Bytes("mint"), mint_wrapped_algo_fixed()],
        [Txn.application_args[0] == Bytes("burn"), burn_wrapped_algo()],
    )


def wrapped_approval_program_3() -> Expr:
    return Cond(
        [Txn.application_args[0] == Bytes("mint"), mint_wrapped_algo()],
        [Txn.application_args[0] == Bytes("burn"), burn_wrapped_algo_fixed()],
    )


def wrapped_approval_program_4() -> Expr:
    return Cond(
        [Txn.application_args[0] == Bytes("mint"), mint_wrapped_algo_fixed()],
        [Txn.application_args[0] == Bytes("burn"), burn_wrapped_algo_fixed()],
    )


wrapped_approval_program_1_teal = compileTeal(
    wrapped_approval_program_1(),
    mode=Mode.Application,
    version=8,
)

wrapped_approval_program_1_vulnerable_paths: List[List[int]] = [
    [0, 1, 3, 8, 4],  # burn
    [0, 5, 7, 6],  # mint
]

wrapped_approval_program_2_teal = compileTeal(
    wrapped_approval_program_2(),
    mode=Mode.Application,
    version=8,
)

wrapped_approval_program_2_vulnerable_paths: List[List[int]] = [
    [0, 1, 3, 8, 4],
]

wrapped_approval_program_3_teal = compileTeal(
    wrapped_approval_program_3(),
    mode=Mode.Application,
    version=8,
)

wrapped_approval_program_3_vulnerable_paths: List[List[int]] = [
    [0, 5, 7, 6],
]

wrapped_approval_program_4_teal = compileTeal(
    wrapped_approval_program_4(),
    mode=Mode.Application,
    version=8,
)

wrapped_approval_program_4_vulnerable_paths: List[List[int]] = []


group_size_tests_pyteal = [
    (
        wrapped_approval_program_1_teal,
        MissingGroupSize,
        wrapped_approval_program_1_vulnerable_paths,
    ),
    (
        wrapped_approval_program_2_teal,
        MissingGroupSize,
        wrapped_approval_program_2_vulnerable_paths,
    ),
    (
        wrapped_approval_program_3_teal,
        MissingGroupSize,
        wrapped_approval_program_3_vulnerable_paths,
    ),
    (
        wrapped_approval_program_4_teal,
        MissingGroupSize,
        wrapped_approval_program_4_vulnerable_paths,
    ),
]

if __name__ == "__main__":
    print(wrapped_approval_program_3_teal)
