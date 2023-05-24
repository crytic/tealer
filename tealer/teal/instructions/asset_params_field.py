"""Defines classes to represent asset_params_get fields.

``asset_params_get`` instruction is used to access parameter fields
of an asset.

Each field that can be accessed using asset_params_get is represented
by a class in tealer. All the classes representing the fields must inherit
from AssetParamsField class.

"""

# pylint: disable=too-few-public-methods
class AssetParamsField:
    """Base class to represent asset_params_get field."""

    def __init__(self) -> None:
        self._version: int = 2

    @property
    def version(self) -> int:
        """Teal version this field is introduced in and supported from.

        Returns:
            Teal version the field is introduced in and supported from.
        """
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
    """Manager address of the asset.

    Manager account is the only account that can authorize transactions
    to re-configure or destroy an asset.
    """


class AssetReserve(AssetParamsField):
    """Reserve address of the asset.

    Non-minted assets will reside in Reserve address instead of creator
    address if specified.
    """


class AssetFreeze(AssetParamsField):
    """Freeze address of the asset.

    The freeze account is allowed to freeze or unfreeze the asset holdings
    for a specific account.
    """


class AssetClawback(AssetParamsField):
    """Clawback address of the asset.

    The clawback address represents an account that is allowed to transfer
    assets from and to any asset holder.
    """


class AssetCreator(AssetParamsField):
    """Creator address of this asset."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5
