# pylint: disable=too-few-public-methods
class GlobalField:
    pass


class GroupSize(GlobalField):
    def __str__(self):
        return "GroupSize"


class MinTxnFee(GlobalField):
    def __str__(self):
        return "MinTxnFee"


class ZeroAddress(GlobalField):
    def __str__(self):
        return "ZeroAddress"


class MinBalance(GlobalField):
    def __str__(self):
        return "MinBalance"


class MaxTxnLife(GlobalField):
    def __str__(self):
        return "MaxTxnLife"


class LogicSigVersion(GlobalField):
    def __str__(self):
        return "LogicSigVersion"


class Round(GlobalField):
    def __str__(self):
        return "Round"


class LatestTimestamp(GlobalField):
    def __str__(self):
        return "LatestTimestamp"


class CurrentApplicationID(GlobalField):
    def __str__(self):
        return "CurrentApplicationID"


class CreatorAddress(GlobalField):
    def __str__(self):
        return "CreatorAddress"


class CurrentApplicationAddress(GlobalField):
    def __str__(self):
        return "CurrentApplicationAddress"


class GroupID(GlobalField):
    def __str__(self):
        return "GroupID"
