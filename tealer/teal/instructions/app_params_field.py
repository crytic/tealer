# pylint: disable=too-few-public-methods
class AppParamsField:
    def __init__(self) -> None:
        self._version: int = 5

    @property
    def version(self) -> int:
        return self._version

    def __str__(self) -> str:
        return self.__class__.__qualname__


class AppApprovalProgram(AppParamsField):
    pass


class AppClearStateProgram(AppParamsField):
    pass


class AppGlobalNumUint(AppParamsField):
    pass


class AppGlobalNumByteSlice(AppParamsField):
    pass


class AppLocalNumUint(AppParamsField):
    pass


class AppLocalNumByteSlice(AppParamsField):
    pass


class AppExtraProgramPages(AppParamsField):
    pass


class AppCreator(AppParamsField):
    pass


class AppAddress(AppParamsField):
    pass
