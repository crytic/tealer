from typing import Tuple, List, Type
import pytest

from tealer.teal.basic_blocks import BasicBlock
from tealer.detectors.abstract_detector import AbstractDetector
from tealer.teal.parse_teal import parse_teal

from tests.detectors.groupsize import missing_group_size_tests
from tests.detectors.fee_check import missing_fee_check_tests
from tests.detectors.can_close_account import can_close_account_tests, new_can_close_account_tests
from tests.detectors.can_close_asset import can_close_asset_tests, new_can_close_asset_tests
from tests.detectors.can_delete import can_delete_tests, new_can_delete_tests
from tests.detectors.can_update import can_update_tests, new_can_update_tests
from tests.detectors.rekeyto import missing_rekeyto_tests, new_missing_rekeyto_tests

from tests.utils import cmp_cfg


ALL_TESTS: List[Tuple[str, Type[AbstractDetector], List[List[BasicBlock]]]] = [
    *missing_group_size_tests,
    *missing_fee_check_tests,
    *can_close_account_tests,
    *can_close_asset_tests,
    *can_delete_tests,
    *can_update_tests,
    *missing_rekeyto_tests,
]


@pytest.mark.parametrize("test", ALL_TESTS)  # type: ignore
def test_detectors(test: Tuple[str, Type[AbstractDetector], List[List[BasicBlock]]]) -> None:
    code, detector, expected_paths = test
    teal = parse_teal(code.strip())
    teal.register_detector(detector)
    result = teal.run_detectors()[0]
    assert len(result.paths) == len(expected_paths)
    for path, ex_path in zip(result.paths, expected_paths):
        assert cmp_cfg(path, ex_path)


ALL_NEW_TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    *new_can_close_account_tests,
    *new_missing_rekeyto_tests,
    *new_can_close_asset_tests,
    *new_can_update_tests,
    *new_can_delete_tests,
]


@pytest.mark.parametrize("test", ALL_NEW_TESTS)  # type: ignore
def test_just_detectors(test: Tuple[str, Type[AbstractDetector], List[List[int]]]) -> None:
    code, detector, expected_paths = test
    teal = parse_teal(code.strip())
    teal.register_detector(detector)
    result = teal.run_detectors()[0]
    for bi in teal.bbs:
        print(
            bi,
            bi.idx,
            bi.transaction_context.transaction_types,
            bi.transaction_context.group_indices,
        )
        print(
            bi.transaction_context.gtxn_context(0).transaction_types,
            bi.transaction_context.group_indices,
        )
        print(
            bi.transaction_context.gtxn_context(1).transaction_types,
            bi.transaction_context.group_indices,
        )

    assert len(result.paths) == len(expected_paths)
    for path, expected_path in zip(result.paths, expected_paths):
        assert len(path) == len(expected_path)
        for bi, expected_idx in zip(path, expected_path):
            assert bi.idx == expected_idx
