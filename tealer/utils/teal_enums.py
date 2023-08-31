from typing import Union

from tealer.utils.comparable_enum import ComparableEnum


class TealerTransactionType(ComparableEnum):
    Pay = 0x10
    KeyReg = 0x20
    Acfg = 0x30
    Axfer = 0x40
    Afrz = 0x50
    ApplNoOp = 0x60
    ApplOptIn = 0x61
    ApplCloseOut = 0x62
    ApplClearState = 0x63
    ApplUpdateApplication = 0x64
    ApplDeleteApplication = 0x65
    ApplCreation = 0x66
    Appl = 0x67

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class TransactionType(ComparableEnum):
    Invalid = 0x0
    Pay = 0x1
    KeyReg = 0x02
    Acfg = 0x3
    Axfer = 0x4
    Afrz = 0x5
    Appl = 0x6

    Any = 0x7
    Unknown = 0x8


def transaction_type_from_txt(txn_type: str) -> TransactionType:
    return {
        "pay": TransactionType.Pay,
        "keyreg": TransactionType.KeyReg,
        "acfg": TransactionType.Acfg,
        "axfer": TransactionType.Axfer,
        "afrz": TransactionType.Afrz,
        "appl": TransactionType.Appl,
        "txn": TransactionType.Any,
    }[txn_type]


class TransactionOnCompletion(ComparableEnum):
    NoOp = 0x0
    OptIn = 0x1
    CloseOut = 0x2
    ClearState = 0x3
    UpdateApplication = 0x4
    DeleteApplication = 0x5


ALL_TRANSACTION_TYPES = (
    TealerTransactionType.Pay,
    TealerTransactionType.KeyReg,
    TealerTransactionType.Acfg,
    TealerTransactionType.Axfer,
    TealerTransactionType.Appl,
    TealerTransactionType.ApplNoOp,
    TealerTransactionType.ApplOptIn,
    TealerTransactionType.ApplCloseOut,
    TealerTransactionType.ApplClearState,
    TealerTransactionType.ApplUpdateApplication,
    TealerTransactionType.ApplDeleteApplication,
    TealerTransactionType.ApplCreation,
)

APPLICATION_TRANSACTION_TYPES = (
    TealerTransactionType.ApplNoOp,
    TealerTransactionType.ApplOptIn,
    TealerTransactionType.ApplCloseOut,
    TealerTransactionType.ApplClearState,
    TealerTransactionType.ApplUpdateApplication,
    TealerTransactionType.ApplDeleteApplication,
    TealerTransactionType.ApplCreation,
)
TYPEENUM_TRANSACTION_TYPES = (
    TealerTransactionType.Pay,
    TealerTransactionType.KeyReg,
    TealerTransactionType.Acfg,
    TealerTransactionType.Axfer,
    TealerTransactionType.Afrz,
    TealerTransactionType.Appl,
)


def oncompletion_to_tealer_type(value: Union[str, int]) -> "TealerTransactionType":
    ENUM_NAMES_TO_INT = {
        "NoOp": 0,
        "OptIn": 1,
        "CloseOut": 2,
        "ClearState": 3,
        "UpdateApplication": 4,
        "DeleteApplication": 5,
    }
    INT_TO_TYPE = {
        0: TealerTransactionType.ApplNoOp,
        1: TealerTransactionType.ApplOptIn,
        2: TealerTransactionType.ApplCloseOut,
        3: TealerTransactionType.ApplClearState,
        4: TealerTransactionType.ApplUpdateApplication,
        5: TealerTransactionType.ApplDeleteApplication,
    }

    if not isinstance(value, int):
        value = ENUM_NAMES_TO_INT[value]

    return INT_TO_TYPE[value]


def transaction_type_to_tealer_type(value: Union[str, int]) -> "TealerTransactionType":
    ENUM_NAMES_TO_INT = {
        "pay": 1,
        "keyreg": 2,
        "acfg": 3,
        "axfer": 4,
        "afrz": 5,
        "appl": 6,
    }
    INT_TO_TYPE = {
        1: TealerTransactionType.Pay,
        2: TealerTransactionType.KeyReg,
        3: TealerTransactionType.Acfg,
        4: TealerTransactionType.Axfer,
        5: TealerTransactionType.Afrz,
        6: TealerTransactionType.Appl,
    }

    if not isinstance(value, int):
        value = ENUM_NAMES_TO_INT[value]

    return INT_TO_TYPE[value]


class ExecutionMode(ComparableEnum):
    """Execution mode of the instruction/function/contract.

    Stateless: Contract do not have access to persistent storage, block information, etc.
        All stateless contracts are LogicSigs.
    Stateful: Contracts have access to persistent storage and are referred to as Applications.
        A stateful contract can be an ApprovalProgram or a ClearStateProgram.
    Any: Contract can be executed in any mode, either stateless or stateful.
    """

    STATELESS = 0
    STATEFUL = 1
    ANY = 2

    def __str__(self) -> str:
        return self.name.title()


class ContractType(ComparableEnum):
    """Type of the contract.

    LogicSig: Contract is used to sign the transactions.
    ApprovalProgram: Contract is deployed onto the chain and will be executed for calls with
        on-complete value of NoOp, OptIn, CloseOut, UpdateApplication and DeleteApplication.
    ClearStateProgram: Contract is deployed onto the chain and will be executed for calls with
        on-complete value of ClearState.
    """

    LogicSig = 0
    ApprovalProgram = 1
    ClearStateProgram = 2

    Unknown = 99

    def __str__(self) -> str:
        return self.name


def contract_type_from_txt(contract_type: str) -> ContractType:
    return {
        "ApprovalProgram": ContractType.ApprovalProgram,
        "ClearStateProgram": ContractType.ClearStateProgram,
        "LogicSig": ContractType.LogicSig,
    }[contract_type]
