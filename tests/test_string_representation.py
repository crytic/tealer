from typing import Any, Dict
import pytest

from tealer.teal.instructions.parse_app_params_field import APP_PARAMS_FIELD_TXT_TO_OBJECT
from tealer.teal.instructions.parse_asset_holding_field import ASSET_HOLDING_FIELD_TXT_TO_OBJECT
from tealer.teal.instructions.parse_asset_params_field import ASSET_PARAMS_FIELD_TXT_TO_OBJECT
from tealer.teal.instructions.parse_global_field import GLOBAL_FIELD_TXT_TO_OBJECT
from tealer.teal.instructions.parse_transaction_field import TX_FIELD_TXT_TO_OBJECT
from tealer.teal.instructions import instructions

INSTRUCTION_TXT_TO_OBJECT = {
    "err": instructions.Err,
    "assert": instructions.Assert,
    "gaids": instructions.Gaids,
    "loads": instructions.Loads,
    "stores": instructions.Stores,
    "swap": instructions.Swap,
    "getbit": instructions.GetBit,
    "setbit": instructions.SetBit,
    "getbyte": instructions.GetByte,
    "setbyte": instructions.SetByte,
    "extract3": instructions.Extract3,
    "extract_uint16": instructions.Extract_uint16,
    "sha256": instructions.Sha256,
    "sha512_256": instructions.Sha512_256,
    "retsub": instructions.Retsub,
}

ALL_TESTS = [
    APP_PARAMS_FIELD_TXT_TO_OBJECT,
    ASSET_HOLDING_FIELD_TXT_TO_OBJECT,
    ASSET_PARAMS_FIELD_TXT_TO_OBJECT,
    GLOBAL_FIELD_TXT_TO_OBJECT,
    TX_FIELD_TXT_TO_OBJECT,
    INSTRUCTION_TXT_TO_OBJECT,
]


@pytest.mark.parametrize("test", ALL_TESTS)  # type: ignore
def test_string_repr(test: Dict[str, Any]) -> None:
    for target, obj in test.items():
        assert str(obj()) == target
