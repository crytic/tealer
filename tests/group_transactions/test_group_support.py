from typing import Tuple, List, Type
from pathlib import Path
import pytest


from tealer.detectors.abstract_detector import AbstractDetector
from tealer.detectors.all_detectors import (
    MissingRekeyTo,
    MissingFeeCheck,
    CanCloseAccount,
    CanCloseAsset,
    IsUpdatable,
    IsDeletable,
    AnyoneCanDelete,
    AnyoneCanUpdate,
)
from tealer.utils.command_line.group_config import read_config_from_file
from tealer.utils.command_line.common import init_tealer_from_config
from tealer.utils.output import GroupTransactionOutput

from tests.group_transactions.utils import expected_output_from_file


# config, detector, expected output
ALL_TESTS: List[Tuple[Path, Type[AbstractDetector], Path]] = [
    (
        Path("tests/group_transactions/basic/config.yaml"),
        MissingRekeyTo,
        Path("tests/group_transactions/basic/expected_output.yaml"),
    ),
    (
        Path("tests/group_transactions/basic/config.yaml"),
        MissingFeeCheck,
        Path("tests/group_transactions/basic/expected_output.yaml"),
    ),
    (
        Path("tests/group_transactions/basic/config.yaml"),
        CanCloseAccount,
        Path("tests/group_transactions/basic/expected_output_close_to.yaml"),
    ),
    (
        Path("tests/group_transactions/basic/config.yaml"),
        CanCloseAsset,
        Path("tests/group_transactions/basic/expected_output_asset_close_to.yaml"),
    ),
    (
        Path("tests/group_transactions/basic/config.yaml"),
        IsUpdatable,
        Path("tests/group_transactions/basic/expected_output_update_delete.yaml"),
    ),
    (
        Path("tests/group_transactions/basic/config.yaml"),
        IsDeletable,
        Path("tests/group_transactions/basic/expected_output_update_delete.yaml"),
    ),
    (
        Path("tests/group_transactions/basic/config.yaml"),
        AnyoneCanUpdate,
        Path("tests/group_transactions/basic/expected_output_update_delete.yaml"),
    ),
    (
        Path("tests/group_transactions/basic/config.yaml"),
        AnyoneCanDelete,
        Path("tests/group_transactions/basic/expected_output_update_delete.yaml"),
    ),
]


# pylint: disable=too-many-locals
@pytest.mark.parametrize("test", ALL_TESTS)  # type: ignore
def test_instructions_output_detectors(test: Tuple[Path, Type[AbstractDetector], Path]) -> None:
    config_path, detector, expected_output_file_path = test

    expected_output = expected_output_from_file(expected_output_file_path)
    tealer = init_tealer_from_config(read_config_from_file(config_path))
    tealer.register_detector(detector)
    output = tealer.run_detectors()[0]

    reported_output: List["GroupTransactionOutput"] = []
    for i in output:
        assert isinstance(i, GroupTransactionOutput)
        reported_output.append(i)
        i.generate_output(Path("."))

    # expected output is also sorted by operation name
    reported_output = sorted(reported_output, key=lambda x: x.group_transaction.operation_name)
    expected_output_operations = sorted(expected_output.operations, key=lambda x: x.operation)
    # same number of groups/operations are reported as vulnerable
    assert len(reported_output) == len(expected_output_operations)

    for expected_operation, reported_operation in zip(expected_output_operations, reported_output):
        # reported same operation
        assert expected_operation.operation == reported_operation.group_transaction.operation_name
        # reported same transactions
        assert len(expected_operation.vulnerable_transactions) == len(
            reported_operation.transactions.keys()
        )
        expected_transactions = sorted(
            expected_operation.vulnerable_transactions, key=lambda x: x.transaction_id
        )
        reported_transactions = sorted(
            list(reported_operation.transactions.keys()), key=lambda x: x.transacton_id
        )

        for expected_txn, reported_txn in zip(expected_transactions, reported_transactions):
            # same transaction id
            assert expected_txn.transaction_id == reported_txn.transacton_id
            # same contracts
            expected_contracts = sorted(
                expected_txn.contracts, key=lambda x: (x.contract_name, x.function_name)
            )
            reported_contracts = sorted(
                reported_operation.transactions[reported_txn],
                key=lambda x: (x.contract.contract_name, x.function_name),
            )

            assert len(expected_contracts) == len(reported_contracts)
            for expected_contract, reported_contract in zip(expected_contracts, reported_contracts):
                # same contract name and function name
                assert expected_contract.contract_name == reported_contract.contract.contract_name
                assert expected_contract.function_name == reported_contract.function_name

    # for i in output:
    #     # assert isinstance(output, Gr)
    #     out = i.to_json()
    #     print(out["operation"])
    #     print(out["transactions"])
    # assert(False)
