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
	AssetCreator
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
	"AssetCreator": AssetCreator
}

def parse_asset_params_field(field: str) -> AssetParamsField:
    return ASSET_PARAMS_FIELD_TXT_TO_OBJECT[field]()


