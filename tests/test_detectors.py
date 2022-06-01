from typing import Tuple, List, Type
import pytest

from tealer.teal.basic_blocks import BasicBlock
from tealer.detectors.abstract_detector import AbstractDetector
from tealer.teal.parse_teal import parse_teal

from tests.detectors.groupsize import missing_group_size_tests
from tests.detectors.fee_check import missing_fee_check_tests
from tests.detectors.can_close_account import can_close_account_tests
from tests.detectors.can_close_asset import can_close_asset_tests
from tests.detectors.can_delete import can_delete_tests
from tests.detectors.can_update import can_update_tests
from tests.detectors.rekeyto import missing_rekeyto_tests

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


@pytest.mark.parametrize("test", ALL_TESTS)
def test_detectors(test: Tuple[str, Type[AbstractDetector], List[List[BasicBlock]]]) -> None:
    code, detector, expected_paths = test
    teal = parse_teal(code.strip())
    teal.register_detector(detector)
    result = teal.run_detectors()[0]
    assert len(result.paths) == len(expected_paths)
    for path, ex_path in zip(result.paths, expected_paths):
        assert cmp_cfg(path, ex_path)
