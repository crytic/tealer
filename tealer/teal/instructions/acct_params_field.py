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
        """Teal version this field is introduced in and supported from.

        Returns:
            Teal version the field is introduced in and supported from.
        """
        return self._version

    def __str__(self) -> str:
        return self.__class__.__qualname__


class AcctBalance(AcctParamsField):
    """Account balance in microalgos."""


class AcctMinBalance(AcctParamsField):
    """Minimum required balance for account, in microalgos."""


class AcctAuthAddr(AcctParamsField):
    """Address the account is rekeyed to."""


class AcctTotalNumUint(AcctParamsField):
    """The total number of uint64 values allocated by this account in Global and Local States."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 8


class AcctTotalNumByteSlice(AcctParamsField):
    """The total number of byte array values allocated by this account in Global and Local States."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 8


class AcctTotalExtraAppPages(AcctParamsField):
    """The number of extra app code pages used by this account."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 8


class AcctTotalAppsCreated(AcctParamsField):
    """The number of existing apps created by this account"""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 8


class AcctTotalAppsOptedIn(AcctParamsField):
    """The number of apps this account is opted into."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 8


class AcctTotalAssetsCreated(AcctParamsField):
    """The number of existing ASAs created by this account."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 8


class AcctTotalAssets(AcctParamsField):
    """The numbers of ASAs held by this account (including ASAs this account created)."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 8


class AcctTotalBoxes(AcctParamsField):
    """The number of existing boxes created by this account's app."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 8


class AcctTotalBoxBytes(AcctParamsField):
    """The total number of bytes used by this account's app's box keys and values."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 8
