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
    GroupID
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
    "GroupID" : GroupID
}


def parse_global_field(field: str) -> GlobalField:
    return GLOBAL_FIELD_TXT_TO_OBJECT[field]()
