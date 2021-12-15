# pylint: disable=too-few-public-methods
class AssetParamsField:
    def __str__(self) -> str:
        return self.__class__.__qualname__


class AssetTotal(AssetParamsField):
    pass


class AssetDecimals(AssetParamsField):
    pass


class AssetDefaultFrozen(AssetParamsField):
    pass


class AssetUnitName(AssetParamsField):
    pass


class AssetName(AssetParamsField):
    pass


class AssetURL(AssetParamsField):
    pass


class AssetMetadataHash(AssetParamsField):
    pass


class AssetManager(AssetParamsField):
    pass


class AssetReserve(AssetParamsField):
    pass


class AssetFreeze(AssetParamsField):
    pass


class AssetClawback(AssetParamsField):
    pass


class AssetCreator(AssetParamsField):
    pass
