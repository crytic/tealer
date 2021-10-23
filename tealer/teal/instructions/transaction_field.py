# pylint: disable=too-few-public-methods

# https://developer.algorand.org/docs/reference/teal/opcodes/#txn


class TransactionField:
    pass


class Sender(TransactionField):
    def __str__(self):
        return "Sender"


class Fee(TransactionField):
    def __str__(self):
        return "Fee"


class FirstValid(TransactionField):
    def __str__(self):
        return "FirstValid"


class FirstValidTime(TransactionField):
    def __str__(self):
        return "FirstValidTime"


class LastValid(TransactionField):
    def __str__(self):
        return "LastValid"


class Note(TransactionField):
    def __str__(self):
        return "Note"


class Lease(TransactionField):
    def __str__(self):
        return "Lease"


class Receiver(TransactionField):
    def __str__(self):
        return "Receiver"


class Amount(TransactionField):
    def __str__(self):
        return "Amount"


class CloseRemainderTo(TransactionField):
    def __str__(self):
        return "CloseRemainderTo"


class VotePK(TransactionField):
    def __str__(self):
        return "VotePK"


class SelectionPK(TransactionField):
    def __str__(self):
        return "SelectionPK"


class VoteFirst(TransactionField):
    def __str__(self):
        return "VoteFirst"


class VoteLast(TransactionField):
    def __str__(self):
        return "VoteLast"


class VoteKeyDilution(TransactionField):
    def __str__(self):
        return "VoteKeyDilution"


class Type(TransactionField):
    def __str__(self):
        return "Type"


class TypeEnum(TransactionField):
    def __str__(self):
        return "TypeEnum"


class XferAsset(TransactionField):
    def __str__(self):
        return "XferAsset"


class AssetAmount(TransactionField):
    def __str__(self):
        return "AssetAmount"


class AssetSender(TransactionField):
    def __str__(self):
        return "AssetSender"


class AssetReceiver(TransactionField):
    def __str__(self):
        return "AssetReceiver"


class AssetCloseTo(TransactionField):
    def __str__(self):
        return "AssetCloseTo"


class GroupIndex(TransactionField):
    def __str__(self):
        return "GroupIndex"


class TxID(TransactionField):
    def __str__(self):
        return "TxID"


class ApplicationID(TransactionField):
    def __str__(self):
        return "ApplicationID"


class OnCompletion(TransactionField):
    def __str__(self):
        return "OnCompletion"


class ApplicationArgs(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self):
        return f"ApplicationArgs {self._idx}"


class NumAppArgs(TransactionField):
    def __str__(self):
        return "NumAppArgs"


class Accounts(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self):
        return f"Accounts {self._idx}"


class NumAccounts(TransactionField):
    def __str__(self):
        return "NumAccounts"


class Applications(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self):
        return f"Applications {self._idx}"


class NumApplications(TransactionField):
    def __str__(self):
        return "NumApplications"


class Assets(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self):
        return f"Assets {self._idx}"


class NumAssets(TransactionField):
    def __str__(self):
        return "NumAssets"


class ApprovalProgram(TransactionField):
    def __str__(self):
        return "ApprovalProgram"


class ClearStateProgram(TransactionField):
    def __str__(self):
        return "ClearStateProgram"


class RekeyTo(TransactionField):
    def __str__(self):
        return "RekeyTo"


class ConfigAsset(TransactionField):
    def __str__(self):
        return "ConfigAsset"


class ConfigAssetTotal(TransactionField):
    def __str__(self):
        return "ConfigAssetTotal"


class ConfigAssetDecimals(TransactionField):
    def __str__(self):
        return "ConfigAssetDecimals"


class ConfigAssetDefaultFrozen(TransactionField):
    def __str__(self):
        return "ConfigAssetDefaultFrozen"


class ConfigAssetUnitName(TransactionField):
    def __str__(self):
        return "ConfigAssetUnitName"


class ConfigAssetName(TransactionField):
    def __str__(self):
        return "ConfigAssetName"


class ConfigAssetURL(TransactionField):
    def __str__(self):
        return "ConfigAssetURL"


class ConfigAssetMetadataHash(TransactionField):
    def __str__(self):
        return "ConfigAssetMetadataHash"


class ConfigAssetManager(TransactionField):
    def __str__(self):
        return "ConfigAssetManager"


class ConfigAssetReserve(TransactionField):
    def __str__(self):
        return "ConfigAssetReserve"


class ConfigAssetFreeze(TransactionField):
    def __str__(self):
        return "ConfigAssetFreeze"


class ConfigAssetClawback(TransactionField):
    def __str__(self):
        return "ConfigAssetClawback"


class FreezeAsset(TransactionField):
    def __str__(self):
        return "FreezeAsset"


class FreezeAssetAccount(TransactionField):
    def __str__(self):
        return "FreezeAssetAccount"


class FreezeAssetFrozen(TransactionField):
    def __str__(self):
        return "FreezeAssetFrozen"


class GlobalNumUint(TransactionField):
    def __str__(self):
        return "GlobalNumUint"


class GlobalNumByteSlice(TransactionField):
    def __str__(self):
        return "GlobalNumByteSlice"


class LocalNumUint(TransactionField):
    def __str__(self):
        return "LocalNumUint"


class LocalNumByteSlice(TransactionField):
    def __str__(self):
        return "LocalNumByteSlice"


class ExtraProgramPages(TransactionField):
    def __str__(self):
        return "ExtraProgramPages"


class Nonparticipation(TransactionField):
    def __str__(self):
        return "Nonparticipation"


class Logs(TransactionField):
    def __str__(self):
        return "Logs"


class NumLogs(TransactionField):
    def __str__(self):
        return "NumLogs"


class CreatedAssetID(TransactionField):
    def __str__(self):
        return "CreatedAssetID"


class CreatedApplicationID(TransactionField):
    def __str__(self):
        return "CreatedApplicationID"
