# pylint: disable=too-few-public-methods
class AcctParamsField:
    pass


class AcctBalance(AcctParamsField):
    def __str__(self) -> str:
        return "AcctBalance"


class AcctMinBalance(AcctParamsField):
    def __str__(self) -> str:
        return "AcctMinBalance"


class AcctAuthAddr(AcctParamsField):
    def __str__(self) -> str:
        return "AcctAuthAddr"
