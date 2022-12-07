"""Parser for global fields.

Each ``global`` field is represented as a class. Parsing
the field is creating the class instance representing the field given
it's string representation.

Fields of ``global`` doesn't have immediate arguments
and have very simple structure. All fields map one-to-one with
their string representation. As a result, global fields are
parsed by first constructing a map(dict) from their string
representation to corresponding class representing the field and
using that to find the correct class for the given field.

Attributes:
    GLOBAL_FIELD_TXT_TO_OBJECT: Map(dict) from string representation
        of global field to the corresponding class.
"""

from tealer.teal.global_field import (
    GroupSize,
    ZeroAddress,
    MinTxnFee,
    GlobalField,
    MinBalance,
    MaxTxnLife,
    LogicSigVersion,
    Round,
    LatestTimestamp,
    CurrentApplicationID,
    CreatorAddress,
    CurrentApplicationAddress,
    GroupID,
    OpcodeBudget,
    CallerApplicationID,
    CallerApplicationAddress,
)

GLOBAL_FIELD_TXT_TO_OBJECT = {
    "GroupSize": GroupSize,
    "MinTxnFee": MinTxnFee,
    "ZeroAddress": ZeroAddress,
    "MinBalance": MinBalance,
    "MaxTxnLife": MaxTxnLife,
    "LogicSigVersion": LogicSigVersion,
    "Round": Round,
    "LatestTimestamp": LatestTimestamp,
    "CurrentApplicationID": CurrentApplicationID,
    "CreatorAddress": CreatorAddress,
    "CurrentApplicationAddress": CurrentApplicationAddress,
    "GroupID": GroupID,
    "OpcodeBudget": OpcodeBudget,
    "CallerApplicationID": CallerApplicationID,
    "CallerApplicationAddress": CallerApplicationAddress,
}


def parse_global_field(field: str) -> GlobalField:
    """Parse global fields.

    Args:
        field: string representation of the field.

    Returns:
        object of class corresponding to the given global field.
    """

    return GLOBAL_FIELD_TXT_TO_OBJECT[field]()
