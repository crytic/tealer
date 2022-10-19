import pytest  # pylint: disable=unused-import

from tealer.teal.parse_teal import parse_teal
from tealer.teal.instructions.instructions import ContractType

STATEFULL = """
#pragma version 6
itxn_begin
int pay
itxn_field TypeEnum
itxn_submit
"""

STATELESS = """
bytes "secret"
arg_0
==
"""

ANY = """
addr 5V2KYGC366NJNMIFLQOER2RUTZGYJSDXH7CLJUCDB7DZAMCDRM3YUHF4OM
txn Sender
==
"""


def test_mode() -> None:
    teal = parse_teal(STATEFULL)
    assert teal.version == 6
    assert teal.mode == ContractType.STATEFULL

    teal = parse_teal(STATELESS)
    assert teal.version == 1
    assert teal.mode == ContractType.STATELESS

    teal = parse_teal(ANY)
    assert teal.version == 1
    assert teal.mode == ContractType.ANY
