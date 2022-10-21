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

from tealer.teal.instructions.acct_params_field import (
    AcctParamsField,
    AcctBalance,
    AcctMinBalance,
    AcctAuthAddr
)


APP_PARAMS_FIELD_TXT_TO_OBJECT = {
    "AcctBalance": AcctBalance,
    "AcctMinBalance": AcctMinBalance,
    "AcctAuthAddr": AcctAuthAddr
}


def parse_acct_params_field(field: str) -> AcctParamsField:
    """Parse fields of ``acct_params_get``.

    Args:
        field: string representation of the field.

    Returns:
        object of class corresponding to the given acct_params_get field.
    """

    return APP_PARAMS_FIELD_TXT_TO_OBJECT[field]()
