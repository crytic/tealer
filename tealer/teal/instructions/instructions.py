# pylint: disable=too-many-lines
from typing import Union, List, TYPE_CHECKING, Optional

from tealer.teal.global_field import GlobalField
from tealer.teal.instructions.transaction_field import TransactionField
from tealer.teal.instructions.asset_holding_field import AssetHoldingField
from tealer.teal.instructions.asset_params_field import AssetParamsField
from tealer.teal.instructions.app_params_field import AppParamsField
from tealer.utils.comparable_enum import ComparableEnum

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock


class ContractType(ComparableEnum):
    STATELESS = 0
    STATEFULL = 1
    ANY = 2


class Instruction:
    def __init__(self) -> None:
        self._prev: List[Instruction] = []
        self._next: List[Instruction] = []
        self._line = 0
        self._comment = ""
        self._bb: Optional["BasicBlock"] = None
        self._version: int = 1
        self._mode: ContractType = ContractType.ANY

    def add_prev(self, p: "Instruction") -> None:
        self._prev.append(p)

    def add_next(self, n: "Instruction") -> None:
        self._next.append(n)

    @property
    def prev(self) -> List["Instruction"]:
        return self._prev

    @property
    def next(self) -> List["Instruction"]:
        return self._next

    @property
    def line(self) -> int:
        return self._line

    @line.setter
    def line(self, l: int) -> None:
        self._line = l

    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, c: str) -> None:
        self._comment = c

    @property
    def bb(self) -> Optional["BasicBlock"]:
        return self._bb

    @bb.setter
    def bb(self, b: "BasicBlock") -> None:
        self._bb = b

    @property
    def version(self) -> int:
        return self._version

    @property
    def mode(self) -> ContractType:
        return self._mode

    def __str__(self) -> str:
        return self.__class__.__qualname__.lower()


class Pragma(Instruction):
    def __init__(self, version: int):
        super().__init__()
        self._program_version = version

    def __str__(self) -> str:
        return f"#pragma version {self._program_version}"

    @property
    def program_version(self) -> int:
        return self._program_version


class Err(Instruction):
    pass


