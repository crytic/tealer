# type: ignore[unreachable]
import sys
from typing import Tuple, List, Type

import pytest

from tealer.detectors.abstract_detector import AbstractDetector
from tealer.teal.parse_teal import parse_teal

if not sys.version_info >= (3, 10):
    pytest.skip(reason="PyTeal based tests require python >= 3.10", allow_module_level=True)

# Place import statements after the version check
from tests.detectors.basic_router_application import (  # pylint: disable=wrong-import-position
    basic_router_tests,
)

TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    *basic_router_tests,
]


@pytest.mark.parametrize("test", TESTS)  # type: ignore
def test_parsing_using_pyteal(test: Tuple[str, Type[AbstractDetector], List[List[int]]]) -> None:
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
