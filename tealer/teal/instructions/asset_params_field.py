# pylint: disable=too-few-public-methods
class AssetParamsField:
    def __init__(self) -> None:
        self._version: int = 2

    @property
    def version(self) -> int:
        return self._version

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
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5
