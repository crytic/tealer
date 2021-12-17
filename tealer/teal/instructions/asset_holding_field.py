# pylint: disable=too-few-public-methods
class AssetHoldingField:
    def __init__(self) -> None:
        self._version: int = 2

    @property
    def version(self) -> int:
        return self._version

    def __str__(self) -> str:
        return self.__class__.__qualname__


class AssetBalance(AssetHoldingField):
    pass


class AssetFrozen(AssetHoldingField):
    pass
