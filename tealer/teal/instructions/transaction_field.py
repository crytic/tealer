# pylint: disable=too-few-public-methods

# https://developer.algorand.org/docs/reference/teal/opcodes/#txn


class TransactionField:
    pass


class Sender(TransactionField):
    def __str__(self) -> str:
        return "Sender"


class Fee(TransactionField):
    def __str__(self) -> str:
        return "Fee"


class FirstValid(TransactionField):
    def __str__(self) -> str:
        return "FirstValid"


class FirstValidTime(TransactionField):
    def __str__(self) -> str:
        return "FirstValidTime"


class LastValid(TransactionField):
    def __str__(self) -> str:
        return "LastValid"


class Note(TransactionField):
    def __str__(self) -> str:
        return "Note"


class Lease(TransactionField):
    def __str__(self) -> str:
        return "Lease"


class Receiver(TransactionField):
    def __str__(self) -> str:
        return "Receiver"


class Amount(TransactionField):
    def __str__(self) -> str:
        return "Amount"


class CloseRemainderTo(TransactionField):
    def __str__(self) -> str:
        return "CloseRemainderTo"


class VotePK(TransactionField):
    def __str__(self) -> str:
        return "VotePK"


class SelectionPK(TransactionField):
    def __str__(self) -> str:
        return "SelectionPK"


class VoteFirst(TransactionField):
    def __str__(self) -> str:
        return "VoteFirst"


class VoteLast(TransactionField):
    def __str__(self) -> str:
        return "VoteLast"


class VoteKeyDilution(TransactionField):
    def __str__(self) -> str:
        return "VoteKeyDilution"


class Type(TransactionField):
    def __str__(self) -> str:
        return "Type"


class TypeEnum(TransactionField):
    def __str__(self) -> str:
        return "TypeEnum"


class XferAsset(TransactionField):
    def __str__(self) -> str:
        return "XferAsset"


class AssetAmount(TransactionField):
    def __str__(self) -> str:
        return "AssetAmount"


class AssetSender(TransactionField):
    def __str__(self) -> str:
        return "AssetSender"


class AssetReceiver(TransactionField):
    def __str__(self) -> str:
        return "AssetReceiver"


class AssetCloseTo(TransactionField):
    def __str__(self) -> str:
        return "AssetCloseTo"


class GroupIndex(TransactionField):
    def __str__(self) -> str:
        return "GroupIndex"


class TxID(TransactionField):
    def __str__(self) -> str:
        return "TxID"


class ApplicationID(TransactionField):
    def __str__(self) -> str:
        return "ApplicationID"


class OnCompletion(TransactionField):
    def __str__(self) -> str:
        return "OnCompletion"


class ApplicationArgs(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "ApplicationArgs " + s


class NumAppArgs(TransactionField):
    def __str__(self) -> str:
        return "NumAppArgs"


class Accounts(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Accounts " + s


class NumAccounts(TransactionField):
    def __str__(self) -> str:
        return "NumAccounts"


class Applications(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Applications " + s


class NumApplications(TransactionField):
    def __str__(self) -> str:
        return "NumApplications"


class Assets(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Assets " + s


class NumAssets(TransactionField):
    def __str__(self) -> str:
        return "NumAssets"


class ApprovalProgram(TransactionField):
    def __str__(self) -> str:
        return "ApprovalProgram"


class ClearStateProgram(TransactionField):
    def __str__(self) -> str:
        return "ClearStateProgram"


class RekeyTo(TransactionField):
    def __str__(self) -> str:
        return "RekeyTo"


class ConfigAsset(TransactionField):
    def __str__(self) -> str:
        return "ConfigAsset"


class ConfigAssetTotal(TransactionField):
    def __str__(self) -> str:
        return "ConfigAssetTotal"


class ConfigAssetDecimals(TransactionField):
    def __str__(self) -> str:
        return "ConfigAssetDecimals"


class ConfigAssetDefaultFrozen(TransactionField):
    def __str__(self) -> str:
        return "ConfigAssetDefaultFrozen"


class ConfigAssetUnitName(TransactionField):
    def __str__(self) -> str:
        return "ConfigAssetUnitName"


class ConfigAssetName(TransactionField):
    def __str__(self) -> str:
        return "ConfigAssetName"


class ConfigAssetURL(TransactionField):
    def __str__(self) -> str:
        return "ConfigAssetURL"


class ConfigAssetMetadataHash(TransactionField):
    def __str__(self) -> str:
        return "ConfigAssetMetadataHash"


class ConfigAssetManager(TransactionField):
    def __str__(self) -> str:
        return "ConfigAssetManager"


class ConfigAssetReserve(TransactionField):
    def __str__(self) -> str:
        return "ConfigAssetReserve"


class ConfigAssetFreeze(TransactionField):
    def __str__(self) -> str:
        return "ConfigAssetFreeze"


class ConfigAssetClawback(TransactionField):
    def __str__(self) -> str:
        return "ConfigAssetClawback"


class FreezeAsset(TransactionField):
    def __str__(self) -> str:
        return "FreezeAsset"


class FreezeAssetAccount(TransactionField):
    def __str__(self) -> str:
        return "FreezeAssetAccount"


class FreezeAssetFrozen(TransactionField):
    def __str__(self) -> str:
        return "FreezeAssetFrozen"


class GlobalNumUint(TransactionField):
    def __str__(self) -> str:
        return "GlobalNumUint"


class GlobalNumByteSlice(TransactionField):
    def __str__(self) -> str:
        return "GlobalNumByteSlice"


class LocalNumUint(TransactionField):
    def __str__(self) -> str:
        return "LocalNumUint"


class LocalNumByteSlice(TransactionField):
    def __str__(self) -> str:
        return "LocalNumByteSlice"


class ExtraProgramPages(TransactionField):
    def __str__(self) -> str:
        return "ExtraProgramPages"


class Nonparticipation(TransactionField):
    def __str__(self) -> str:
        return "Nonparticipation"


class Logs(TransactionField):
    def __str__(self) -> str:
        return "Logs"


class NumLogs(TransactionField):
    def __str__(self) -> str:
        return "NumLogs"


class CreatedAssetID(TransactionField):
    def __str__(self) -> str:
        return "CreatedAssetID"


class CreatedApplicationID(TransactionField):
    def __str__(self) -> str:
        return "CreatedApplicationID"