class Assert(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class Int(Instruction):
    def __init__(self, value: str):
        super().__init__()
        if value.isdigit():
            self._value: Union[int, str] = int(value)
        else:
            self._value = value

    @property
    def value(self) -> Union[str, int]:
        return self._value

    def __str__(self) -> str:
        return f"int {self._value}"


class PushInt(Instruction):
    def __init__(self, value: str):
        super().__init__()
        if value.isdigit():
            self._value: Union[int, str] = int(value)
        else:
            self._value = value
        self._version = 3

    @property
    def value(self) -> Union[str, int]:
        return self._value

    def __str__(self) -> str:
        return f"pushint {self._value}"


class Txn(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"txn {self._field}"


class Txna(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 2

    def __str__(self) -> str:
        return f"txna {self._field}"


class Gtxn(Instruction):
    def __init__(self, idx: int, field: TransactionField):
        super().__init__()
        self._idx = idx
        self._field: TransactionField = field

    @property
    def idx(self) -> int:
        return self._idx

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"gtxn {self._idx} {self._field}"


class Gtxna(Instruction):
    def __init__(self, idx: int, field: TransactionField):
        super().__init__()
        self._idx = idx
        self._field: TransactionField = field
        self._version: int = 2

    @property
    def idx(self) -> int:
        return self._idx

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"gtxna {self._idx} {self._field}"


class Gtxns(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 3

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"Gtxns {self._field}"


class Gtxnsa(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 3

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"Gtxnsa {self._field}"


class Load(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self) -> str:
        return f"load {self._idx}"


class Store(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self) -> str:
        return f"store {self._idx}"


class Gload(Instruction):
    def __init__(self, idx: int, slot: int):
        super().__init__()
        self._idx = idx
        self._slot = slot
        self._version: int = 4
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return f"gload {self._idx} {self._slot}"


class Gloads(Instruction):
    def __init__(self, slot: int):
        super().__init__()
        self._slot = slot
        self._version: int = 4
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return f"gloads {self._slot}"


class Gaid(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 4
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return f"gaid {self._idx}"


class Gaids(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4
        self._mode: ContractType = ContractType.STATEFULL


class Loads(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Stores(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Dig(Instruction):
    def __init__(self, idx: int) -> None:
        super().__init__()
        self._idx = idx
        self._version: int = 3

    def __str__(self) -> str:
        return f"dig {self._idx}"


class Swap(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class GetBit(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class SetBit(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class GetByte(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class SetByte(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class Extract(Instruction):
    def __init__(self, idx: int, idy: int) -> None:
        super().__init__()
        self._idx = idx
        self._idy = idy
        self._version: int = 5

    @property
    def idx(self) -> int:
        return self._idx

    @property
    def idy(self) -> int:
        return self._idy

    def __str__(self) -> str:
        return f"extract {self._idx} {self._idy}"


class Extract3(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Extract_uint16(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Extract_uint32(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Extract_uint64(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Sha256(Instruction):
    pass


class Sha512_256(Instruction):
    pass


class Keccak256(Instruction):
    pass


class Ed25519verify(Instruction):
    pass


class Ecdsa_verify(Instruction):
    def __init__(self, idx: str):
        super().__init__()
        self._idx = idx
        self._version: int = 5

    def __str__(self) -> str:
        return f"ecdsa_verify {self._idx}"


class Ecdsa_pk_decompress(Instruction):
    def __init__(self, idx: str):
        super().__init__()
        self._idx = idx
        self._version: int = 5

    def __str__(self) -> str:
        return f"ecdsa_pk_decompress {self._idx}"


class Ecdsa_pk_recover(Instruction):
    def __init__(self, idx: str):
        super().__init__()
        self._idx = idx
        self._version: int = 5

    def __str__(self) -> str:
        return f"ecdsa_pk_recover {self._idx}"


class Global(Instruction):
    def __init__(self, field: GlobalField):
        super().__init__()
        self._field: GlobalField = field

    @property
    def field(self) -> GlobalField:
        return self._field

    def __str__(self) -> str:
        return f"global {self._field}"


class Dup(Instruction):
    pass


class Dup2(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class Select(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class Cover(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 5

    def __str__(self) -> str:
        return f"cover {self._idx}"


class Uncover(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 5

    def __str__(self) -> str:
        return f"uncover {self._idx}"


class Concat(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class InstructionWithLabel(Instruction):
    def __init__(self, label: str):
        super().__init__()
        label = label.replace(" ", "")
        self._label = label

    @property
    def label(self) -> str:
        return self._label


class B(InstructionWithLabel):
    def __init__(self, label: str):
        super().__init__(label)
        self._version: int = 2

    def __str__(self) -> str:
        return f"b {self._label}"


class BZ(InstructionWithLabel):
    def __init__(self, label: str):
        super().__init__(label)
        self._version: int = 2

    def __str__(self) -> str:
        return f"bz {self._label}"


class BNZ(InstructionWithLabel):
    def __str__(self) -> str:
        return f"bnz {self._label}"


class Label(InstructionWithLabel):
    def __str__(self) -> str:
        return f"{self._label}:"


class Callsub(InstructionWithLabel):
    def __init__(self, label: str):
        super().__init__(label)
        self._version: int = 4

    def __str__(self) -> str:
        return f"callsub {self._label}"


class Return(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class Retsub(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._labels: List[Label] = []
        self._version: int = 4

    def add_label(self, p: Label) -> None:
        self._labels.append(p)

    def set_labels(self, p: List[Label]) -> None:
        self._labels = p

    @property
    def labels(self) -> List[Label]:
        return self._labels


class AppGlobalGet(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_global_get"


class AppGlobalGetEx(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_global_get_ex"


class AppGlobalPut(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_global_put"


class AppGlobalDel(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_global_del"


class AppLocalGetEx(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_local_get_ex"


class AppLocalGet(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_local_get"


class AppLocalPut(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_local_put"


class AppLocalDel(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_local_del"


class AssetHoldingGet(Instruction):
    def __init__(self, field: AssetHoldingField):
        super().__init__()
        self._field: AssetHoldingField = field
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    @property
    def field(self) -> AssetHoldingField:
        return self._field

    def __str__(self) -> str:
        return f"asset_holding_get {self._field}"


class AssetParamsGet(Instruction):
    def __init__(self, field: AssetParamsField):
        super().__init__()
        self._field: AssetParamsField = field
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    @property
    def field(self) -> AssetParamsField:
        return self._field

    def __str__(self) -> str:
        return f"asset_params_get {self._field}"


class AppParamsGet(Instruction):
    def __init__(self, field: AppParamsField):
        super().__init__()
        self._field: AppParamsField = field
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL

    @property
    def field(self) -> AppParamsField:
        return self._field

    def __str__(self) -> str:
        return f"app_params_get {self._field}"


class AppOptedIn(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_opted_in"


class Balance(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL


class MinBalance(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "min_balance"


class Itob(Instruction):
    pass


class Btoi(Instruction):
    pass


class Addr(Instruction):
    def __init__(self, addr: str):
        super().__init__()
        self._addr = addr

    def __str__(self) -> str:
        return f"addr {self._addr}"


class Pop(Instruction):
    pass


class Not(Instruction):
    def __str__(self) -> str:
        return "!"


class Neq(Instruction):
    def __str__(self) -> str:
        return "!="


class Eq(Instruction):
    def __str__(self) -> str:
        return "=="


class Greater(Instruction):
    def __str__(self) -> str:
        return ">"


class GreaterE(Instruction):
    def __str__(self) -> str:
        return ">="


class Less(Instruction):
    def __str__(self) -> str:
        return "<"


class LessE(Instruction):
    def __str__(self) -> str:
        return "<="


class And(Instruction):
    def __str__(self) -> str:
        return "&&"


class Or(Instruction):
    def __str__(self) -> str:
        return "||"


class Add(Instruction):
    def __str__(self) -> str:
        return "+"


class Sub(Instruction):
    def __str__(self) -> str:
        return "-"


class Mul(Instruction):
    def __str__(self) -> str:
        return "*"


class Div(Instruction):
    def __str__(self) -> str:
        return "/"


class Modulo(Instruction):
    def __str__(self) -> str:
        return "%"


class BitwiseOr(Instruction):
    def __str__(self) -> str:
        return "|"


class BitwiseAnd(Instruction):
    def __str__(self) -> str:
        return "&"


class BitwiseXor(Instruction):
    def __str__(self) -> str:
        return "^"


class BitwiseInvert(Instruction):
    def __str__(self) -> str:
        return "~"


class BitLen(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class BModulo(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b%"


class BNeq(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b!="


class BEq(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b=="


class BBitwiseAnd(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b&"


class BBitwiseOr(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b|"


class BAdd(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b+"


class BSubtract(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b-"


class BDiv(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b/"


class BMul(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b*"


class BGreaterE(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b>="


class BGreater(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b>"


class BLessE(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b<="


class BLess(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b<"


class BBitwiseXor(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b^"


class BBitwiseInvert(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b~"


class BZero(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Log(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL


class Itxn_begin(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL


class Itxn_field(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"itxn_field {self._field}"


class Itxn_submit(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL


class Itxn(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"itxn {self._field}"


class Itxna(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"itxna {self._field}"


class Txnas(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 5

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"txnas {self._field}"


class Gtxnas(Instruction):
    def __init__(self, idx: int, field: TransactionField):
        super().__init__()
        self._idx: int = idx
        self._field: TransactionField = field
        self._version: int = 5

    @property
    def idx(self) -> int:
        return self._idx

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"Gtxnas {self._idx} {self._field}"


class Gtxnsas(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 5

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"gtxnsas {self._field}"


class Args(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5
        self._mode: ContractType = ContractType.STATELESS


class Mulw(Instruction):
    pass


class Addw(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class Divmodw(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Exp(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Expw(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Shl(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Shr(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Sqrt(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Intcblock(Instruction):
    def __str__(self) -> str:
        return "intcblock"


class Intc(Instruction):
    def __init__(self, idx: str):
        super().__init__()
        self._idx = int(idx)

    def __str__(self) -> str:
        return f"intc {self._idx}"


class Intc0(Instruction):
    def __str__(self) -> str:
        return "intc_0"


class Intc1(Instruction):
    def __str__(self) -> str:
        return "intc_1"


class Intc2(Instruction):
    def __str__(self) -> str:
        return "intc_2"


class Intc3(Instruction):
    def __str__(self) -> str:
        return "intc_3"


class Bytec(Instruction):
    def __init__(self, idx: str):
        super().__init__()
        self._idx = int(idx)

    def __str__(self) -> str:
        return f"bytec {self._idx}"


class Bytec0(Instruction):
    def __str__(self) -> str:
        return "bytec_0"


class Bytec1(Instruction):
    def __str__(self) -> str:
        return "bytec_1"


class Bytec2(Instruction):
    def __str__(self) -> str:
        return "bytec_2"


class Bytec3(Instruction):
    def __str__(self) -> str:
        return "bytec_3"


class Arg(Instruction):
    def __init__(self, idx: str):
        super().__init__()
        self._idx = int(idx)
        self._mode: ContractType = ContractType.STATELESS

    def __str__(self) -> str:
        return f"arg {self._idx}"


class Arg0(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._mode: ContractType = ContractType.STATELESS

    def __str__(self) -> str:
        return "arg_0"


class Arg1(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._mode: ContractType = ContractType.STATELESS

    def __str__(self) -> str:
        return "arg_1"


class Arg2(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._mode: ContractType = ContractType.STATELESS

    def __str__(self) -> str:
        return "arg_2"


class Arg3(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._mode: ContractType = ContractType.STATELESS

    def __str__(self) -> str:
        return "arg_3"


class ByteBase64(Instruction):
    def __init__(self, bytesb64: str):
        super().__init__()
        self._bytes = bytesb64

    def __str__(self) -> str:
        return f"byte base64 {self._bytes}"


class Byte(Instruction):
    def __init__(self, bytesb: str):
        super().__init__()
        self._bytes = bytesb

    def __str__(self) -> str:
        return f"byte {self._bytes}"


class PushBytes(Instruction):
    def __init__(self, bytesb: str):
        super().__init__()
        self._bytes = bytesb
        self._version: int = 3

    def __str__(self) -> str:
        return f"pushbytes {self._bytes}"


class Len(Instruction):
    pass


class Bytecblock(Instruction):
    def __str__(self) -> str:
        return "bytecblock"


class Substring(Instruction):
    def __init__(self, start: int, stop: int):
        super().__init__()
        self._start = int(start)
        self._stop = int(stop)
        self._version: int = 2

    def __str__(self) -> str:
        return f"substring {self._start} {self._stop}"


class Substring3(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
