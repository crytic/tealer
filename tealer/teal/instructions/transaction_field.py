# pylint: disable=too-few-public-methods

# https://developer.algorand.org/docs/reference/teal/opcodes/#txn


class TransactionField:
    def __str__(self) -> str:
        return self.__class__.__qualname__


class Sender(TransactionField):
    pass


class Fee(TransactionField):
    pass


class FirstValid(TransactionField):
    pass


class FirstValidTime(TransactionField):
    pass


class LastValid(TransactionField):
    pass


class Note(TransactionField):
    pass


class Lease(TransactionField):
    pass


class Receiver(TransactionField):
    pass


class Amount(TransactionField):
    pass


class CloseRemainderTo(TransactionField):
    pass


class VotePK(TransactionField):
    pass


class SelectionPK(TransactionField):
    pass


class VoteFirst(TransactionField):
    pass


class VoteLast(TransactionField):
    pass


class VoteKeyDilution(TransactionField):
    pass


class Type(TransactionField):
    pass


class TypeEnum(TransactionField):
    pass


class XferAsset(TransactionField):
    pass


class AssetAmount(TransactionField):
    pass


class AssetSender(TransactionField):
    pass


class AssetReceiver(TransactionField):
    pass


class AssetCloseTo(TransactionField):
    pass


class GroupIndex(TransactionField):
    pass


class TxID(TransactionField):
    pass


class ApplicationID(TransactionField):
    pass


class OnCompletion(TransactionField):
    pass


class ApplicationArgs(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "ApplicationArgs " + s


class NumAppArgs(TransactionField):
    pass


class Accounts(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Accounts " + s


class NumAccounts(TransactionField):
    pass


class Applications(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Applications " + s


class NumApplications(TransactionField):
    pass


class Assets(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Assets " + s


class NumAssets(TransactionField):
    pass


class ApprovalProgram(TransactionField):
    pass


class ClearStateProgram(TransactionField):
    pass


class RekeyTo(TransactionField):
    pass


class ConfigAsset(TransactionField):
    pass


class ConfigAssetTotal(TransactionField):
    pass


class ConfigAssetDecimals(TransactionField):
    pass


class ConfigAssetDefaultFrozen(TransactionField):
    pass


class ConfigAssetUnitName(TransactionField):
    pass


class ConfigAssetName(TransactionField):
    pass


class ConfigAssetURL(TransactionField):
    pass


class ConfigAssetMetadataHash(TransactionField):
    pass


class ConfigAssetManager(TransactionField):
    pass


class ConfigAssetReserve(TransactionField):
    pass


class ConfigAssetFreeze(TransactionField):
    pass


class ConfigAssetClawback(TransactionField):
    pass


class FreezeAsset(TransactionField):
    pass


class FreezeAssetAccount(TransactionField):
    pass


class FreezeAssetFrozen(TransactionField):
    pass


class GlobalNumUint(TransactionField):
    pass


class GlobalNumByteSlice(TransactionField):
    pass


class LocalNumUint(TransactionField):
    pass


class LocalNumByteSlice(TransactionField):
    pass


class ExtraProgramPages(TransactionField):
    pass


class Nonparticipation(TransactionField):
    pass


class Logs(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Logs " + s


class NumLogs(TransactionField):
    pass


class CreatedAssetID(TransactionField):
    pass


class CreatedApplicationID(TransactionField):
    pass
