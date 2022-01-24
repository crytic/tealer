"""Parser for fields of asset_params_get.

Each ``asset_params_get`` field is represented as a class. Parsing
the field is creating the class instance representing the field given
it's string representation.

Fields of ``asset_params_get`` doesn't have immediate arguments
and have very simple structure. All fields map one-to-one with
their string representation. As a result, asset parameter fields are
parsed by first constructing a map(dict) from their string
representation to corresponding class representing the field and
using that to find the correct class for the given field.

Attributes:
    ASSET_PARAMS_FIELD_TXT_TO_OBJECT: Map(dict) from string representation
        of asset parameter field to the corresponding class.
"""

from tealer.teal.instructions.asset_params_field import (
    AssetParamsField,
    AssetTotal,
    AssetDecimals,
    AssetDefaultFrozen,
    AssetUnitName,
    AssetName,
    AssetURL,
    AssetMetadataHash,
    AssetManager,
    AssetReserve,
    AssetFreeze,
    AssetClawback,
    AssetCreator,
)

ASSET_PARAMS_FIELD_TXT_TO_OBJECT = {
    "AssetTotal": AssetTotal,
    "AssetDecimals": AssetDecimals,
    "AssetDefaultFrozen": AssetDefaultFrozen,
    "AssetUnitName": AssetUnitName,
    "AssetName": AssetName,
    "AssetURL": AssetURL,
    "AssetMetadataHash": AssetMetadataHash,
    "AssetManager": AssetManager,
    "AssetReserve": AssetReserve,
    "AssetFreeze": AssetFreeze,
    "AssetClawback": AssetClawback,
    "AssetCreator": AssetCreator,
}


def parse_asset_params_field(field: str) -> AssetParamsField:
    """Parse fields of ``asset_params_get``.

    Args:
        field: string representation of the field.

    Returns:
        object of class corresponding to the given asset_params_get field.
    """

    return ASSET_PARAMS_FIELD_TXT_TO_OBJECT[field]()
