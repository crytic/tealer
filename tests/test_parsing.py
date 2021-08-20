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
]


@pytest.mark.parametrize("target", TARGETS)
def test_parsing(target: str):
    with open(target) as f:
        teal = parse_teal(f.read())
    # print instruction to trigger __str__ on each ins
    for i in teal.instructions:
        print(i)
