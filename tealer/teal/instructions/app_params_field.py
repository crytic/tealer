"""Defines classes to represent app_params_get fields.

``app_params_get`` instruction is used to access parameter fields
of an application in the contract.

Each field that can be accessed using app_params_get is represented
by a class in tealer. All the classes representing the fields must
inherit from AppParamsField class.

"""

# pylint: disable=too-few-public-methods
class AppParamsField:
    """Base class to represent App fields."""

    def __init__(self) -> None:
        self._version: int = 5

    @property
    def version(self) -> int:
        """Teal version this field is introduced in and supported from.

        Returns:
            Teal version the field is introduced in and supported from.
        """
        return self._version

    def __str__(self) -> str:
        return self.__class__.__qualname__


class AppApprovalProgram(AppParamsField):
    """Bytecode of approval program of the App."""


class AppClearStateProgram(AppParamsField):
    """Bytecode of clear state program of the App."""


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
    """Address of Creator(deployer) of the application."""


class AppAddress(AppParamsField):
    """Address for which this application has authority."""
