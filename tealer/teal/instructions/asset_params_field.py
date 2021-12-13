# pylint: disable=too-few-public-methods
class AssetParamsField:
    pass


class AssetTotal(AssetParamsField):
    def __str__(self) -> str:
        return "AssetTotal"


class AssetDecimals(AssetParamsField):
    def __str__(self) -> str:
        return "AssetDecimals"


class AssetDefaultFrozen(AssetParamsField):
    def __str__(self) -> str:
        return "AssetDefaultFrozen"


class AssetUnitName(AssetParamsField):
    def __str__(self) -> str:
        return "AssetUnitName"


class AssetName(AssetParamsField):
    def __str__(self) -> str:
        return "AssetName"


class AssetURL(AssetParamsField):
    def __str__(self) -> str:
        return "AssetURL"


class AssetMetadataHash(AssetParamsField):
    def __str__(self) -> str:
        return "AssetMetadataHash"


class AssetManager(AssetParamsField):
    def __str__(self) -> str:
        return "AssetManager"


class AssetReserve(AssetParamsField):
    def __str__(self) -> str:
        return "AssetReserve"


class AssetFreeze(AssetParamsField):
    def __str__(self) -> str:
        return "AssetFreeze"


class AssetClawback(AssetParamsField):
    def __str__(self) -> str:
        return "AssetClawback"


class AssetCreator(AssetParamsField):
    def __str__(self) -> str:
        return "AssetCreator"
