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
        """Teal version this field is introduced in and supported from."""
        return self._version

    def type(self) -> str:
        ...

    def __str__(self) -> str:
        return self.__class__.__qualname__

    def to_dict(self):
        pass


class AssetTotal(AssetParamsField):
    """Total number of units of this asset."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "AssetTotal", "type": self.type}


class AssetDecimals(AssetParamsField):
    """Number of digits to display after the decimal place."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "AssetDecimal", "type": self.type}


class AssetDefaultFrozen(AssetParamsField):
    """Whether the asset is frozen by default or not."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "AssetDefaultFrozen", "type": self.type}


class AssetUnitName(AssetParamsField):
    """Unit name of the asset."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AssetUnitName", "type": self.type}


class AssetName(AssetParamsField):
    """The asset name."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AssetName", "type": self.type}


class AssetURL(AssetParamsField):
    """Url associated with the asset."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AssetURL", "type": self.type}


class AssetMetadataHash(AssetParamsField):
    """32 byte commitment to some unspecified asset metadata."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AssetMetadataHash", "type": self.type}


class AssetManager(AssetParamsField):
    """Manager address of the asset.

    Manager account is the only account that can authorize transactions
    to re-configure or destroy an asset.
    """

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AssetManager", "type": self.type}


class AssetReserve(AssetParamsField):
    """Reserve address of the asset.

    Non-minted assets will reside in Reserve address instead of creator
    address if specified.
    """

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AssetReserve", "type": self.type}


class AssetFreeze(AssetParamsField):
    """Freeze address of the asset.

    The freeze account is allowed to freeze or unfreeze the asset holdings
    for a specific account.
    """

    def to_dict(self):
        return {"name": "AssetFreeze", "type": self.type}


class AssetClawback(AssetParamsField):
    """Clawback address of the asset.

    The clawback address represents an account that is allowed to transfer
    assets from and to any asset holder.
    """

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AssetClawback", "type": self.type}


class AssetCreator(AssetParamsField):
    """Creator address of this asset."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5

    def to_dict(self):
        return {"name": "AssetCreator", "type": self.type}
