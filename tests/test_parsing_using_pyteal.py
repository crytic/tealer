# type: ignore[unreachable]
import sys
import pytest

from tealer.teal.instructions import instructions
from tealer.teal.parse_teal import parse_teal

if not sys.version_info >= (3, 10):
    pytest.skip(reason="PyTeal based tests require python >= 3.10", allow_module_level=True)

# pylint: disable=wrong-import-position
# Place import statements after the version check
from tests.pyteal_parsing.normal_application import normal_application_approval_program
from tests.pyteal_parsing.arc4_application import arc4_application_ap
from tests.pyteal_parsing.control_flow_constructs import control_flow_ap


TARGETS = [
    normal_application_approval_program,
    arc4_application_ap,
    control_flow_ap,
]


@pytest.mark.parametrize("target", TARGETS)  # type: ignore
def test_parsing_using_pyteal(target: str) -> None:
    teal = parse_teal(target)
    # print instruction to trigger __str__ on each ins
    # print stack pop/push to trigger the function on each ins
    for i in teal.instructions:
        assert not isinstance(i, instructions.UnsupportedInstruction), f'ins "{i}" is not supported'
        print(i, i.cost)
        print(i, i.stack_pop_size)
        print(i, i.stack_push_size)
