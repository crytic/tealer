# pylint: disable=too-few-public-methods
class GlobalField:
    def __str__(self) -> str:
        return self.__class__.__qualname__


class GroupSize(GlobalField):
    pass


class MinTxnFee(GlobalField):
    pass


class ZeroAddress(GlobalField):
    pass


class MinBalance(GlobalField):
    pass


class MaxTxnLife(GlobalField):
    pass


class LogicSigVersion(GlobalField):
    pass


class Round(GlobalField):
    pass


class LatestTimestamp(GlobalField):
    pass


class CurrentApplicationID(GlobalField):
    pass


class CreatorAddress(GlobalField):
    pass


class CurrentApplicationAddress(GlobalField):
    pass


class GroupID(GlobalField):
    pass
