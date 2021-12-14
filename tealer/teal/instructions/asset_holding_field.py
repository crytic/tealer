# pylint: disable=too-few-public-methods
class AssetHoldingField:
    def __str__(self) -> str:
        return self.__class__.__qualname__


class AssetBalance(AssetHoldingField):
    pass


class AssetFrozen(AssetHoldingField):
    pass
