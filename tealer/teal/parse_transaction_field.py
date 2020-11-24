from tealer.teal.transaction_field import (
    ApplicationArgs,
    Accounts,
    TransactionField,
    OnCompletion,
    ApplicationID,
    AssetAmount,
    AssetCloseTo,
    Amount,
    AssetReceiver,
    CloseRemainderTo,
    Fee,
    GroupIndex,
    Receiver,
    RekeyTo,
    Sender,
    TypeEnum,
    XferAsset,
    NumAppArgs,
)

TX_FIELD_TXT_TO_OBJECT = {
    "ApplicationID": ApplicationID,
    "Amount": Amount,
    "AssetAmount": AssetAmount,
    "AssetCloseTo": AssetCloseTo,
    "AssetReceiver": AssetReceiver,
    "CloseRemainderTo": CloseRemainderTo,
    "Fee": Fee,
    "GroupIndex": GroupIndex,
    "OnCompletion": OnCompletion,
    "Receiver": Receiver,
    "RekeyTo": RekeyTo,
    "Sender": Sender,
    "TypeEnum": TypeEnum,
    "XferAsset": XferAsset,
    "NumAppArgs": NumAppArgs,
}


def parse_transaction_field(tx_field: str) -> TransactionField:
    if tx_field.startswith("Accounts "):
        return Accounts(int(tx_field[len("Accounts ") :]))
    if tx_field.startswith("ApplicationArgs "):
        return ApplicationArgs(int(tx_field[len("ApplicationArgs ") :]))
    tx_field = tx_field.replace(" ", "")
    return TX_FIELD_TXT_TO_OBJECT[tx_field]()
