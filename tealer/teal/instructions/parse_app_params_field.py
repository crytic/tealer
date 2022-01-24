"""Parser for fields of app_params_get.

Each ``app_params_get`` field is represented as a class. Parsing
the field is creating the class instance representing the field given
it's string representation.

Fields of ``app_params_get`` doesn't have immediate arguments
and have very simple structure. All fields map one-to-one with
their string representation. As a result, app parameter fields are
parsed by first constructing a map(dict) from their string
representation to corresponding class representing the field and
using that to find the correct class for the given field.

Attributes:
    APP_PARAMS_FIELD_TXT_TO_OBJECT: Map(dict) from string representation
        of app parameter field to the corresponding class.
"""

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
    """Parse fields of ``app_params_get``.

    Args:
        field: string representation of the field.

    Returns:
        object of class corresponding to the given app_params_get field.
    """

    return APP_PARAMS_FIELD_TXT_TO_OBJECT[field]()
