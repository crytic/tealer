"""Defines classes to represent global fields.

Global fields are fields that are common to all the transactions
in the group. Teal supports access to this fields using ``global``
instruction.

Each global field is represented by a class in tealer. All the
classes representing the fields must inherit from GlobalField class.

"""

# pylint: disable=too-few-public-methods
class GlobalField:
    """Base class representing a global field"""

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


class GroupSize(GlobalField):
    """Number of transactions in this atomic transaction group."""


class MinTxnFee(GlobalField):
    """Minimum transaction fee in micro algos."""


class ZeroAddress(GlobalField):
    """32 byte address of all zero bytes"""


class MinBalance(GlobalField):
    """Minimum balance in micro algos."""


class MaxTxnLife(GlobalField):
    """Maximum Transaction Life in number of rounds."""


class LogicSigVersion(GlobalField):
    """Maximum supported TEAL version."""

    def __init__(self) -> None:
        super().__init__()
        self._version = 2


class Round(GlobalField):
    """Current round number."""

    def __init__(self) -> None:
        super().__init__()
        self._version = 2


class LatestTimestamp(GlobalField):
    """Last confirmed block unix timestamp. Fails if negative."""

    def __init__(self) -> None:
        super().__init__()
        self._version = 2


class CurrentApplicationID(GlobalField):
    """ID of the current application executing."""

    def __init__(self) -> None:
        super().__init__()
        self._version = 2


class CreatorAddress(GlobalField):
    """Address of the creator of the current application."""

    def __init__(self) -> None:
        super().__init__()
        self._version = 3


class CurrentApplicationAddress(GlobalField):
    """Address that the current application controls."""

    def __init__(self) -> None:
        super().__init__()
        self._version = 5


class GroupID(GlobalField):
    """ID of the transaction group.

    ID will be 32 zero bytes if the transaction is not part
    of the group.
    """

    def __init__(self) -> None:
        super().__init__()
        self._version = 5


class OpcodeBudget(GlobalField):
    """The remaining cost that can be spent by opcodes in the program"""

    def __init__(self) -> None:
        super().__init__()
        self._version = 6


class CallerApplicationID(GlobalField):
    """The application ID of the application that called this application.

    ID wil be 0 if the current application is at the top-level. Application mode only.
    """

    def __init__(self) -> None:
        super().__init__()
        self._version = 6


class CallerApplicationAddress(GlobalField):
    """The application address of the application that called this application.

    ZeroAddress if this application is at the top-level. Application mode only.
    """

    def __init__(self) -> None:
        super().__init__()
        self._version = 6
