# pylint: disable=too-few-public-methods
class AppParamsField:
    pass


class AppApprovalProgram(AppParamsField):
    def __str__(self):
        return "AppApprovalProgram"


class AppClearStateProgram(AppParamsField):
    def __str__(self):
        return "AppClearStateProgram"


class AppGlobalNumUint(AppParamsField):
    def __str__(self):
        return "AppGlobalNumUint"


class AppGlobalNumByteSlice(AppParamsField):
    def __str__(self):
        return "AppGlobalNumByteSlice"


class AppLocalNumUint(AppParamsField):
    def __str__(self):
        return "AppLocalNumUint"


class AppLocalNumByteSlice(AppParamsField):
    def __str__(self):
        return "AppLocalNumByteSlice"


class AppExtraProgramPages(AppParamsField):
    def __str__(self):
        return "AppExtraProgramPages"


class AppCreator(AppParamsField):
    def __str__(self):
        return "AppCreator"


class AppAddress(AppParamsField):
    def __str__(self):
        return "AppAddress"
