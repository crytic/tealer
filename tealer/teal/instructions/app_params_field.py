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
        """Teal version this field is introduced in and supported from."""
        return self._version

    def type(self) -> str:
        ...

    def __str__(self) -> str:
        return self.__class__.__qualname__

    def to_dict(self):
        pass


class AppApprovalProgram(AppParamsField):
    """Bytecode of approval program of the App."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AppApprovalProgram", "type": self.type}


class AppClearStateProgram(AppParamsField):
    """Bytecode of clear state program of the App."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AppClearStateProgram", "type": self.type}


class AppGlobalNumUint(AppParamsField):
    """Number of uint64 values allowed in Global State."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "AppGlobalNumUint", "type": self.type}


class AppGlobalNumByteSlice(AppParamsField):
    """Number of byte array values allowed in Global State."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "AppGlobalNumByteSlice", "type": self.type}


class AppLocalNumUint(AppParamsField):
    """Number of uint64 values allowed in Local State."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "AppLocalNumUint", "type": self.type}


class AppLocalNumByteSlice(AppParamsField):
    """Number of byte array values allowed in Local State."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "AppLocalNumByteSlice", "type": self.type}


class AppExtraProgramPages(AppParamsField):
    """Number of extra program pages of code space."""

    def type(self):
        return "uint64"

    def to_dict(self):
        return {"name": "AppExtraProgramPages", "type": self.type}


class AppCreator(AppParamsField):
    """Address of Creator(deployer) of the application."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AppCreator", "type": self.type}


class AppAddress(AppParamsField):
    """Address for which this application has authority."""

    def type(self):
        return "[]byte"

    def to_dict(self):
        return {"name": "AppAddress", "type": self.type}
