# pylint: disable=too-few-public-methods
class AssetParamsField:
    pass


class AssetTotal(AssetParamsField):
    def __str__(self):
        return "AssetTotal"


class AssetDecimals(AssetParamsField):
    def __str__(self):
        return "AssetDecimals"


class AssetDefaultFrozen(AssetParamsField):
    def __str__(self):
        return "AssetDefaultFrozen"


class AssetUnitName(AssetParamsField):
    def __str__(self):
        return "AssetUnitName"


class AssetName(AssetParamsField):
    def __str__(self):
        return "AssetName"


class AssetURL(AssetParamsField):
    def __str__(self):
        return "AssetURL"


class AssetMetadataHash(AssetParamsField):
    def __str__(self):
        return "AssetMetadataHash"


class AssetManager(AssetParamsField):
    def __str__(self):
        return "AssetManager"


class AssetReserve(AssetParamsField):
    def __str__(self):
        return "AssetReserve"


class AssetFreeze(AssetParamsField):
    def __str__(self):
        return "AssetFreeze"


class AssetClawback(AssetParamsField):
    def __str__(self):
        return "AssetClawback"


class AssetCreator(AssetParamsField):
    def __str__(self):
        return "AssetCreator"
