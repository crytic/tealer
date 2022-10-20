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

    def to_dict(self):
        pass


class Sender(TransactionField):
    """address of sender of this transaction."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "Sender", "type": self.type}


class Fee(TransactionField):
    """Transaction fee in micro-Algos."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "Fee", "type": self.type}


class FirstValid(TransactionField):
    """minimum round number after which this transaction is valid."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "FirstValid", "type": self.type}


class FirstValidTime(TransactionField):
    """reserved for future use. causes program to fail if used."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "FirstValidTime", "type": self.type}


class LastValid(TransactionField):
    """maximum round number before which this transaction is valid."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "LastValid", "type": self.type}


class Note(TransactionField):
    """Any data up to 1024 bytes."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "Note", "type": self.type}


class Lease(TransactionField):
    """A lease to enforces mutual exclusion of transactions."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "Lease", "type": self.type}


class Receiver(TransactionField):
    """Address of the account that receives the amount."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "Receiver", "type": self.type}


class Amount(TransactionField):
    """The total amount to sent in microAlgos."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "Amount", "type": self.type}


class CloseRemainderTo(TransactionField):
    """if set, the account will be closed and all funds will be sent to the given address"""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "CloseRemainderTo", "type": self.type}


class VotePK(TransactionField):
    """The root participation public key."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "VotePK", "type": self.type}


class SelectionPK(TransactionField):
    """The VRF public key."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "SelectionPK", "type": self.type}


class VoteFirst(TransactionField):
    """The first round the participation key is valid."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "VoteFirst", "type": self.type}


class VoteLast(TransactionField):
    """The last round the participation key is valid."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "VoteLast", "type": self.type}


class VoteKeyDilution(TransactionField):
    """Dilution for the 2-level participation key."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "VoteKeyDilution", "type": self.type}


class Type(TransactionField):
    """Specifies the type of the transaction"""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "Type", "type": self.type}


class TypeEnum(TransactionField):
    """Type of the transaction"""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "Type", "type": self.type}


class XferAsset(TransactionField):
    """The unique id of the asset to be transferred."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "XferAsset", "type": self.type}


class AssetAmount(TransactionField):
    """The amount of the asset to be transferred."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "AssetAmount", "type": self.type}


class AssetSender(TransactionField):
    """The sender of the asset transfer."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AssetSender", "type": self.type}


class AssetReceiver(TransactionField):
    """The receiver of the asset transfer."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AssetReceiver", "type": self.type}


class AssetCloseTo(TransactionField):
    """if set, removes the asset holding from sender and reduced minimum required balance."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AssetCloseTo", "type": self.type}


class GroupIndex(TransactionField):
    """Position of this transaction within the atomic group transaction."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "GroupIndex", "type": self.type}


class TxID(TransactionField):
    """The computed ID for this transaction."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "TxID", "type": self.type}


class ApplicationID(TransactionField):
    """ApplicationID from ApplicationCall transaction"""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "ApplicationID", "type": self.type}


class OnCompletion(TransactionField):
    """ApplicationCall transaction on completion action."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "OnCompletion", "type": self.type}


class ApplicationArgs(TransactionField):
    """Arguments passed to the application in the ApplicationCall."""

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 2

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "ApplicationArgs " + s

    def to_dict(self):
        return {"name": "ApplicationArgs", "type": self.type, "index": self._idx}


class NumAppArgs(TransactionField):
    """Number of Application Args."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "NumAppArgs", "type": self.type}


class Accounts(TransactionField):
    """Accounts listed in the ApplicationCall transaction."""

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 2

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Accounts " + s

    def to_dict(self):
        return {"name": "Accounts", "type": self.type, "index": self._idx}


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

    def to_dict(self):
        return {"name": "Applications", "type": self.type, "index": self._idx}


class NumApplications(TransactionField):
    """Number of Applications."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3

    def to_dict(self):
        return {"name": "NumApplications", "type": self.type}


