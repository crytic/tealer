# pylint: disable=too-few-public-methods
class AssetHoldingField:
    """Base class to represent asset holding field."""

    def __init__(self) -> None:
        self._version: int = 2

    @property
    def version(self) -> int:
        return self._version

    def __str__(self) -> str:
        return self.__class__.__qualname__


class AssetBalance(AssetHoldingField):
    """Amount of the asset unit held by this account."""


class AssetFrozen(AssetHoldingField):
    """Is asset frozen for this account or not."""
