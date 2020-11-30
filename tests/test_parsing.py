import pytest

from tealer.teal.parse_teal import parse_teal

TARGETS = [
    "tests/parsing/transaction_fields.teal",
    "tests/parsing/global_fields.teal",
    "tests/parsing/instructions.teal",
]


@pytest.mark.parametrize("target", TARGETS)
def test_parsing(target: str):
    with open(target) as f:
        teal = parse_teal(f.read())
    # print instruction to trigger __str__ on each ins
    for i in teal.instructions:
        print(i)
