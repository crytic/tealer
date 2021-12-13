# pylint: disable=too-few-public-methods
class AssetHoldingField:
    pass


class AssetBalance(AssetHoldingField):
    def __str__(self) -> str:
        return "AssetBalance"


class AssetFrozen(AssetHoldingField):
    def __str__(self) -> str:
        return "AssetFrozen"
