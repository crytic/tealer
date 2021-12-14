# pylint: disable=too-few-public-methods
class GlobalField:
    pass


class GroupSize(GlobalField):
    def __str__(self) -> str:
        return "GroupSize"


class MinTxnFee(GlobalField):
    def __str__(self) -> str:
        return "MinTxnFee"


class ZeroAddress(GlobalField):
    def __str__(self) -> str:
        return "ZeroAddress"


class MinBalance(GlobalField):
    def __str__(self) -> str:
        return "MinBalance"


class MaxTxnLife(GlobalField):
    def __str__(self) -> str:
        return "MaxTxnLife"


class LogicSigVersion(GlobalField):
    def __str__(self) -> str:
        return "LogicSigVersion"


class Round(GlobalField):
    def __str__(self) -> str:
        return "Round"


class LatestTimestamp(GlobalField):
    def __str__(self) -> str:
        return "LatestTimestamp"


class CurrentApplicationID(GlobalField):
    def __str__(self) -> str:
        return "CurrentApplicationID"


class CreatorAddress(GlobalField):
    def __str__(self) -> str:
        return "CreatorAddress"


class CurrentApplicationAddress(GlobalField):
    def __str__(self) -> str:
        return "CurrentApplicationAddress"


class GroupID(GlobalField):
    def __str__(self) -> str:
        return "GroupID"
