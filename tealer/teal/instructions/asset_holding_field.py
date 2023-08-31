"""Defines classes to represent asset_holding_get fields.

``asset_holding_get`` instruction is used to access holding fields
of an asset for the given account.

Each field that can be accessed using asset_holding_get is represented
by a class in tealer. All the classes representing the fields must inherit
from AssetHoldingField class.

"""

# pylint: disable=too-few-public-methods
class AssetHoldingField:
    """Base class to represent asset_holding_get field."""

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


class AssetBalance(AssetHoldingField):
    """Amount of the asset unit held by this account."""


class AssetFrozen(AssetHoldingField):
    """Is asset frozen for this account or not."""
