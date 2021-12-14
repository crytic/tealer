from tealer.teal.instructions.app_params_field import (
    AppParamsField,
    AppApprovalProgram,
    AppClearStateProgram,
    AppGlobalNumUint,
    AppGlobalNumByteSlice,
    AppLocalNumUint,
    AppLocalNumByteSlice,
    AppExtraProgramPages,
    AppCreator,
    AppAddress,
)

APP_PARAMS_FIELD_TXT_TO_OBJECT = {
    "AppParamsField": AppParamsField,
    "AppApprovalProgram": AppApprovalProgram,
    "AppClearStateProgram": AppClearStateProgram,
    "AppGlobalNumUint": AppGlobalNumUint,
    "AppGlobalNumByteSlice": AppGlobalNumByteSlice,
    "AppLocalNumUint": AppLocalNumUint,
    "AppLocalNumByteSlice": AppLocalNumByteSlice,
    "AppExtraProgramPages": AppExtraProgramPages,
    "AppCreator": AppCreator,
    "AppAddress": AppAddress,
}


def parse_app_params_field(field: str) -> AppParamsField:
    return APP_PARAMS_FIELD_TXT_TO_OBJECT[field]()
