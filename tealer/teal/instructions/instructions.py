# pylint: disable=too-many-lines
from typing import Union, List, TYPE_CHECKING, Optional

from tealer.teal.global_field import GlobalField
from tealer.teal.instructions.transaction_field import TransactionField
from tealer.teal.instructions.asset_holding_field import AssetHoldingField
from tealer.teal.instructions.asset_params_field import AssetParamsField
from tealer.teal.instructions.app_params_field import AppParamsField

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock


class Instruction:
    def __init__(self) -> None:
        self._prev: List[Instruction] = []
        self._next: List[Instruction] = []
        self._line = 0
        self._comment = ""
        self._bb: Optional["BasicBlock"] = None

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


class Pragma(Instruction):
    def __init__(self, version: int):
        super().__init__()
        self._version = version

    def __str__(self) -> str:
        return f"#pragma version {self._version}"


class Err(Instruction):
    def __str__(self) -> str:
        return "err"


class Assert(Instruction):
    def __str__(self) -> str:
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

    def __str__(self) -> str:
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

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"Gtxns {self._field}"


class Gtxnsa(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field

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

    def __str__(self) -> str:
        return f"gload {self._idx} {self._slot}"


class Gloads(Instruction):
    def __init__(self, slot: int):
        super().__init__()
        self._slot = slot

    def __str__(self) -> str:
        return f"gloads {self._slot}"


class Gaid(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self) -> str:
        return f"gaid {self._idx}"


class Gaids(Instruction):
    def __str__(self) -> str:
        return "gaids"


class Loads(Instruction):
    def __str__(self) -> str:
        return "loads"


class Stores(Instruction):
    def __str__(self) -> str:
        return "stores"


class Dig(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self) -> str:
        return f"dig {self._idx}"


class Swap(Instruction):
    def __str__(self) -> str:
        return "swap"


class GetBit(Instruction):
    def __str__(self) -> str:
        return "getbit"


class SetBit(Instruction):
    def __str__(self) -> str:
        return "setbit"


class GetByte(Instruction):
    def __str__(self) -> str:
        return "getbyte"


class SetByte(Instruction):
    def __str__(self) -> str:
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

    def __str__(self) -> str:
        return f"extract {self._idx} {self._idy}"


class Extract3(Instruction):
    def __str__(self) -> str:
        return "extract3"


class Extract_uint16(Instruction):
    def __str__(self) -> str:
        return "extract_uint16"


class Extract_uint32(Instruction):
    def __str__(self) -> str:
        return "extract_uint32"


class Extract_uint64(Instruction):
    def __str__(self) -> str:
        return "extract_uint64"


class Sha256(Instruction):
    def __str__(self) -> str:
        return "sha256"


class Sha512_256(Instruction):
    def __str__(self) -> str:
        return "sha512_256"


class Keccak256(Instruction):
    def __str__(self) -> str:
        return "keccak256"


class Ed25519verify(Instruction):
    def __str__(self) -> str:
        return "ed25519verify"


class Ecdsa_verify(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self) -> str:
        return f"ecdsa_verify {self._idx}"


class Ecdsa_pk_decompress(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self) -> str:
        return f"ecdsa_pk_decompress {self._idx}"


class Ecdsa_pk_recover(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

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
    def __str__(self) -> str:
        return "dup"


class Dup2(Instruction):
    def __str__(self) -> str:
        return "dup2"


class Select(Instruction):
    def __str__(self) -> str:
        return "select"


class Cover(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self) -> str:
        return f"cover {self._idx}"


class Uncover(Instruction):
    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self) -> str:
        return f"uncover {self._idx}"


class Concat(Instruction):
    def __str__(self) -> str:
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
    def __str__(self) -> str:
        return f"b {self._label}"


class BZ(InstructionWithLabel):
    def __str__(self) -> str:
        return f"bz {self._label}"


class BNZ(InstructionWithLabel):
    def __str__(self) -> str:
        return f"bnz {self._label}"


class Label(InstructionWithLabel):
    def __str__(self) -> str:
        return f"{self._label}:"


class Callsub(InstructionWithLabel):
    def __str__(self) -> str:
        return f"callsub {self._label}"


class Return(Instruction):
    def __str__(self) -> str:
        return "return"


class Retsub(Instruction):
    def __init__(self) -> None:
        super().__init__()
        self._labels: List[Label] = []

    def add_label(self, p: Label) -> None:
        self._labels.append(p)

    def set_labels(self, p: List[Label]) -> None:
        self._labels = p

    @property
    def labels(self) -> List[Label]:
        return self._labels

    def __str__(self) -> str:
        return "retsub"


class AppGlobalGet(Instruction):
    def __str__(self) -> str:
        return "app_global_get"


class AppGlobalGetEx(Instruction):
    def __str__(self) -> str:
        return "app_global_get_ex"


class AppGlobalPut(Instruction):
    def __str__(self) -> str:
        return "app_global_put"


class AppGlobalDel(Instruction):
    def __str__(self) -> str:
        return "app_global_del"


class AppLocalGetEx(Instruction):
    def __str__(self) -> str:
        return "app_local_get_ex"


class AppLocalGet(Instruction):
    def __str__(self) -> str:
        return "app_local_get"


class AppLocalPut(Instruction):
    def __str__(self) -> str:
        return "app_local_put"


class AppLocalDel(Instruction):
    def __str__(self) -> str:
        return "app_local_del"


class AssetHoldingGet(Instruction):
    def __init__(self, field: AssetHoldingField):
        super().__init__()
        self._field: AssetHoldingField = field

    @property
    def field(self) -> AssetHoldingField:
        return self._field

    def __str__(self) -> str:
        return f"asset_holding_get {self._field}"


class AssetParamsGet(Instruction):
    def __init__(self, field: AssetParamsField):
        super().__init__()
        self._field: AssetParamsField = field

    @property
    def field(self) -> AssetParamsField:
        return self._field

    def __str__(self) -> str:
        return f"asset_params_get {self._field}"


class AppParamsGet(Instruction):
    def __init__(self, field: AppParamsField):
        super().__init__()
        self._field: AppParamsField = field

    @property
    def field(self) -> AppParamsField:
        return self._field

    def __str__(self) -> str:
        return f"app_params_get {self._field}"


class AppOptedIn(Instruction):
    def __str__(self) -> str:
        return "app_opted_in"


class Balance(Instruction):
    def __str__(self) -> str:
        return "balance"


class MinBalance(Instruction):
    def __str__(self) -> str:
        return "min_balance"


class Itob(Instruction):
    def __str__(self) -> str:
        return "itob"


class Btoi(Instruction):
    def __str__(self) -> str:
        return "btoi"


class Addr(Instruction):
    def __init__(self, addr: str):
        super().__init__()
        self._addr = addr

    def __str__(self) -> str:
        return f"addr {self._addr}"


class Pop(Instruction):
    def __str__(self) -> str:
        return "pop"


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
    def __str__(self) -> str:
        return "bitlen"


class BModulo(Instruction):
    def __str__(self) -> str:
        return "b%"


class BNeq(Instruction):
    def __str__(self) -> str:
        return "b!="


class BEq(Instruction):
    def __str__(self) -> str:
        return "b=="


class BBitwiseAnd(Instruction):
    def __str__(self) -> str:
        return "b&"


class BBitwiseOr(Instruction):
    def __str__(self) -> str:
        return "b|"


class BAdd(Instruction):
    def __str__(self) -> str:
        return "b+"


class BSubtract(Instruction):
    def __str__(self) -> str:
        return "b-"


class BDiv(Instruction):
    def __str__(self) -> str:
        return "b/"


class BMul(Instruction):
    def __str__(self) -> str:
        return "b*"


class BGreaterE(Instruction):
    def __str__(self) -> str:
        return "b>="


class BGreater(Instruction):
    def __str__(self) -> str:
        return "b>"


class BLessE(Instruction):
    def __str__(self) -> str:
        return "b<="


class BLess(Instruction):
    def __str__(self) -> str:
        return "b<"


class BBitwiseXor(Instruction):
    def __str__(self) -> str:
        return "b^"


class BBitwiseInvert(Instruction):
    def __str__(self) -> str:
        return "b~"


class BZero(Instruction):
    def __str__(self) -> str:
        return "bzero"


class Log(Instruction):
    def __str__(self) -> str:
        return "log"


class Itxn_begin(Instruction):
    def __str__(self) -> str:
        return "itxn_begin"


class Itxn_field(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"itxn_field {self._field}"


class Itxn_submit(Instruction):
    def __str__(self) -> str:
        return "itxn_submit"


class Itxn(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"itxn {self._field}"


class Itxna(Instruction):
    def __init__(self, field: TransactionField, idx: int):
        super().__init__()
        self._field: TransactionField = field
        self._idx: int = idx

    @property
    def field(self) -> TransactionField:
        return self._field

    @property
    def idx(self) -> int:
        return self._idx

    def __str__(self) -> str:
        return f"itxna {self._field} {self._idx}"


class Txnas(Instruction):
    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field

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

    @property
    def field(self) -> TransactionField:
        return self._field

    def __str__(self) -> str:
        return f"gtxnsas {self._field}"


class Args(Instruction):
    def __str__(self) -> str:
        return "args"


class Mulw(Instruction):
    def __str__(self) -> str:
        return "mulw"


class Addw(Instruction):
    def __str__(self) -> str:
        return "addw"


class Divmodw(Instruction):
    def __str__(self) -> str:
        return "divmodw"


class Exp(Instruction):
    def __str__(self) -> str:
        return "exp"


class Expw(Instruction):
    def __str__(self) -> str:
        return "expw"


class Shl(Instruction):
    def __str__(self) -> str:
        return "shl"


class Shr(Instruction):
    def __str__(self) -> str:
        return "shr"


class Sqrt(Instruction):
    def __str__(self) -> str:
        return "sqrt"


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

    def __str__(self) -> str:
        return f"arg {self._idx}"


class Arg0(Instruction):
    def __str__(self) -> str:
        return "arg_0"


class Arg1(Instruction):
    def __str__(self) -> str:
        return "arg_1"


class Arg2(Instruction):
    def __str__(self) -> str:
        return "arg_2"


class Arg3(Instruction):
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

    def __str__(self) -> str:
        return f"pushbytes {self._bytes}"


class Len(Instruction):
    def __str__(self) -> str:
        return "len"


class Bytecblock(Instruction):
    def __str__(self) -> str:
        return "bytecblock"


class Substring(Instruction):
    def __init__(self, start: int, stop: int):
        super().__init__()
        self._start = int(start)
        self._stop = int(stop)

    def __str__(self) -> str:
        return f"substring {self._start} {self._stop}"


class Substring3(Instruction):
    def __str__(self) -> str:
        return "substring3"
