# pylint: disable=too-few-public-methods


class TransactionField:
    pass


class Accounts(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self):
        return f"Accounts {self._idx}"


class ApplicationID(TransactionField):
    def __str__(self):
        return "ApplicationID"


class ApplicationArgs(TransactionField):
    def __init__(self, idx: int):
        self._idx = idx

    def __str__(self):
        return f"ApplicationArgs {self._idx}"


class Amount(TransactionField):
    def __str__(self):
        return "Amount"


class AssetAmount(TransactionField):
    def __str__(self):
        return "AssetAmount"


class AssetCloseTo(TransactionField):
    def __str__(self):
        return "AssetCloseTo"


class AssetReceiver(TransactionField):
    def __str__(self):
        return "AssetReceiver"


class CloseRemainderTo(TransactionField):
    def __str__(self):
        return "CloseRemainderTo"


class Fee(TransactionField):
    def __str__(self):
        return "Fee"


class OnCompletion(TransactionField):
    def __str__(self):
        return "OnCompletion"


class Receiver(TransactionField):
    def __str__(self):
        return "Receiver"


class RekeyTo(TransactionField):
    def __str__(self):
        return "RekeyTo"


class Sender(TransactionField):
    def __str__(self):
        return "Sender"


class TypeEnum(TransactionField):
    def __str__(self):
        return "TypeEnum"


class GroupIndex(TransactionField):
    def __str__(self):
        return "GroupIndex"


class XferAsset(TransactionField):
    def __str__(self):
        return "XferAsset"


class NumAppArgs(TransactionField):
    def __str__(self):
        return "NumAppArgs"
