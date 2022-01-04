# pylint: disable=too-few-public-methods
class AssetParamsField:
    """Base class to represent asset_params_get field."""

    def __init__(self) -> None:
        self._version: int = 2

    @property
    def version(self) -> int:
        return self._version

    def __str__(self) -> str:
        return self.__class__.__qualname__


class AssetTotal(AssetParamsField):
    """Total number of units of this asset."""


class AssetDecimals(AssetParamsField):
    """Number of digits to display after the decimal place."""


class AssetDefaultFrozen(AssetParamsField):
    """Whether the asset is frozen by default or not."""


class AssetUnitName(AssetParamsField):
    """Unit name of the asset."""


class AssetName(AssetParamsField):
    """The asset name."""


class AssetURL(AssetParamsField):
    """Url associated with the asset."""


class AssetMetadataHash(AssetParamsField):
    """32 byte commitment to some unspecified asset metadata."""


class AssetManager(AssetParamsField):
    """Manager address, only account that can authorize transactions to re-configure or destroy an asset."""


class AssetReserve(AssetParamsField):
    """Reserve address, where non-minted assets will reside."""


class AssetFreeze(AssetParamsField):
    """Freeze account, which is allowed to freeze or unfreeze the asset holding for an account."""


class AssetClawback(AssetParamsField):
    """Clawback address, which can transfer assets from and to any asset holder."""


class AssetCreator(AssetParamsField):
    """Creator address of this asset."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5
