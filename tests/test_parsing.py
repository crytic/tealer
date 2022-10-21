from ast import parse
from typing import Type, Tuple
import pytest

from tealer.teal.parse_teal import parse_teal
from tealer.teal.instructions.parse_instruction import parse_line, ParseError
from tealer.teal.instructions import instructions

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
    "tests/parsing/teal-instructions-with-versions.teal",
    "tests/parsing/teal-fields-with-versions.teal",
    "tests/parsing/multiple_retsub.teal",
    "tests/parsing/subroutine_jump_back.teal",
    "tests/parsing/teal6-acct_params_get.teal",
    "tests/parsing/teal6-instructions.teal",    
]

TEST_CODE = """
intcblock 0xf 017 15
intcblock
int pay
byte base64 AA
byte b64 AA
byte base64(AA)
byte b64(AA)
byte base32 AA
byte b32 AA
byte base32(AA)
byte b32(AA)
byte 0x0123456789abcdef
byte "\x01\x02"
byte "string literal"
bytecblock b32(AA) base64 AA 0x00 "00"
bytecblock
byte "not label: // not comment either"
labelwithqoute": // valid
"""

invalid_instructions = """
byte "sdf       // missing closing qoute
byte base64     // missing encoded string
byte b64        // missing encoded string
byte base32     // missing encoded string
byte b32        // missing encoded string
byte base64(AA  // missing closing paranthesis
byte b64(AA     // missing closing paranthesis
byte base32(AA  // missing closing paranthesis
byte b32(AA     // missing closing paranthesis
label: add      // contains additional token add
byte "1" "2"    // byte expects only one immediate arg.
byte sdf        // incorrect byte format
"""

unsupported_instructions = """
not an instruction
"""

@pytest.mark.parametrize("target", TARGETS)  # type: ignore
def test_parsing(target: str) -> None:
    with open(target, encoding="utf-8") as f:
        teal = parse_teal(f.read())
    # print instruction to trigger __str__ on each ins
    for i in teal.instructions:
        assert not isinstance(i, instructions.UnsupportedInstruction) , f'ins "{i}" is not supported'
        print(i, i.cost)


def _cmp_instructions(
    b1: instructions.Instruction,
    b2: instructions.Instruction,
    target: Type[instructions.Instruction],
    attributes: Tuple[str],
) -> bool:
    check = isinstance(b1, target) and isinstance(b2, target)
    if not check:
        return check

    for attr in attributes:
        v1 = getattr(b1, attr, None)
        v2 = getattr(b2, attr, None)
        if v1 != v2:
            return False
    return True


def test_parsing_2() -> None:
    teal = parse_teal(TEST_CODE)
    ins1 = teal.instructions
    ins2 = [
        instructions.Intcblock([15, 15, 15]),
        instructions.Intcblock([]),
        instructions.Int("pay"),
        instructions.Byte("0x00"),
        instructions.Byte("0x00"),
        instructions.Byte("0x00"),
        instructions.Byte("0x00"),
        instructions.Byte("0x00"),
        instructions.Byte("0x00"),
        instructions.Byte("0x00"),
        instructions.Byte("0x00"),
        instructions.Byte("0x0123456789abcdef"),
        instructions.Byte('"\x01\x02"'),
        instructions.Byte('"string literal"'),
        instructions.Bytecblock(["0x00", "0x00", "0x00", '"00"']),
        instructions.Bytecblock([]),
        instructions.Byte('"not label: // not comment either"'),
        instructions.Label('labelwithqoute"'),
    ]
    t = [
        (instructions.Intcblock, ("_constants",)),
        (instructions.Intcblock, ("_constants",)),
        (instructions.Int, ("value",)),
        (instructions.Byte, ("_bytes",)),
        (instructions.Byte, ("_bytes",)),
        (instructions.Byte, ("_bytes",)),
        (instructions.Byte, ("_bytes",)),
        (instructions.Byte, ("_bytes",)),
        (instructions.Byte, ("_bytes",)),
        (instructions.Byte, ("_bytes",)),
        (instructions.Byte, ("_bytes",)),
        (instructions.Byte, ("_bytes",)),
        (instructions.Byte, ("_bytes",)),
        (instructions.Byte, ("_bytes",)),
        (instructions.Bytecblock, ("_constants",)),
        (instructions.Bytecblock, ("_constants",)),
        (instructions.Byte, ("_bytes",)),
        (instructions.Label, ("label",)),
    ]

    for (b1, b2, (target, attributes)) in zip(ins1, ins2, t):
        assert _cmp_instructions(b1, b2, target, attributes)


def test_invalid_instructions() -> None:
    for line in invalid_instructions.strip().splitlines():
        with pytest.raises(ParseError):
            parse_line(line)


def test_unsupported_instructions() -> None:
    for line in unsupported_instructions.strip().splitlines():
        ins = parse_line(line)
        assert isinstance(ins, instructions.UnsupportedInstruction)

def test_field_properties() -> None:
    ins = parse_line("gitxnas 1 ApplicationArgs")
    assert isinstance(ins, instructions.Gitxnas) and ins.idx == 1

    ins = parse_line("gitxna 1 ApplicationArgs 0")
    assert isinstance(ins, instructions.Gitxna) and ins.idx == 1