class Assets(TransactionField):
    """Foreign Assets listed in the ApplicationCall transaction."""

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 3

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Assets " + s

    def to_dict(self):
        return {"name": "Assets", "type": self.type, "index": self._idx}


class NumAssets(TransactionField):
    """Number of Assets."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3

    def to_dict(self):
        return {"name": "NumAssets", "type": self.type}


class ApprovalProgram(TransactionField):
    """Approval program of the application."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "ApprovalProgram", "type": self.type}


class ClearStateProgram(TransactionField):
    """Clear state program of the application."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "ClearStateProgram", "type": self.type}


class RekeyTo(TransactionField):
    """Sender's new AuthAddr."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "RekeyTo", "type": self.type}


class ConfigAsset(TransactionField):
    """AssetID in asset config transaction."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "ConfigAsset", "type": self.type}


class ConfigAssetTotal(TransactionField):
    """Total number of units of asset created."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "ConfigAssetTotal", "type": self.type}


class ConfigAssetDecimals(TransactionField):
    """Number of digits to display after the decimal place."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "ConfigAssetDecimal", "type": self.type}


class ConfigAssetDefaultFrozen(TransactionField):
    """Whether the asset's slots are frozen by default or not."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "ConfigAssetDefaultFrozen", "type": self.type}


class ConfigAssetUnitName(TransactionField):
    """Unit name of the asset."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "ConfigAssetUnitName", "type": self.type}


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

    def to_dict(self):
        return {"name": "ConfigAssetMetadataHash", "type": self.type}


class ConfigAssetManager(TransactionField):
    """Manager address, only account that can authorize transactions to re-configure or destroy an asset."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "ConfigAssetManager", "type": self.type}


class ConfigAssetReserve(TransactionField):
    """Reserve address, where non-minted assets will reside."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "ConfigAssetReserve", "type": self.type}


class ConfigAssetFreeze(TransactionField):
    """Freeze account, which is allowed to freeze or unfreeze the asset holding for an account."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "ConfigAssetFreeze", "type": self.type}


class ConfigAssetClawback(TransactionField):
    """Clawback address, which can transfer assets from and to any asset holder."""

    def type(self):
        return "[]byte"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "ConfigAssetClawback", "type": self.type}


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

    def to_dict(self):
        return {"name": "FreezeAssetAccount", "type": self.type}


class FreezeAssetFrozen(TransactionField):
    """The new frozen value, 0 or 1."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2

    def to_dict(self):
        return {"name": "FreezeAssetFrozen", "type": self.type}


class GlobalNumUint(TransactionField):
    """Number of global state integers in ApplicationCall."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3

    def to_dict(self):
        return {"name": "GlobalNumUint", "type": self.type}


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

    def to_dict(self):
        return {"name": "LocalNumUint", "type": self.type}


class LocalNumByteSlice(TransactionField):
    """Number of local state byteslices in ApplicationCall."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3

    def to_dict(self):
        return {"name": "LocalNumByteSlice", "type": self.type}


class ExtraProgramPages(TransactionField):
    """Number of additional pages for each of approval and clear state programs."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def to_dict(self):
        return {"name": "ExtraProgramPages", "type": self.type}


class Nonparticipation(TransactionField):
    """Marks an account nonparticipating for rewards."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5

    def to_dict(self):
        return {"name": "Nonparticipation", "type": self.type}


class Logs(TransactionField):
    """Log messages emitted by an application call(itxn only)."""

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 5

    def __str__(self) -> str:
        s = "" if self._idx < 0 else str(self._idx)
        return "Logs " + s

    def to_dict(self):
        return {"name": "Logs", "type": self.type, "index": self._idx}


class NumLogs(TransactionField):
    """Number of log messages(itxn only)."""

    def type(self):
        return "uint64"

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5

    def to_dict(self):
        return {"name": "NumLogs", "type": self.type}


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

    def to_dict(self):
        return {"name": "CreatedApplicationID", "type": self.type}
