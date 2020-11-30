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
}


def parse_global_field(field: str) -> GlobalField:
    return GLOBAL_FIELD_TXT_TO_OBJECT[field]()
