# pylint: disable=too-few-public-methods

# https://developer.algorand.org/docs/reference/teal/opcodes/#txn


class TransactionField:
    def __init__(self) -> None:
        self._version: int = 1

    @property
    def version(self) -> int:
        return self._version

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
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class OnCompletion(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ApplicationArgs(TransactionField):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 2

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "ApplicationArgs " + s


class NumAppArgs(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class Accounts(TransactionField):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 2

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Accounts " + s


class NumAccounts(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class Applications(TransactionField):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 3

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Applications " + s


class NumApplications(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class Assets(TransactionField):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 3

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Assets " + s


class NumAssets(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class ApprovalProgram(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ClearStateProgram(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class RekeyTo(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAsset(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetTotal(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetDecimals(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetDefaultFrozen(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetUnitName(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetName(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetURL(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetMetadataHash(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetManager(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetReserve(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetFreeze(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetClawback(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class FreezeAsset(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class FreezeAssetAccount(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class FreezeAssetFrozen(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class GlobalNumUint(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class GlobalNumByteSlice(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class LocalNumUint(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class LocalNumByteSlice(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class ExtraProgramPages(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Nonparticipation(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Logs(TransactionField):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 5

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Logs " + s


class NumLogs(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class CreatedAssetID(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class CreatedApplicationID(TransactionField):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5
