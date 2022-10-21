"""Defines classes to represent acct_params_get fields.

``acct_params_get`` instruction is used to access fields
of an account in the contract.

Each field that can be accessed using acct_params_get is represented
by a class in tealer. All the classes representing the fields must
inherit from AcctParamsField class.

"""

# pylint: disable=too-few-public-methods
class AcctParamsField:
    """Base class to represent Acct fields."""

    def __init__(self) -> None:
        self._version: int = 6

    @property
    def version(self) -> int:
        """Teal version this field is introduced in and supported from."""
        return self._version

    def __str__(self) -> str:
        return self.__class__.__qualname__


class AcctBalance(AcctParamsField):
    """Account balance in microalgos."""


class AcctMinBalance(AcctParamsField):
    """Minimum required balance for account, in microalgos."""


class AcctAuthAddr(AcctParamsField):
    """Address the account is rekeyed to."""
