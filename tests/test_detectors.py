from typing import Tuple, List, Type
import pytest

from tealer.teal.basic_blocks import BasicBlock
from tealer.detectors.abstract_detector import AbstractDetector
from tealer.utils.command_line.common import init_tealer_from_single_contract
from tealer.utils.output import ExecutionPaths, InstructionsOutput

from tests.detectors.groupsize import missing_group_size_tests
from tests.detectors.fee_check import missing_fee_check_tests, new_missing_fee_tests
from tests.detectors.can_close_account import can_close_account_tests, new_can_close_account_tests
from tests.detectors.can_close_asset import can_close_asset_tests, new_can_close_asset_tests
from tests.detectors.can_delete import can_delete_tests, new_can_delete_tests
from tests.detectors.can_update import can_update_tests, new_can_update_tests
from tests.detectors.optimizations.constant_gtxn import constant_gtxn
from tests.detectors.optimizations.sender_access import sender_access
from tests.detectors.optimizations.self_access import self_access
from tests.detectors.rekeyto import missing_rekeyto_tests, new_missing_rekeyto_tests
from tests.detectors.subroutine_patterns import subroutine_patterns_tests

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
    tealer = init_tealer_from_single_contract(code.strip(), "test")
    tealer.register_detector(detector)
    result = tealer.run_detectors()[0][0]

    if isinstance(result, ExecutionPaths):
        assert len(result.paths) == len(expected_paths)
        for path, ex_path in zip(result.paths, expected_paths):
            assert cmp_cfg(path, ex_path)

    else:
        # Not implemented yet
        assert False


ALL_NEW_TESTS: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    *new_can_close_account_tests,
    *new_missing_rekeyto_tests,
    *new_can_close_asset_tests,
    *new_can_update_tests,
    *new_can_delete_tests,
    *new_missing_fee_tests,
    *subroutine_patterns_tests,
]


@pytest.mark.parametrize("test", ALL_NEW_TESTS)  # type: ignore
def test_just_detectors(test: Tuple[str, Type[AbstractDetector], List[List[int]]]) -> None:
    code, detector, expected_paths = test
    tealer = init_tealer_from_single_contract(code.strip(), "test")
    tealer.register_detector(detector)
    result = tealer.run_detectors()[0][0]

    if isinstance(result, ExecutionPaths):
        print(f"count: result = {len(result.paths)}, expected = {len(expected_paths)}")
        assert len(result.paths) == len(expected_paths)
        for path, expected_path in zip(result.paths, expected_paths):
            print(f"path length: result = {len(path)}, expected = {len(expected_path)}")
            print(f"path ids: result = {path}, expected = {expected_path}")
            assert len(path) == len(expected_path)
            for bi, expected_idx in zip(path, expected_path):
                assert bi.idx == expected_idx

    else:
        # Not implemented yet
        assert False


# This test is for the detectors using InstructionsOutput
# This type return only a list of instructions
# So we compare the expected lines of the source code
# source code -> detector -> lust(expected lines)
TESTS_INSTRUCTIONS_OUTPUT: List[Tuple[str, Type[AbstractDetector], List[List[int]]]] = [
    *constant_gtxn,
    *sender_access,
    *self_access,
]


@pytest.mark.parametrize("test", TESTS_INSTRUCTIONS_OUTPUT)  # type: ignore
def test_instructions_output_detectors(
    test: Tuple[str, Type[AbstractDetector], List[List[int]]]
) -> None:
    code, detector, expected_instruction_lines = test
    tealer = init_tealer_from_single_contract(code.strip(), "test")
    tealer.register_detector(detector)
    result = tealer.run_detectors()[0][0]

    if isinstance(result, InstructionsOutput):
        print(
            f"count: result = {len(result.instructions)}, expected = {len(expected_instruction_lines)}"
        )

        actual_instruction_lines = [
            [ins.line for ins in instructions] for instructions in result.instructions
        ]

        assert actual_instruction_lines == expected_instruction_lines

    else:
        # Not implemented yet
        assert False
