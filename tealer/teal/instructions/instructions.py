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
        self._comment = ""
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
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, c: str):
        self._comment = c

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


class Assert(Instruction):
    def __str__(self):
        return "assert"


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


class PushInt(Instruction):
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
        return f"pushint {self._value}"


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


class Gtxns(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self):
        return f"Gtxns {self._field}"


class Gtxnsa(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self):
        return f"Gtxnsa {self._field}"


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


class Gload(Instruction):
    def __init__(self, idx: int, slot: int):
        super().__init__()
        self._idx = idx
        self._slot = slot

    def __str__(self):
        return f"gload {self._idx} {self._slot}"


class Gloads(Instruction):
    def __init__(self, slot: int):
        super().__init__()
        self._slot = slot

    def __str__(self):
        return f"gloads {self._slot}"


class Gaid(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self):
        return f"gaid {self._idx}"


class Gaids(Instruction):
    def __str__(self):
        return "gaids"


class Loads(Instruction):
    def __str__(self):
        return "loads"


class Stores(Instruction):
    def __str__(self):
        return "stores"


class Dig(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self):
        return f"dig {self._idx}"


class Swap(Instruction):
    def __str__(self):
        return "swap"


class GetBit(Instruction):
    def __str__(self):
        return "getbit"


class SetBit(Instruction):
    def __str__(self):
        return "setbit"


class GetByte(Instruction):
    def __str__(self):
        return "getbyte"


class SetByte(Instruction):
    def __str__(self):
        return "setbyte"


class Extract(Instruction):
    def __init__(self, idx: int, idy: int):
        super().__init__()
        self._idx = idx
        self._idy = idy

    @property
    def idx(self) -> int:
        return self._idx

    @property
    def idy(self) -> int:
        return self._idy

    def __str__(self):
        return f"extract {self._idx} {self._idy}"


class Extract3(Instruction):
    def __str__(self):
        return "extract3"


class Extract_uint16(Instruction):
    def __str__(self):
        return "extract_uint16"


class Extract_uint32(Instruction):
    def __str__(self):
        return "extract_uint32"


class Extract_uint64(Instruction):
    def __str__(self):
        return "extract_uint64"


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


class Ecdsa_verify(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self):
        return f"ecdsa_verify {self._idx}"


class Ecdsa_pk_decompress(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self):
        return f"ecdsa_pk_decompress {self._idx}"


class Ecdsa_pk_recover(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self):
        return f"ecdsa_pk_recover {self._idx}"


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


class Select(Instruction):
    def __str__(self):
        return "select"


class Cover(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self):
        return f"cover {self._idx}"


class Uncover(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self):
        return f"uncover {self._idx}"


class Concat(Instruction):
    def __str__(self):
        return "concat"


class InstructionWithLabel(Instruction):
    def __init__(self, label: str):
        super().__init__()
        label = label.replace(" ", "")
        self._label = label

    @property
    def label(self) -> str:
        return self._label


class B(InstructionWithLabel):
    def __str__(self):
        return f"b {self._label}"


class BZ(InstructionWithLabel):
    def __str__(self):
        return f"bz {self._label}"


class BNZ(InstructionWithLabel):
    def __str__(self):
        return f"bnz {self._label}"


class Label(InstructionWithLabel):
    def __str__(self):
        return f"{self._label}:"


class Callsub(InstructionWithLabel):
    def __str__(self):
        return f"callsub {self._label}"


class Return(Instruction):
    def __str__(self):
        return "return"


class Retsub(Instruction):
    def __init__(self):
        super().__init__()
        self._labels: List[Label] = []

    def add_label(self, p: Label):
        self._labels.append(p)

    def set_labels(self, p: List[Label]):
        self._labels = p

    @property
    def labels(self) -> List[Label]:
        return self._labels

    def __str__(self):
        return "retsub"


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


class MinBalance(Instruction):
    def __str__(self):
        return "min_balance"


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
        return f"addr {self._addr}"


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


class BitLen(Instruction):
    def __str__(self):
        return "bitlen"


class BModulo(Instruction):
    def __str__(self):
        return "b%"


class BNeq(Instruction):
    def __str__(self):
        return "b!="


class BEq(Instruction):
    def __str__(self):
        return "b=="


class BBitwiseAnd(Instruction):
    def __str__(self):
        return "b&"


class BBitwiseOr(Instruction):
    def __str__(self):
        return "b|"


class BAdd(Instruction):
    def __str__(self):
        return "b+"


class BSubtract(Instruction):
    def __str__(self):
        return "b-"


class BDiv(Instruction):
    def __str__(self):
        return "b/"


class BMul(Instruction):
    def __str__(self):
        return "b*"


class BGreaterE(Instruction):
    def __str__(self):
        return "b>="


class BGreater(Instruction):
    def __str__(self):
        return "b>"


class BLessE(Instruction):
    def __str__(self):
        return "b<="


class BLess(Instruction):
    def __str__(self):
        return "b<"


class BBitwiseXor(Instruction):
    def __str__(self):
        return "b^"


class BBitwiseInvert(Instruction):
    def __str__(self):
        return "b~"


class BZero(Instruction):
    def __str__(self):
        return "bzero"


class Mulw(Instruction):
    def __str__(self):
        return "mulw"


class Addw(Instruction):
    def __str__(self):
        return "addw"


class Divmodw(Instruction):
    def __str__(self):
        return "divmodw"


class Exp(Instruction):
    def __str__(self):
        return "exp"


class Expw(Instruction):
    def __str__(self):
        return "expw"


class Shl(Instruction):
    def __str__(self):
        return "shl"


class Shr(Instruction):
    def __str__(self):
        return "shr"


class Sqrt(Instruction):
    def __str__(self):
        return "sqrt"


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


class PushBytes(Instruction):
    def __init__(self, bytesb: str):
        super().__init__()
        self._bytes = bytesb

    def __str__(self):
        return f"pushbytes {self._bytes}"


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
