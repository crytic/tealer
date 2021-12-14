# pylint: disable=too-few-public-methods
class AppParamsField:
    pass


class AppApprovalProgram(AppParamsField):
    def __str__(self) -> str:
        return "AppApprovalProgram"


class AppClearStateProgram(AppParamsField):
    def __str__(self) -> str:
        return "AppClearStateProgram"


class AppGlobalNumUint(AppParamsField):
    def __str__(self) -> str:
        return "AppGlobalNumUint"


class AppGlobalNumByteSlice(AppParamsField):
    def __str__(self) -> str:
        return "AppGlobalNumByteSlice"


class AppLocalNumUint(AppParamsField):
    def __str__(self) -> str:
        return "AppLocalNumUint"


class AppLocalNumByteSlice(AppParamsField):
    def __str__(self) -> str:
        return "AppLocalNumByteSlice"


class AppExtraProgramPages(AppParamsField):
    def __str__(self) -> str:
        return "AppExtraProgramPages"


class AppCreator(AppParamsField):
    def __str__(self) -> str:
        return "AppCreator"


class AppAddress(AppParamsField):
    def __str__(self) -> str:
        return "AppAddress"
