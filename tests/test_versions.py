import re
import pytest

from tealer.teal.parse_teal import parse_teal
from tealer.teal.instructions.transaction_field import TransactionField
from tealer.teal.instructions.instructions import ContractType
from tealer.teal.global_field import *


INSTRUCTIONS_TARGETS = [
    "tests/parsing/teal-instructions-with-versions.teal",
]

FIELDS_TARGETS = [
    "tests/parsing/teal-fields-with-versions.teal",
]

instruction_info_pattern = re.compile(r"\(version: ([0-9]+), mode: (Any|Stateful|Stateless)\)")

field_info_pattern = re.compile(r"\(version: ([0-9]+)\)")


@pytest.mark.parametrize("target", INSTRUCTIONS_TARGETS)  # type: ignore
def test_instruction_version(target: str) -> None:
    with open(target) as f:
        teal = parse_teal(f.read())
    for ins in teal.instructions:
        match_obj = instruction_info_pattern.search(ins.comment)
        if match_obj is None:
            continue
        version, mode_str = match_obj.groups()
        mode = {
            "Any": ContractType.ANY,
            "Stateful": ContractType.STATEFULL,
            "Stateless": ContractType.STATELESS,
        }[mode_str]
        assert ins.mode == mode
        assert ins.version == int(version)


@pytest.mark.parametrize("target", FIELDS_TARGETS)  # type: ignore
def test_field_version(target: str) -> None:
    with open(target) as f:
        teal = parse_teal(f.read())
    for ins in teal.instructions:
        field = getattr(ins, "field", None)
        if field is None:
            continue
        if isinstance(field, TransactionField):
            match_obj = field_info_pattern.search(ins.comment)
            if match_obj is None:
                continue
            version = match_obj.groups()[0]
            assert field.version == int(version)

def test_field_version_basic() -> None:
    caa = CurrentApplicationAddress()
    assert caa.version == 5
    ca = CreatorAddress()
    assert ca.version == 3
