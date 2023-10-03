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
        """Teal version this field is introduced in and supported from.

        Returns:
            Teal version the field is introduced in and supported from.
        """
        return self._version

    def __str__(self) -> str:
        return self.__class__.__qualname__


class TransactionArrayField(TransactionField):
    """Base class to represent array transaction fields.

    Array transaction fields have an additional index parameter.
    """

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    @property
    def idx(self) -> int:
        return self._idx

    def __str__(self) -> str:
        s = "" if self._idx < 0 else " " + str(self._idx)
        return self.__class__.__qualname__ + s


class Sender(TransactionField):
    """address of sender of this transaction."""


class Fee(TransactionField):
    """Transaction fee in micro-Algos."""


class FirstValid(TransactionField):
    """minimum round number after which this transaction is valid."""


class LastValid(TransactionField):
    """maximum round number before which this transaction is valid."""


class Note(TransactionField):
    """Any data up to 1024 bytes."""


class Lease(TransactionField):
    """A lease to enforces mutual exclusion of transactions."""


class Receiver(TransactionField):
    """Address of the account that receives the amount."""


class Amount(TransactionField):
    """The total amount to sent in microAlgos."""


class CloseRemainderTo(TransactionField):
    """if set, the account will be closed and all funds will be sent to the given address"""


class VotePK(TransactionField):
    """The root participation public key."""


class SelectionPK(TransactionField):
    """The VRF public key."""


class VoteFirst(TransactionField):
    """The first round the participation key is valid."""


class VoteLast(TransactionField):
    """The last round the participation key is valid."""


class VoteKeyDilution(TransactionField):
    """Dilution for the 2-level participation key."""


class Type(TransactionField):
    """Specifies the type of the transaction"""


class TypeEnum(TransactionField):
    """Type of the transaction"""


class XferAsset(TransactionField):
    """The unique id of the asset to be transferred."""


class AssetAmount(TransactionField):
    """The amount of the asset to be transferred."""


class AssetSender(TransactionField):
    """The sender of the asset transfer."""


class AssetReceiver(TransactionField):
    """The receiver of the asset transfer."""


class AssetCloseTo(TransactionField):
    """if set, removes the asset holding from sender and reduced minimum required balance."""


class GroupIndex(TransactionField):
    """Position of this transaction within the atomic group transaction."""


class TxID(TransactionField):
    """The computed ID for this transaction."""


class ApplicationID(TransactionField):
    """ApplicationID from ApplicationCall transaction"""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class OnCompletion(TransactionField):
    """ApplicationCall transaction on completion action."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ApplicationArgs(TransactionArrayField):
    """Arguments passed to the application in the ApplicationCall."""

    def __init__(self, idx: int):
        super().__init__(idx)
        self._version: int = 2


class NumAppArgs(TransactionField):
    """Number of Application Args."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class Accounts(TransactionArrayField):
    """Accounts listed in the ApplicationCall transaction."""

    def __init__(self, idx: int):
        super().__init__(idx)
        self._version: int = 2


class NumAccounts(TransactionField):
    """Number of Accounts."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class Applications(TransactionArrayField):
    """Foreign Apps listed in the ApplicationCall transaction."""

    def __init__(self, idx: int):
        super().__init__(idx)
        self._version: int = 3


class NumApplications(TransactionField):
    """Number of Applications."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class Assets(TransactionArrayField):
    """Foreign Assets listed in the ApplicationCall transaction."""

    def __init__(self, idx: int):
        super().__init__(idx)
        self._version: int = 3


class NumAssets(TransactionField):
    """Number of Assets."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class ApprovalProgram(TransactionField):
    """Approval program of the application."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ClearStateProgram(TransactionField):
    """Clear state program of the application."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class RekeyTo(TransactionField):
    """Sender's new AuthAddr."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAsset(TransactionField):
    """AssetID in asset config transaction."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetTotal(TransactionField):
    """Total number of units of asset created."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetDecimals(TransactionField):
    """Number of digits to display after the decimal place."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetDefaultFrozen(TransactionField):
    """Whether the asset's slots are frozen by default or not."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetUnitName(TransactionField):
    """Unit name of the asset."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetName(TransactionField):
    """The asset name."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetURL(TransactionField):
    """Url associated with the asset."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetMetadataHash(TransactionField):
    """32 byte commitment to some unspecified asset metadata."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetManager(TransactionField):
    """Manager address, only account that can authorize transactions to re-configure or destroy an asset."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetReserve(TransactionField):
    """Reserve address, where non-minted assets will reside."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetFreeze(TransactionField):
    """Freeze account, which is allowed to freeze or unfreeze the asset holding for an account."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class ConfigAssetClawback(TransactionField):
    """Clawback address, which can transfer assets from and to any asset holder."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class FreezeAsset(TransactionField):
    """AssetID being frozen or un-frozen."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class FreezeAssetAccount(TransactionField):
    """address whose asset slot is being frozen or un-frozen."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class FreezeAssetFrozen(TransactionField):
    """The new frozen value, 0 or 1."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class GlobalNumUint(TransactionField):
    """Number of global state integers in ApplicationCall."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class GlobalNumByteSlice(TransactionField):
    """Number of global state byteslices in ApplicationCall."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class LocalNumUint(TransactionField):
    """Number of local state integers in ApplicationCall."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class LocalNumByteSlice(TransactionField):
    """Number of local state byteslices in ApplicationCall."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class ExtraProgramPages(TransactionField):
    """Number of additional pages for each of approval and clear state programs."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Nonparticipation(TransactionField):
    """Marks an account nonparticipating for rewards."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Logs(TransactionArrayField):
    """Log messages emitted by an application call(itxn only)."""

    def __init__(self, idx: int):
        super().__init__(idx)
        self._version: int = 5


class NumLogs(TransactionField):
    """Number of log messages(itxn only)."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class CreatedAssetID(TransactionField):
    """Asset ID allocated by the creation of an ASA (itxn only)."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class CreatedApplicationID(TransactionField):
    """ApplicationID allocated by the creation of an application (itxn only)."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class LastLog(TransactionField):
    """([]byte) The last message emitted. Empty bytes if none were emitted. Application mode only"""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 6


class StateProofPK(TransactionField):
    """([]byte) 64 byte state proof public key"""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 6


class FirstValidTime(TransactionField):
    """(uint64) UNIX timestamp of block before txn.FirstValid. Fails if negative.

    FirstValidTime is present from Teal v1 itself. However, execution would fail if this
    field is used in versions less than v7.
    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 7


class NumApprovalProgramPages(TransactionField):
    """(uint64) Number of Approval Program pages"""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 7


class NumClearStateProgramPages(TransactionField):
    """(uint64) Number of clear state program pages"""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 7


class ApprovalProgramPages(TransactionArrayField):
    """Approval Program as an array of pages"""

    def __init__(self, idx: int):
        super().__init__(idx)
        self._version: int = 7


class ClearStateProgramPages(TransactionArrayField):
    """Approval Program as an array of pages"""

    def __init__(self, idx: int):
        super().__init__(idx)
        self._version: int = 7
