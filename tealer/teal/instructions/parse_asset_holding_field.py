from tealer.teal.instructions.asset_holding_field import (
    AssetHoldingField,
    AssetBalance,
    AssetFrozen,
)

ASSET_HOLDING_FIELD_TXT_TO_OBJECT = {"AssetBalance": AssetBalance, "AssetFrozen": AssetFrozen}


def parse_asset_holding_field(field: str) -> AssetHoldingField:
    return ASSET_HOLDING_FIELD_TXT_TO_OBJECT[field]()
