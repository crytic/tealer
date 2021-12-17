# pylint: disable=too-few-public-methods
class GlobalField:
    def __init__(self) -> None:
        self._version: int = 1

    @property
    def version(self) -> int:
        return self._version

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
    def __init__(self) -> None:
        super().__init__()
        self._version = 2


class Round(GlobalField):
    def __init__(self) -> None:
        super().__init__()
        self._version = 2


class LatestTimestamp(GlobalField):
    def __init__(self) -> None:
        super().__init__()
        self._version = 2


class CurrentApplicationID(GlobalField):
    def __init__(self) -> None:
        super().__init__()
        self._version = 2


class CreatorAddress(GlobalField):
    def __init__(self) -> None:
        super().__init__()
        self._version = 3


class CurrentApplicationAddress(GlobalField):
    def __init__(self) -> None:
        super().__init__()
        self._version = 5


class GroupID(GlobalField):
    def __init__(self) -> None:
        super().__init__()
        self._version = 5
