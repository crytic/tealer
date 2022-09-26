"""Defines classes to represent transaction fields.

Teal supports access to fields of the transaction that invoked the
execution of this contract through multiple instructions.

Each transaction field is represented by a class in tealer. All the
classes representing the fields must inherit from TransactionField class.

"""

# pylint: disable=too-few-public-methods

# https://developer.algorand.org/docs/reference/teal/opcodes/#txn


class TransactionField:
    """Base class representing a transaction field"""

    def __init__(self) -> None:
        self._version: int = 1

    @property
    def version(self) -> int:
        """Teal version this field is introduced in and supported from."""
        return self._version

    def type(self) -> str:
        ...

    def __str__(self) -> str:
        return self.__class__.__qualname__


class Sender(TransactionField):
    """address of sender of this transaction."""

    def type(self):
        return "[]byte"


class Fee(TransactionField):
    """Transaction fee in micro-Algos."""

    def type(self):
        return "uint64"


class FirstValid(TransactionField):
    """minimum round number after which this transaction is valid."""

    def type(self):
        return "uint64"


class FirstValidTime(TransactionField):
    """reserved for future use. causes program to fail if used."""

    def type(self):
        return "uint64"


class LastValid(TransactionField):
    """maximum round number before which this transaction is valid."""

    def type(self):
        return "uint64"


class Note(TransactionField):
    """Any data up to 1024 bytes."""

    def type(self):
        return "[]byte"


class Lease(TransactionField):
    """A lease to enforces mutual exclusion of transactions."""

    def type(self):
        return "[]byte"


class Receiver(TransactionField):
    """Address of the account that receives the amount."""

    def type(self):
        return "[]byte"


class Amount(TransactionField):
    """The total amount to sent in microAlgos."""

    def type(self):
        return "uint64"


class CloseRemainderTo(TransactionField):
    """if set, the account will be closed and all funds will be sent to the given address"""

    def type(self):
        return "[]byte"


class VotePK(TransactionField):
    """The root participation public key."""

    def type(self):
        return "[]byte"


class SelectionPK(TransactionField):
    """The VRF public key."""

    def type(self):
        return "[]byte"


class VoteFirst(TransactionField):
    """The first round the participation key is valid."""

    def type(self):
        return "uint64"


class VoteLast(TransactionField):
    """The last round the participation key is valid."""

    def type(self):
        return "uint64"


class VoteKeyDilution(TransactionField):
    """Dilution for the 2-level participation key."""

    def type(self):
        return "uint64"


class Type(TransactionField):
    """Specifies the type of the transaction"""

    def type(self):
        return "[]byte"


class TypeEnum(TransactionField):
    """Type of the transaction"""

    def type(self):
        return "uint64"


class XferAsset(TransactionField):
    """The unique id of the asset to be transferred."""

    def type(self):
        return "uint64"


class AssetAmount(TransactionField):
    """The amount of the asset to be transferred."""

    def type(self):
        return "uint64"


class AssetSender(TransactionField):
    """The sender of the asset transfer."""

    def type(self):
        return "[]byte"


class AssetReceiver(TransactionField):
    """The receiver of the asset transfer."""

    def type(self):
        return "[]byte"


class AssetCloseTo(TransactionField):
    """if set, removes the asset holding from sender and reduced minimum required balance."""

    def type(self):
        return "[]byte"


class GroupIndex(TransactionField):
    """Position of this transaction within the atomic group transaction."""

    def type(self):
        return "uint64"


class TxID(TransactionField):
    """The computed ID for this transaction."""

    def type(self):
        return "[]byte"


class ApplicationID(TransactionField):
    """ApplicationID from ApplicationCall transaction"""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class OnCompletion(TransactionField):
    """ApplicationCall transaction on completion action."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ApplicationArgs(TransactionField):
    """Arguments passed to the application in the ApplicationCall."""

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 2

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "ApplicationArgs " + s


class NumAppArgs(TransactionField):
    """Number of Application Args."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class Accounts(TransactionField):
    """Accounts listed in the ApplicationCall transaction."""

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 2

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Accounts " + s


class NumAccounts(TransactionField):
    """Number of Accounts."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class Applications(TransactionField):
    """Foreign Apps listed in the ApplicationCall transaction."""

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 3

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Applications " + s


class NumApplications(TransactionField):
    """Number of Applications."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class Assets(TransactionField):
    """Foreign Assets listed in the ApplicationCall transaction."""

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 3

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Assets " + s


class NumAssets(TransactionField):
    """Number of Assets."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class ApprovalProgram(TransactionField):
    """Approval program of the application."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ClearStateProgram(TransactionField):
    """Clear state program of the application."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class RekeyTo(TransactionField):
    """Sender's new AuthAddr."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAsset(TransactionField):
    """AssetID in asset config transaction."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetTotal(TransactionField):
    """Total number of units of asset created."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetDecimals(TransactionField):
    """Number of digits to display after the decimal place."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetDefaultFrozen(TransactionField):
    """Whether the asset's slots are frozen by default or not."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetUnitName(TransactionField):
    """Unit name of the asset."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetName(TransactionField):
    """The asset name."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetURL(TransactionField):
    """Url associated with the asset."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetMetadataHash(TransactionField):
    """32 byte commitment to some unspecified asset metadata."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetManager(TransactionField):
    """Manager address, only account that can authorize transactions to re-configure or destroy an asset."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetReserve(TransactionField):
    """Reserve address, where non-minted assets will reside."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetFreeze(TransactionField):
    """Freeze account, which is allowed to freeze or unfreeze the asset holding for an account."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetClawback(TransactionField):
    """Clawback address, which can transfer assets from and to any asset holder."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class FreezeAsset(TransactionField):
    """AssetID being frozen or un-frozen."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class FreezeAssetAccount(TransactionField):
    """address whose asset slot is being frozen or un-frozen."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class FreezeAssetFrozen(TransactionField):
    """The new frozen value, 0 or 1."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class GlobalNumUint(TransactionField):
    """Number of global state integers in ApplicationCall."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class GlobalNumByteSlice(TransactionField):
    """Number of global state byteslices in ApplicationCall."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class LocalNumUint(TransactionField):
    """Number of local state integers in ApplicationCall."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class LocalNumByteSlice(TransactionField):
    """Number of local state byteslices in ApplicationCall."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class ExtraProgramPages(TransactionField):
    """Number of additional pages for each of approval and clear state programs."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Nonparticipation(TransactionField):
    """Marks an account nonparticipating for rewards."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Logs(TransactionField):
    """Log messages emitted by an application call(itxn only)."""

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 5

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Logs " + s


class NumLogs(TransactionField):
    """Number of log messages(itxn only)."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class CreatedAssetID(TransactionField):
    """Asset ID allocated by the creation of an ASA (itxn only)."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class CreatedApplicationID(TransactionField):
    """ApplicationID allocated by the creation of an application (itxn only)."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5
