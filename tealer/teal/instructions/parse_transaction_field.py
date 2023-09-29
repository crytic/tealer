"""Parser for transaction fields.

Each transaction field is represented as a class. Parsing the field
is creating the class instance representing the field given it's
string representation.

Most of the transaction fields doesn't have immediate arguments
and their string representation consists of single sequence of characters.
Few transaction fields are arrays and have single immediate argument
which is the index into the array. Array Transaction fields with single immediate
argument are parsed using ARRAY_TX_FIELD_TO_OBJECT. For other fields,
TX_FIELD_TXT_TO_OJECT is used as lookup.

Attributes:
    TX_FIELD_TXT_TO_OBJECT: Map(dict) from string representation
        of transaction field to the corresponding class.
    ARRAY_TX_FIELD_TXT_TO_OBJECT: Map(dict) from string representation
        of array transaction field to the corresponding class.
"""
from typing import Dict, Type
from tealer.teal.instructions import transaction_field

TX_FIELD_TXT_TO_OBJECT: Dict[str, Type[transaction_field.TransactionField]] = {
    "Sender": transaction_field.Sender,
    "Fee": transaction_field.Fee,
    "FirstValid": transaction_field.FirstValid,
    "FirstValidTime": transaction_field.FirstValidTime,
    "LastValid": transaction_field.LastValid,
    "Note": transaction_field.Note,
    "Lease": transaction_field.Lease,
    "Receiver": transaction_field.Receiver,
    "Amount": transaction_field.Amount,
    "CloseRemainderTo": transaction_field.CloseRemainderTo,
    "VotePK": transaction_field.VotePK,
    "SelectionPK": transaction_field.SelectionPK,
    "VoteFirst": transaction_field.VoteFirst,
    "VoteLast": transaction_field.VoteLast,
    "VoteKeyDilution": transaction_field.VoteKeyDilution,
    "Type": transaction_field.Type,
    "TypeEnum": transaction_field.TypeEnum,
    "XferAsset": transaction_field.XferAsset,
    "AssetAmount": transaction_field.AssetAmount,
    "AssetSender": transaction_field.AssetSender,
    "AssetReceiver": transaction_field.AssetReceiver,
    "AssetCloseTo": transaction_field.AssetCloseTo,
    "GroupIndex": transaction_field.GroupIndex,
    "TxID": transaction_field.TxID,
    "ApplicationID": transaction_field.ApplicationID,
    "OnCompletion": transaction_field.OnCompletion,
    "NumAppArgs": transaction_field.NumAppArgs,
    "NumAccounts": transaction_field.NumAccounts,
    "NumApplications": transaction_field.NumApplications,
    "NumAssets": transaction_field.NumAssets,
    "ApprovalProgram": transaction_field.ApprovalProgram,
    "ClearStateProgram": transaction_field.ClearStateProgram,
    "RekeyTo": transaction_field.RekeyTo,
    "ConfigAsset": transaction_field.ConfigAsset,
    "ConfigAssetTotal": transaction_field.ConfigAssetTotal,
    "ConfigAssetDecimals": transaction_field.ConfigAssetDecimals,
    "ConfigAssetDefaultFrozen": transaction_field.ConfigAssetDefaultFrozen,
    "ConfigAssetUnitName": transaction_field.ConfigAssetUnitName,
    "ConfigAssetName": transaction_field.ConfigAssetName,
    "ConfigAssetURL": transaction_field.ConfigAssetURL,
    "ConfigAssetMetadataHash": transaction_field.ConfigAssetMetadataHash,
    "ConfigAssetManager": transaction_field.ConfigAssetManager,
    "ConfigAssetReserve": transaction_field.ConfigAssetReserve,
    "ConfigAssetFreeze": transaction_field.ConfigAssetFreeze,
    "ConfigAssetClawback": transaction_field.ConfigAssetClawback,
    "FreezeAsset": transaction_field.FreezeAsset,
    "FreezeAssetAccount": transaction_field.FreezeAssetAccount,
    "FreezeAssetFrozen": transaction_field.FreezeAssetFrozen,
    "GlobalNumUint": transaction_field.GlobalNumUint,
    "GlobalNumByteSlice": transaction_field.GlobalNumByteSlice,
    "LocalNumUint": transaction_field.LocalNumUint,
    "LocalNumByteSlice": transaction_field.LocalNumByteSlice,
    "ExtraProgramPages": transaction_field.ExtraProgramPages,
    "Nonparticipation": transaction_field.Nonparticipation,
    "NumLogs": transaction_field.NumLogs,
    "CreatedAssetID": transaction_field.CreatedAssetID,
    "CreatedApplicationID": transaction_field.CreatedApplicationID,
    "LastLog": transaction_field.LastLog,
    "StateProofPK": transaction_field.StateProofPK,
    "NumApprovalProgramPages": transaction_field.NumApprovalProgramPages,
    "NumClearStateProgramPages": transaction_field.NumClearStateProgramPages,
}


ARRAY_TX_FIELD_TO_OBJECT = {
    "Accounts": transaction_field.Accounts,
    "ApplicationArgs": transaction_field.ApplicationArgs,
    "Applications": transaction_field.Applications,
    "Assets": transaction_field.Assets,
    "Logs": transaction_field.Logs,
    "ApprovalProgramPages": transaction_field.ApprovalProgramPages,
    "ClearStateProgramPages": transaction_field.ClearStateProgramPages,
}


def _parse_int(x: str) -> int:
    """Parse teal integers.

    Teal supports three formats to write integers, hex, octal and
    decimal. hexadecimal numbers start with the prefix 0x and octal
    numbers have prefix 0.

    Args:
        x: string representation of the teal integer.

    Returns:
        python integer equal to the value represented by the given
        teal integer.
    """

    if x.startswith("0x"):
        return int(x[2:], 16)
    if x.startswith("0"):
        return int(x, 8)
    return int(x)


def parse_transaction_field(tx_field: str, use_stack: bool) -> transaction_field.TransactionField:
    """Parse transaction fields.

    Args:
        tx_field: string representation of the field.
        use_stack: boolean representing whether the array transaction field
            takes it's index from stack instead of as immediate argument.

    Returns:
        object of class corresponding to the given transaction field.
    """
    # parse array transaction fields
    for field, obj in ARRAY_TX_FIELD_TO_OBJECT.items():
        if tx_field.startswith(field):
            index = -1 if use_stack else _parse_int(tx_field[len(field) + 1 :])  # +1 for space(" ")
            return obj(index)

    tx_field = tx_field.replace(" ", "")
    return TX_FIELD_TXT_TO_OBJECT[tx_field]()
