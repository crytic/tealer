from tealer.teal.instructions import transaction_field

TX_FIELD_TXT_TO_OBJECT = {
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
    # "ApplicationArgs": transaction_field.ApplicationArgs,
    "NumAppArgs": transaction_field.NumAppArgs,
    # "Accounts": transaction_field.Accounts,
    "NumAccounts": transaction_field.NumAccounts,
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
}


def parse_transaction_field(tx_field: str) -> transaction_field.TransactionField:
    if tx_field.startswith("Accounts "):
        return transaction_field.Accounts(int(tx_field[len("Accounts ") :]))
    if tx_field.startswith("ApplicationArgs "):
        return transaction_field.ApplicationArgs(int(tx_field[len("ApplicationArgs ") :]))
    tx_field = tx_field.replace(" ", "")
    return TX_FIELD_TXT_TO_OBJECT[tx_field]()
