# type: ignore[unreachable]
import sys
from typing import Tuple, List, Type

import pytest

from tealer.detectors.abstract_detector import AbstractDetector
from tealer.teal.parse_teal import parse_teal

if not sys.version_info >= (3, 10):
    pytest.skip(reason="PyTeal based tests require python >= 3.10", allow_module_level=True)

# Place import statements after the version check
from tests.detectors.router_with_assembled_constants import (  # pylint: disable=wrong-import-position
    router_with_assembled_constants,
)
from tests.detectors.pyteal_can_close import (  # pylint: disable=wrong-import-position
    txn_type_based_tests,
)
from tests.detectors.pyteal_group_size import (  # pylint: disable=wrong-import-position
    group_size_tests_pyteal,
)

from tests.detectors.pyteal_subroutine_recursion import (  # pylint: disable=wrong-import-position
    subroutine_recursion_patterns_tests,
)

from tests.detectors.multiple_calls_to_subroutine import (  # pylint: disable=wrong-import-position
    multiple_calls_to_subroutine_tests,
)

# pylint: disable=wrong-import-position
from tests.detectors.detector_reduced_output import reduced_output_tests


TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    *router_with_assembled_constants,
    *txn_type_based_tests,
    *group_size_tests_pyteal,
    *subroutine_recursion_patterns_tests,
    *multiple_calls_to_subroutine_tests,
    *reduced_output_tests,
]


@pytest.mark.parametrize("test", TESTS)  # type: ignore
def test_detectors_using_pyteal(test: Tuple[str, Type[AbstractDetector], List[List[int]]]) -> None:
    code, detector, expected_paths = test
    teal = parse_teal(code.strip())
    teal.register_detector(detector)
    result = teal.run_detectors()[0]
    # for bi in teal.bbs:
    #     print(
    #         bi,
    #         bi.idx,
    #         bi.transaction_context.transaction_types,
    #         bi.transaction_context.group_indices,
    #     )
    #     print(
    #         bi.transaction_context.gtxn_context(0).transaction_types,
    #         bi.transaction_context.group_indices,
    #     )
    #     print(
    #         bi.transaction_context.gtxn_context(1).transaction_types,
    #         bi.transaction_context.group_indices,
    #     )
    print("result paths =", result.paths)
    print("expected paths =", expected_paths)
    assert len(result.paths) == len(expected_paths)
    for path, expected_path in zip(result.paths, expected_paths):
        assert len(path) == len(expected_path)
        for bi, expected_idx in zip(path, expected_path):
            assert bi.idx == expected_idx
