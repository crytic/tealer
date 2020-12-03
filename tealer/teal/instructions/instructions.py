from typing import Union, List, TYPE_CHECKING, Optional

from tealer.teal.global_field import GlobalField
from tealer.teal.instructions.transaction_field import TransactionField

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock


class Instruction:
    def __init__(self):
        self._prev: List[Instruction] = []
        self._next: List[Instruction] = []
        self._line = 0
        self._bb: Optional["BasicBlock"] = None

    def add_prev(self, p):
        self._prev.append(p)

    def add_next(self, n):
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
    def line(self, l: int):
        self._line = l

    @property
    def bb(self) -> Optional["BasicBlock"]:
        return self._bb

    @bb.setter
    def bb(self, b: "BasicBlock"):
        self._bb = b


class Pragma(Instruction):
    def __init__(self, version: int):
        super().__init__()
        self._version = version

    def __str__(self):
        return f"#pragma version {self._version}"


class Err(Instruction):
    def __str__(self):
        return "err"


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

    def __str__(self):
        return f"int {self._value}"


class Txn(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self):
        return f"txn {self._field}"


class Txna(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field

    def __str__(self):
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

    def __str__(self):
        return f"gtxn {self._idx} {self._field}"


class Gtxna(Instruction):
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

    def __str__(self):
        return f"gtxna {self._idx} {self._field}"


class Load(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self):
        return f"load {self._idx}"


class Store(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self):
        return f"store {self._idx}"


class Sha256(Instruction):
    def __str__(self):
        return "sha256"


class Sha512_256(Instruction):
    def __str__(self):
        return "sha512_256"


class Keccak256(Instruction):
    def __str__(self):
        return "keccak256"


class Ed25519verify(Instruction):
    def __str__(self):
        return "ed25519verify"


class Global(Instruction):
    def __init__(self, field: GlobalField):
        super().__init__()
        self._field: GlobalField = field

    @property
    def field(self) -> GlobalField:
        return self._field

    def __str__(self):
        return f"global {self._field}"


class Dup(Instruction):
    def __str__(self):
        return "dup"


class Dup2(Instruction):
    def __str__(self):
        return "dup2"


class Concat(Instruction):
    def __str__(self):
        return "concat"


class B(Instruction):
    def __init__(self, label: str):
        super().__init__()
        label = label.replace(" ", "")
        self._label = label

    @property
    def label(self) -> str:
        return self._label

    def __str__(self):
        return f"b {self._label}"


class BZ(Instruction):
    def __init__(self, label: str):
        super().__init__()
        label = label.replace(" ", "")
        self._label = label

    @property
    def label(self) -> str:
        return self._label

    def __str__(self):
        return f"bz {self._label}"


class BNZ(Instruction):
    def __init__(self, label: str):
        super().__init__()
        label = label.replace(" ", "")
        self._label = label

    @property
    def label(self) -> str:
        return self._label

    def __str__(self):
        return f"bnz {self._label}"


class Label(Instruction):
    def __init__(self, label: str):
        super().__init__()
        label = label.replace(" ", "")
        self._label = label

    @property
    def label(self) -> str:
        return self._label

    def __str__(self):
        return f"{self._label}:"


class Return(Instruction):
    def __str__(self):
        return "return"


class AppGlobalGet(Instruction):
    def __str__(self):
        return "app_global_get"


class AppGlobalGetEx(Instruction):
    def __str__(self):
        return "app_global_get_ex"


class AppGlobalPut(Instruction):
    def __str__(self):
        return "app_global_put"


class AppGlobalDel(Instruction):
    def __str__(self):
        return "app_global_del"


class AppLocalGetEx(Instruction):
    def __str__(self):
        return "app_local_get_ex"


class AppLocalGet(Instruction):
    def __str__(self):
        return "app_local_get"


class AppLocalPut(Instruction):
    def __str__(self):
        return "app_local_put"


class AppLocalDel(Instruction):
    def __str__(self):
        return "app_local_del"


class AssetHoldingGet(Instruction):
    def __str__(self):
        return "asset_holding_get"


class AssetParamsGet(Instruction):
    def __str__(self):
        return "asset_params_get"


class AppOptedIn(Instruction):
    def __str__(self):
        return "app_opted_in"


class Balance(Instruction):
    def __str__(self):
        return "balance"


class Itob(Instruction):
    def __str__(self):
        return "itob"


class Btoi(Instruction):
    def __str__(self):
        return "btoi"


class Addr(Instruction):
    def __init__(self, addr: str):
        super().__init__()
        self._addr = addr

    def __str__(self):
        return "addr {self._addr}"


class Pop(Instruction):
    def __str__(self):
        return "pop"


class Not(Instruction):
    def __str__(self):
        return "!"


class Neq(Instruction):
    def __str__(self):
        return "!="


class Eq(Instruction):
    def __str__(self):
        return "=="


class Greater(Instruction):
    def __str__(self):
        return ">"


class GreaterE(Instruction):
    def __str__(self):
        return ">="


class Less(Instruction):
    def __str__(self):
        return "<"


class LessE(Instruction):
    def __str__(self):
        return "<="


class And(Instruction):
    def __str__(self):
        return "&&"


class Or(Instruction):
    def __str__(self):
        return "||"


class Add(Instruction):
    def __str__(self):
        return "+"


class Sub(Instruction):
    def __str__(self):
        return "-"


class Mul(Instruction):
    def __str__(self):
        return "*"


class Div(Instruction):
    def __str__(self):
        return "/"


class Modulo(Instruction):
    def __str__(self):
        return "%"


class BitwiseOr(Instruction):
    def __str__(self):
        return "|"


class BitwiseAnd(Instruction):
    def __str__(self):
        return "&"


class BitwiseXor(Instruction):
    def __str__(self):
        return "^"


class BitwiseInvert(Instruction):
    def __str__(self):
        return "~"


class Mulw(Instruction):
    def __str__(self):
        return "mulw"


class Addw(Instruction):
    def __str__(self):
        return "addw"


class Intcblock(Instruction):
    def __str__(self):
        return "intcblock"


class Intc(Instruction):
    def __init__(self, idx: str):
        super().__init__()
        self._idx = int(idx)

    def __str__(self):
        return f"intc {self._idx}"


class Intc0(Instruction):
    def __str__(self):
        return "intc_0"


class Intc1(Instruction):
    def __str__(self):
        return "intc_1"


class Intc2(Instruction):
    def __str__(self):
        return "intc_2"


class Intc3(Instruction):
    def __str__(self):
        return "intc_3"


class Bytec(Instruction):
    def __init__(self, idx: str):
        super().__init__()
        self._idx = int(idx)

    def __str__(self):
        return f"bytec {self._idx}"


class Bytec0(Instruction):
    def __str__(self):
        return "bytec_0"


class Bytec1(Instruction):
    def __str__(self):
        return "bytec_1"


class Bytec2(Instruction):
    def __str__(self):
        return "bytec_2"


class Bytec3(Instruction):
    def __str__(self):
        return "bytec_3"


class Arg(Instruction):
    def __init__(self, idx: str):
        super().__init__()
        self._idx = int(idx)

    def __str__(self):
        return f"arg {self._idx}"


class Arg0(Instruction):
    def __str__(self):
        return "arg_0"


class Arg1(Instruction):
    def __str__(self):
        return "arg_1"


class Arg2(Instruction):
    def __str__(self):
        return "arg_2"


class Arg3(Instruction):
    def __str__(self):
        return "arg_3"


class ByteBase64(Instruction):
    def __init__(self, bytesb64: str):
        super().__init__()
        self._bytes = bytesb64

    def __str__(self):
        return f"byte base64 {self._bytes}"


class Byte(Instruction):
    def __init__(self, bytesb: str):
        super().__init__()
        self._bytes = bytesb

    def __str__(self):
        return f"byte {self._bytes}"


class Len(Instruction):
    def __str__(self):
        return "len"


class Bytecblock(Instruction):
    def __str__(self):
        return "bytecblock"


class Substring(Instruction):
    def __init__(self, start: int, stop: int):
        super().__init__()
        self._start = int(start)
        self._stop = int(stop)

    def __str__(self):
        return f"substring {self._start} {self._stop}"


class Substring3(Instruction):
    def __str__(self):
        return "substring3"
