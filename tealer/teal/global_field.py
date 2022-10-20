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
        """Teal version this field is introduced in and supported from."""
        return self._version

    def type(self) -> str:
        ...

    def __str__(self) -> str:
        return self.__class__.__qualname__

    def to_dict(self):
        pass


class GroupSize(GlobalField):
    """Number of transactions in this atomic transaction group."""

    def type(self) -> str:
        return "uint64"

    def to_dict(self):
        return {"name": "GroupSize", "type": self.type}


class MinTxnFee(GlobalField):
    """Minimum transaction fee in micro algos."""

    def type(self) -> str:
        return "uint64"

    def to_dict(self):
        return {"name": "MinTxnFee", "type": self.type}


class ZeroAddress(GlobalField):
    """32 byte address of all zero bytes"""

    def type(self) -> str:
        return "[]byte"

    def to_dict(self):
        return {"name": "ZeroAddress", "type": self.type}


class MinBalance(GlobalField):
    """Minimum balance in micro algos."""

    def type(self) -> str:
        return "uint64"

    def to_dict(self):
        return {"name": "MinBalance", "type": self.type}


class MaxTxnLife(GlobalField):
    """Maximum Transaction Life in number of rounds."""

    def type(self) -> str:
        return "uint64"

    def to_dict(self):
        return {"name": "MaxTxnLife", "type": self.type}


class LogicSigVersion(GlobalField):
    """Maximum supported TEAL version."""

    def __init__(self) -> None:
        super().__init__()
        self._version = 2

    def type(self) -> str:
        return "uint64"

    def to_dict(self):
        return {"name": "LogicSigVersion", "type": self.type}


class Round(GlobalField):
    """Current round number."""

    def __init__(self) -> None:
        super().__init__()
        self._version = 2

    def type(self) -> str:
        return "uint64"

    def to_dict(self):
        return {"name": "Round", "type": self.type}


class LatestTimestamp(GlobalField):
    """Last confirmed block unix timestamp. Fails if negative."""

    def __init__(self) -> None:
        super().__init__()
        self._version = 2

    def type(self) -> str:
        return "uint64"

    def to_dict(self):
        return {"name": "LatestTimestamp", "type": self.type}


class CurrentApplicationID(GlobalField):
    """ID of the current application executing."""

    def __init__(self) -> None:
        super().__init__()
        self._version = 2

    def type(self) -> str:
        return "uint64"

    def to_dict(self):
        return {"name": "CurrentApplicationID", "type": self.type}


class CreatorAddress(GlobalField):
    """Address of the creator of the current application."""

    def __init__(self) -> None:
        super().__init__()
        self._version = 3

    def type(self) -> str:
        return "[]byte"

    def to_dict(self):
        return {"name": "CreatorAddress", "type": self.type}


class CurrentApplicationAddress(GlobalField):
    """Address that the current application controls."""

    def __init__(self) -> None:
        super().__init__()
        self._version = 5

    def type(self) -> str:
        return "[]byte"

    def to_dict(self):
        return {"name": "CurrentApplicationAddress", "type": self.type}


class GroupID(GlobalField):
    """ID of the transaction group.

    ID will be 32 zero bytes if the transaction is not part
    of the group.
    """

    def __init__(self) -> None:
        super().__init__()
        self._version = 5

    def type(self) -> str:
        return "[]byte"

    def to_dict(self):
        return {"name": "GroupID", "type": self.type}
