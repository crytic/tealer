# pylint: disable=too-few-public-methods
class AppParamsField:
    """Base class to represent App fields."""

    def __init__(self) -> None:
        self._version: int = 5

    @property
    def version(self) -> int:
        return self._version

    def __str__(self) -> str:
        return self.__class__.__qualname__


class AppApprovalProgram(AppParamsField):
    """Bytecode of approval program."""


class AppClearStateProgram(AppParamsField):
    """Bytecode of clear state program."""


class AppGlobalNumUint(AppParamsField):
    """Number of uint64 values allowed in Global State."""


class AppGlobalNumByteSlice(AppParamsField):
    """Number of byte array values allowed in Global State."""


class AppLocalNumUint(AppParamsField):
    """Number of uint64 values allowed in Local State."""


class AppLocalNumByteSlice(AppParamsField):
    """Number of byte array values allowed in Local State."""


class AppExtraProgramPages(AppParamsField):
    """Number of extra program pages of code space."""


class AppCreator(AppParamsField):
    """Creator address."""


class AppAddress(AppParamsField):
    """Address for which this application has authority."""
