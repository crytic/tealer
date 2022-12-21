# type: ignore[unreachable]
import sys
import pytest

from tealer.teal.instructions import instructions
from tealer.teal.parse_teal import parse_teal

if not sys.version_info >= (3, 10):
    pytest.skip(reason="PyTeal based tests require python >= 3.10", allow_module_level=True)

# Place import statements after the version check
from tests.pyteal_parsing.normal_application import (  # pylint: disable=wrong-import-position
    normal_application_approval_program,
)

TARGETS = [
    normal_application_approval_program,
]


@pytest.mark.parametrize("target", TARGETS)  # type: ignore
def test_parsing_using_pyteal(target: str) -> None:
    teal = parse_teal(target)
    # print instruction to trigger __str__ on each ins
    for i in teal.instructions:
        assert not isinstance(i, instructions.UnsupportedInstruction), f'ins "{i}" is not supported'
        print(i, i.cost)
