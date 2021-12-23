import json
import os
import sys
import pathlib
from pprint import pprint

import pytest
from deepdiff import DeepDiff

from tealer.utils.output import bbs_to_json
from tealer.teal.parse_teal import parse_teal


class Test:  # pylint: disable=too-few-public-methods
    def __init__(self, test_file: str):
        self.test_file = test_file
        self.expected_result = test_file + ".cfg.json"


ALL_TESTS = [
    Test("multiple_retsub.teal"),
    Test("subroutine_back_jump.teal"),
    Test("branches.teal"),
    Test("branching.teal"),
    Test("loopsandsub.teal"),
]


@pytest.mark.parametrize("test_item", ALL_TESTS)
def test_cfg_construction(test_item: Test) -> None:
    test_dir_path = pathlib.Path(
        pathlib.Path().absolute(),
        "tests",
        "cfg",
    )

    test_file_path = str(pathlib.Path(test_dir_path, test_item.test_file))
    expected_result_path = str(pathlib.Path(test_dir_path, test_item.expected_result).absolute())

    with open(test_file_path) as f:
        teal = parse_teal(f.read())

    results = bbs_to_json(teal.bbs)

    with open(expected_result_path, encoding="utf8") as f:
        expected_result = json.load(f)

    ignore_order_func = lambda level: "instructions" not in level.path()

    diff = DeepDiff(
        results, expected_result, ignore_order=True, ignore_order_func=ignore_order_func
    )

    if diff:
        pprint(diff)
        diff_as_dict = diff.to_dict()

        if "iterable_item_added" in diff_as_dict:
            print("#### Added blocks")
            print(diff_as_dict["iterable_item_added"])

        if "iterable_item_removed" in diff_as_dict:
            print("#### removed blocks")
            print(diff_as_dict["iterable_item_removed"])


def _generate_test(test_item: Test, skip_existing: bool = False) -> None:
    test_dir_path = pathlib.Path(
        pathlib.Path().absolute(),
        "tests",
        "cfg",
    )

    test_file_path = str(pathlib.Path(test_dir_path, test_item.test_file))
    expected_result_path = str(pathlib.Path(test_dir_path, test_item.expected_result).absolute())

    if skip_existing:
        if os.path.isfile(expected_result_path):
            return

    with open(test_file_path) as f:
        teal = parse_teal(f.read())

    results = bbs_to_json(teal.bbs)

    with open(expected_result_path, "w") as f:
        f.write(json.dumps(results, indent=4))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("To generate the json artifacts run\n\tpython tests/test_cfg.py --generate")
    elif sys.argv[1] == "--generate":
        for next_test in ALL_TESTS:
            _generate_test(next_test, skip_existing=True)
    elif sys.argv[1] == "--overwrite":
        for next_test in ALL_TESTS:
            _generate_test(next_test)
