# pylint: disable=too-few-public-methods
class AssetHoldingField:
    pass


class AssetBalance(AssetHoldingField):
    def __str__(self):
        return "AssetBalance"


class AssetFrozen(AssetHoldingField):
    def __str__(self):
        return "AssetFrozen"
