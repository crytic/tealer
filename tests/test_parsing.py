import pytest

from tealer.teal.parse_teal import parse_teal

TARGETS = [
    "tests/parsing/transaction_fields.teal",
    "tests/parsing/global_fields.teal",
    "tests/parsing/instructions.teal",
    "tests/parsing/instructions.teal",
    "tests/parsing/instructions.teal",
    "tests/parsing/teal3-gload.teal",
    "tests/parsing/teal4-test0.teal",
    "tests/parsing/teal4-test1.teal",
    "tests/parsing/teal4-test2.teal",
    "tests/parsing/teal4-test3.teal",
    "tests/parsing/teal4-test4.teal",
    "tests/parsing/teal4-test5.teal",
    "tests/parsing/teal4-random-opcodes.teal",
    "tests/parsing/comments.teal",
    "tests/parsing/asset_holding_get.teal",
    "tests/parsing/asset_params_get.teal",
    "tests/parsing/teal5-app_params_get.teal",
    "tests/parsing/teal5-ecdsa.teal",
    "tests/parsing/teal5-extract.teal",
    "tests/parsing/teal5-itxn.teal",
    "tests/parsing/teal5-itxna.teal",
    "tests/parsing/teal5-mixed.teal",
]


@pytest.mark.parametrize("target", TARGETS)  # type: ignore
def test_parsing(target: str) -> None:
    with open(target) as f:
        teal = parse_teal(f.read())
    # print instruction to trigger __str__ on each ins
    for i in teal.instructions:
        print(i)
