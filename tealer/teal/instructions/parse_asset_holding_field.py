"""Parser for fields of asset_holding_get.

Each ``asset_holding_get`` field is represented as a class. Parsing
the field is creating the class instance representing the field given
it's string representation.

Fields of ``asset_holding_get`` doesn't have immediate arguments
and have very simple structure. All fields map one-to-one with
their string representation. As a result, asset holding fields are
parsed by first constructing a map(dict) from their string
representation to corresponding class representing the field and
using that to find the correct class for the given field.

Attributes:
    ASSET_HOLDING_FIELD_TXT_TO_OBJECT: Map(dict) from string representation
        of asset holding field to the corresponding class.
"""

from tealer.teal.instructions.asset_holding_field import (
    AssetHoldingField,
    AssetBalance,
    AssetFrozen,
)

ASSET_HOLDING_FIELD_TXT_TO_OBJECT = {"AssetBalance": AssetBalance, "AssetFrozen": AssetFrozen}


def parse_asset_holding_field(field: str) -> AssetHoldingField:
    """Parse fields of ``asset_holding_get``.

    Args:
        field: string representation of the field.

    Returns:
        object of class corresponding to the given asset_holding_get field.
    """

    return ASSET_HOLDING_FIELD_TXT_TO_OBJECT[field]()
