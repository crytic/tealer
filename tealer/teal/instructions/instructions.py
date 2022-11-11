"""Defines classes to represent teal instructions.

Each teal instruction is represented by a class specific to
that instruction. All instruction classes inherit ``Instruction``
class which defines common methods and properties of teal instructions.

Few teal instructions have immediate values which are defined and stored
as appropriate properties in the class representing that instruction.

Attributes:
    ContractType: ContractType is a comparable enumerator. it defines
        three symbols ``STATELESS``, ``STATEFULL``, ``ANY``.
        ``STATELESS`` represents stateless(signature) contracts,
        ``STATEFULL`` represents stateful(Application) contracts and
        ``ANY`` represents that contract is either ``STATELESS`` Or
        ``STATEFULL``. Exact meaning of the symbols depend on the place
        of usage.

    contract_type_to_txt: This is a mapping from ContractType symbol to
        their corresponding string representation. Useful while printing
        or outputting ContractType variable.

"""

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


contract_type_to_txt = {
    ContractType.STATEFULL: "stateful",
    ContractType.STATELESS: "stateless",
    ContractType.ANY: "any",
}


class Instruction:  # pylint: disable=too-many-instance-attributes
    """Base class for Teal instructions.

    Any class that represents a teal instruction must inherit from
    this class. This class is used for type hints anywhere a teal
    instruction is expected and this also comes with methods
    and properties common to every teal instruction.
    """

    def __init__(self) -> None:
        self._prev: List[Instruction] = []
        self._next: List[Instruction] = []
        self._line = 0
        self._comment = ""
        self._bb: Optional["BasicBlock"] = None
        self._version: int = 1
        self._mode: ContractType = ContractType.ANY
        self._callsub_ins: Optional["Instruction"] = None

    def add_prev(self, prev_ins: "Instruction") -> None:
        """Add instruction that may execute just before this instruction.

        An instruction is considered as a previous instruction if it's
        possible for that instruction to execute just before this instruction.
        Previous instruction doesn't necessarily have to be previous
        instruction in the source code, a branch instruction is also considered
        as previous instruction to the instruction present at it's destination.

        Args:
            prev_ins: instruction to add to the list of previous instructions
                of this instruction.
        """

        self._prev.append(prev_ins)

    def add_next(self, next_ins: "Instruction") -> None:
        """Add instruction that may execute right after this instruction.

        An instruction is considered as a next instruction if it's possible
        for that instruction to execute right after this instruction.
        Again, next instruction doesn't neccessarily have to present right
        after this instruction in the source code, destination of a branch
        instruction is also considered as a next instruction to the branch
        instruction.

        Args:
            next_ins: instruction to add to the list of next instructions
                of this instruction.
        """

        self._next.append(next_ins)

    @property
    def prev(self) -> List["Instruction"]:
        """List of previous instructions to this instruction."""
        return self._prev

    @property
    def next(self) -> List["Instruction"]:
        """List of next instructions to this instruction."""
        return self._next

    @property
    def line(self) -> int:
        """Source code line number of this instruction."""
        return self._line

    @line.setter
    def line(self, l: int) -> None:
        self._line = l

    @property
    def comment(self) -> str:
        """Teal comment present in the instruction line."""
        return self._comment

    @comment.setter
    def comment(self, c: str) -> None:
        self._comment = c

    @property
    def bb(self) -> Optional["BasicBlock"]:
        """Instance of BasicBlock this instruction is part of."""
        return self._bb

    @bb.setter
    def bb(self, b: "BasicBlock") -> None:
        self._bb = b

    @property
    def callsub_ins(self) -> Optional["Instruction"]:
        """if this instruction is a return point to a callsub instruction i.e callsub instruction is
        present right before this instruction, then callsub_ins returns a reference to that callsub
        instruction object.

        e.g
        callsub main
        int 1
        return

        callsub_ins of `int 1` will be instruction obj of `callsub main`.
        """
        return self._callsub_ins

    @callsub_ins.setter
    def callsub_ins(self, ins: "Instruction") -> None:
        self._callsub_ins = ins

    @property
    def version(self) -> int:
        """Teal version this instruction is introduced in and supported from."""
        return self._version

    @property
    def mode(self) -> ContractType:
        """Type of smart contract this instruction execution is supported in.

        Execution of every teal instruction is not supported in all types
        of smart contracts. There are instructions that will execute without
        failing only if the contract they are defined in is used as an application.
        Similarly, there are instructions that work only when contract is used
        as a signature(stateless). Remaining instructions execute correctly
        irrespective of the contract type. This property represents the contract
        type(mode) this instruction is supported in and executes properly.

        ``STATELESS`` contract type implies that this instruction will execute only
        in stateless(signature) contracts, ``STATEFULL`` implies that the instructions
        only work in application contracts and ``ANY`` represents that this instruction
        is supported in both kind of contracts.
        """

        return self._mode

    @property
    def cost(self) -> int:
        """cost of executing this instruction.

        Most of the opcodes in teal have cost of 1. By default, this property
        will return 1 independent of contract version. Instructions whose cost
        is not 1 or depends on contract version must override the cost property
        and return the correct cost.
        """

        return 1

    def __str__(self) -> str:
        return self.__class__.__qualname__.lower()


class UnsupportedInstruction(Instruction):
    """
    Instruction that is not supported by Tealer.

    The unsupported instruction will be printed in the CFG verbatim
    and specifically marked as UNSUPPORTED.
    """

    def __init__(self, verbatim_line: str):
        super().__init__()
        self._verbatim_line = verbatim_line

    def __str__(self) -> str:
        return f"UNSUPPORTED {self._verbatim_line}"

    @property
    def verbatim_line(self) -> str:
        """unsupported instruction as read from input"""
        return self._verbatim_line


class Pragma(Instruction):
    """Pragma version instruction to store version of the teal program.

    `#program version X` is used to specify the Teal version to the assembler and
    is present as the first line of the program. In absence of this instruction,
    Teal version 1 is used as default.

    Immediates:
        X (int): Teal version number.

    """

    def __init__(self, version: int):
        super().__init__()
        self._program_version = version

    def __str__(self) -> str:
        return f"#pragma version {self._program_version}"

    @property
    def program_version(self) -> int:
        """version number of teal program"""
        return self._program_version


class Err(Instruction):
    """`err` creates a error failing the execution of teal program immediately.

    Errors:
        This instruction creates a error resulting in failure of execution.
    """


class Assert(Instruction):
    """`assert` value on top of the stack is non-zero.

    Pops:
        X (top)(uint64): value being asserted

    Errors:
        creates error and fails immediately if X is not a non-zero number.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class Int(Instruction):
    """`int x` instruction pushes immediate value to the top of the stack.

    Immediates:
        x (Union[NamedIntegerConstant, uint64]): x can be an integer specified in one
            of the supported representations or x can be string representing one of
            the named integer constants. Named integer constants can be OnComplete
            constants "NoOp", "OptIn", "CloseOut", "ClearState", "UpdateApplication",
            "DeleteAplication" or else TYpeNum constants "unknown", "pay", "keyreg",
            "acfg", "axfer", "afrz", "appl".

    Pushes:
        (uint64): x if x is uint64 else value corresponding to the given named constant

    """

    def __init__(self, value: Union[str, int]):
        super().__init__()
        self._value = value

    @property
    def value(self) -> Union[str, int]:
        """Immediate value of int instruction."""
        return self._value

    def __str__(self) -> str:
        return f"int {self._value}"


class PushInt(Instruction):
    """`pushint x` instruction pushes immediate value to the top of the stack.

    pushint is similar to int instruction with the difference that immediate values of
    pushint are not treated as constants by the teal assembler whereas int instruction
    immediate values are stored into separate storage called constants and int instruction
    is replaced with instructions which load the value from the constant storage space.

    Immediates:
        x (Union[NamedIntegerConstant, uint64]): x can be an integer specified in one
            of the supported representations or x can be string representing one of
            the named integer constants. Named integer constants can be OnComplete
            constants "NoOp", "OptIn", "CloseOut", "ClearState", "UpdateApplication",
            "DeleteAplication" or else TYpeNum constants "unknown", "pay", "keyreg",
            "acfg", "axfer", "afrz", "appl".

    Pushes:
        (uint64): x if x is uint64 else value corresponding to the given named constant

    """

    def __init__(self, value: Union[str, int]):
        super().__init__()
        self._value = value
        self._version = 3

    @property
    def value(self) -> Union[str, int]:
        """Immediate value of pushint instruction."""
        return self._value

    def __str__(self) -> str:
        return f"pushint {self._value}"


class Txn(Instruction):
    """`txn f` pushes the value of transaction field f.

    Immediates:
        f (TransactionField): transaction field whose value is being accessed.
            see (transaction_field.py) for available transaction fields.

    Pushes:
        pushes the value of the transaction field `f`.

    """

    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field

    @property
    def field(self) -> TransactionField:
        """Transaction field being accessed using the txn instruction."""
        return self._field

    def __str__(self) -> str:
        return f"txn {self._field}"


class Txna(Instruction):
    """`txna f i` pushes ith value of array transaction field f.

    Few transaction fields namely "ApplicationArgs", "Accounts",
    "Applications", "Logs" are arrays and this instruction allows
    accesing their values by index.

    Immediates:
        f (TransactionField): Array transaction field whose value is being accessed.
        i (int): index into the array.

    Pushes:
        pushes value at index i of array transaction field f.

    """

    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 2

    @property
    def field(self) -> TransactionField:
        """Transaction field being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"txna {self._field}"


class Gtxn(Instruction):
    """`gtxn t f` pushes value of transaction field f of transaction t in the group.

    Immediates:
        t (int): index of the transaction in the group.
        f (TransactionField): transaction field whose value is being accessed.

    Pushes:
        push value of trasaction field f of transaction t.

    """

    def __init__(self, idx: int, field: TransactionField):
        super().__init__()
        self._idx = idx
        self._field: TransactionField = field

    @property
    def idx(self) -> int:
        """Index of the transaction in the atomic group"""
        return self._idx

    @property
    def field(self) -> TransactionField:
        """Transaction field of the instruction being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"gtxn {self._idx} {self._field}"


class Gtxna(Instruction):
    """`gtxna t f i` pushes ith value of array transaction field f of transaction t in the group.

    Few transaction fields namely "ApplicationArgs", "Accounts",
    "Applications", "Logs" are arrays and this instruction allows
    accesing their values by index.

    Immediates:
        t (int): index of the transaction in the group
        f (TransactionField): Array transaction field whose value is being accessed.
        i (int): index into the array.

    Pushes:
        pushes value at index i of array transaction field f of transaction t.

    """

    def __init__(self, idx: int, field: TransactionField):
        super().__init__()
        self._idx = idx
        self._field: TransactionField = field
        self._version: int = 2

    @property
    def idx(self) -> int:
        """Index of the transaction in the atomic group."""
        return self._idx

    @property
    def field(self) -> TransactionField:
        """Array transaction field being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"gtxna {self._idx} {self._field}"


class Gtxns(Instruction):
    """`gtxns f` pushes value of transaction field f of given transaction in the group.

    immediate:
        f (TransactionField): transaction field whose value is being accessed.

    Pops:
        t (top)(int): index of the transaction in the group.

    Pushes:
        push value of trasaction field f of transaction t.

    """

    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 3

    @property
    def field(self) -> TransactionField:
        """Transaction field being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"Gtxns {self._field}"


class Gtxnsa(Instruction):
    """`gtxnsa f i` pushes ith value of array transaction field f of given transaction in the group.

    immediate:
        f (TransactionField): transaction field whose value is being accessed.
        i (int): index into the array

    Pops:
        t (top)(int): index of the transaction in the group.

    Pushes:
        pushes value at index i of array transaction field f of transaction t.

    """

    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 3

    @property
    def field(self) -> TransactionField:
        """Array transaction field being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"Gtxnsa {self._field}"


class Load(Instruction):
    """`load i` pushes the value at scratch space position i.

    Immediates:
        i (int): position of scratch space to load the value from.

    Pushes:
        pushes the vaue at position i of scratch space.

    """

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self) -> str:
        return f"load {self._idx}"


class Store(Instruction):
    """`store i` store value on top of the stack at scratch space position i.

    Immediates:
        i (int): position of scratch space to store the value at.

    Pops:
        X (any): value to store in the scratch space.

    """

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self) -> str:
        return f"store {self._idx}"


class Gload(Instruction):
    """`gload t i` loads value at scratch space position i of transaction t.

    Immediates:
        t (int): index of the transaction in the group.
        i (int): position of the scratch space to load the value from.

    Pushes:
        pushes the value at position i of scratch space of transaction t.

    Errors:
        fails if transaction t is not a ApplicationCall and t < GroupIndex
        i.e if transaction is not executed before this transaction.

    """

    def __init__(self, idx: int, slot: int):
        super().__init__()
        self._idx = idx
        self._slot = slot
        self._version: int = 4
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return f"gload {self._idx} {self._slot}"


class Gloads(Instruction):
    """`gloads i` loads value at scratch space position i of transaction X.

    Immediates:
        i (int): position of the scratch space to load the value from.

    Pops:
        X (int): index of the transaction in the group.

    Pushes:
        pushes the value at position i of scratch space of transaction t.

    Errors:
        fails if transaction X is not a ApplicationCall and X < GroupIndex
        i.e if transaction is not executed before this transaction.

    """

    def __init__(self, slot: int):
        super().__init__()
        self._slot = slot
        self._version: int = 4
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return f"gloads {self._slot}"


class Gaid(Instruction):
    """`gaid t` pushes the id of asset or application created in transaction t in the group.

    Immediates:
        t (int): index of the transaction in the group.

    Pushes:
        pushes the id of the newly created asset in Tth transaction.

    Errors:
        fails if the Tth transaction did not create an asset or application.

    """

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 4
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return f"gaid {self._idx}"


class Gaids(Instruction):
    """`gaids` pushes the id of asset or application created in transaction X in the group.

    Pops:
        X (int): index of the transaction in the group.

    Pushes:
        pushes the id of the newly created asset in Xth transaction.

    Errors:
        fails if the Xth transaction of the group did not create an asset or application.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4
        self._mode: ContractType = ContractType.STATEFULL


class Loads(Instruction):
    """`loads` pushes the value at scratch space position X.

    Pops:
        X (top)(int): position of scratch space to load the value from.

    Pushes:
        pushes the vaue at position X of scratch space.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Stores(Instruction):
    """`stores` store value on top of the stack (B) at scratch space position (A).

    Pops:
        B (top)(any): value to store in the scratch space.
        A (int): position of scratch space to store the value at.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Dig(Instruction):
    """`dig n` pushes Nth value from the top of the stack.

    Pushes:
        pushes Nth value from the top of the stack.

    Errors:
        fails if n is greater than length of the stack.

    """

    def __init__(self, idx: int) -> None:
        super().__init__()
        self._idx = idx
        self._version: int = 3

    def __str__(self) -> str:
        return f"dig {self._idx}"


class Swap(Instruction):
    """`swap` swaps top two elements of the stack.

    Errors:
        fails if the length of the stack is less than 2.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class GetBit(Instruction):
    """`getbit` pushes the bit value of given element at given position.

    Bit ordering for uint64 is that index 0 is the least significant bit, whereas
    for byte arrays, index 0 is the leftmost bit of the leftmost byte.

    Pops:
        B (top)(int): bit position.
        A (any): element to get the Bth bit from.

    Pushes:
        pushes Bth bit of A.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class SetBit(Instruction):
    """`setbit` sets the bit value of given element to given value at given position.

    Bit ordering for uint64 is that index 0 is the least significant bit, whereas
    for byte arrays, index 0 is the leftmost bit of the leftmost byte.

    Pops:
        C (top)(int): bit value
        B (int): bit position.
        A (any): element to set the Bth bit of.

    Pushes:
        pushes the result after setting the bit.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class GetByte(Instruction):
    """`getbyte` pushes the byte value of given element at given position.

    Pops:
        B (top)(int): position of the byte.
        A (bytes): byte array to take the byte from.

    Pushes:
        pushes integer value of byte at Bth position of A.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class SetByte(Instruction):
    """`setbyte` sets the byte value of given element to given value at given position.

    Pops:
        C (top)(int): byte value
        B (int): byte position.
        A (any): byte array to set the byte at Bth position to C.

    Pushes:
        pushes the result after setting the byte C at Bth position.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class Extract(Instruction):
    """`extract s l` extracts the bytes from the given position s of given length l.

    Immediates:
        s (int): starting position of the substring.
        l (int): length of the the substring.

    Pops:
        A (top)([]byte): bytearray to get the bytes from.

    Pushes:
        pushes bytes of A from s upto s+l (A[s: s+l]).

    Errors:
        fails if s or s+l is greater than the length of A.

    """

    def __init__(self, idx: int, idy: int) -> None:
        super().__init__()
        self._idx = idx
        self._idy = idy
        self._version: int = 5

    @property
    def start_position(self) -> int:
        """Starting position of the substring in the bytearray."""
        return self._idx

    @property
    def length(self) -> int:
        """Length of the bytearray to extract."""
        return self._idy

    def __str__(self) -> str:
        return f"extract {self._idx} {self._idy}"


class Extract3(Instruction):
    """`extract3` extracts the bytes from the given position of given length.

    Pops:
        C (top)(int): length of the substring.
        B (int): starting position of the substring.
        A ([]byte): bytearray to get the bytes from.

    Pushes:
        pushes bytes of A from B upto B+C (A[B: B+C]).

    Errors:
        fails if B or B+C is greater than the length of A.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Extract_uint16(Instruction):
    """`extract_uint16` converts the two bytes at given position as uint16.

    Pops:
        B (top)(int): starting position of the two bytes.
        A ([]byte): bytearray to extract the uint16 from.

    Pushes:
        integer value of bytes at B as big endian.

    Errors:
        fails if B+2 is greater than the length of A.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Extract_uint32(Instruction):
    """`extract_uint32` converts the four bytes at given position as uint32.

    Pops:
        B (top)(int): starting position of the four bytes.
        A ([]byte): bytearray to extract the uint32 from.

    Pushes:
        integer value of bytes at B as big endian.

    Errors:
        fails if B+4 is greater than the length of A.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Extract_uint64(Instruction):
    """`extract_uint64` converts the eight bytes at given position as uint64.

    Pops:
        B (top)(int): starting position of the eight bytes.
        A ([]byte): bytearray to extract the uint64 from.

    Pushes:
        integer value of bytes at B as big endian.

    Errors:
        fails if B+8 is greater than the length of A.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5


class Sha256(Instruction):
    """`sha256` calculate the sha256 hash of the given element.

    Pops:
        X ([]byte): input to the sha256 hash function.

    Pushes:
        ([32]byte): pushes Sha256 hash of X.

    Changes:
        Teal v1: cost of sha256 is 7.
        Teal v2 onwards: cost of sha256 is 35.

    """

    @property
    def cost(self) -> int:
        """cost of executing sha256 instruction."""

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version == 1:
            return 7
        return 35


class Sha512_256(Instruction):
    """`sha512_256` calculate the sha512_256 hash of the given element.

    Pops:
        X ([]byte): input to the sha512_256 hash function.

    Pushes:
        ([32]byte): pushes Sha512_256 hash of X.

    Changes:
        Teal v1: cost of sha512_256 is 9.
        Teal v2 onwards: cost of sha512_256 is 45.

    """

    @property
    def cost(self) -> int:
        """cost of executing sha512_256 instruction."""

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version == 1:
            return 9
        return 45


class Keccak256(Instruction):
    """`keccak256` calculate the keccak256 hash of the given element.

    Pops:
        X ([]byte): input to the keccak256 hash function.

    Pushes:
        ([32]byte): pushes Keccak256 hash of X.

    Changes:
        Teal v1: cost of keccak256 is 26.
        Teal v2 onwards: cost of keccak256 is 130.

    """

    @property
    def cost(self) -> int:
        """cost of executing keccak256 instruction."""

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version == 1:
            return 26
        return 130


class Ed25519verify(Instruction):
    """`ed25519verify` verifies the ed25519 signature for given public key and data.

    this instructions verifies the signature for ("ProgData" || program_hash || data)
    where data is the given data against the given public key.

    Pops:
        C (top)([]byte): 32 byte public key.
        B ([]byte): 64 byte signature.
        A ([]byte): input data.

    Pushes:
        pushes 1 if the B is a valid signature of ("ProgData" || program_hash || A) against
        the public key C or else 0.

    """

    @property
    def cost(self) -> int:
        """cost of executing ed25519verify instruction."""
        return 1900


class Ecdsa_verify(Instruction):
    """`ecdsa_verify v` verify the given ecdsa signature for given data and public key.

    Immediates:
        v (NamedIntegerConstant): elliptic curve used for the signature and public key calculation.
            currently supports "Secp256k1" curve only.

    Pops:
        E (top)([]byte): Y-component of public key.
        D ([]byte): X-component of public key.
        C ([]byte): S component of ecdsa signature.
        B ([]byte): R component of ecdsa signature.
        A ([]byte): input data.

    Pushes:
        pushes 1 if signature (B, C) is valid signature for data A for public key (D, E) or else 0.

    Errors:
        fails if the signature is not in lower-S form. ecdsa signatures are malleable because (R, S)
        and (R, curve_order - S) are both valid signatures for the given data. To avoid that program
        accepts only one signature i.e with lower-S value.

    """

    def __init__(self, idx: str):
        super().__init__()
        self._idx = idx
        self._version: int = 5

    @property
    def cost(self) -> int:
        """cost of executing ecdsa_verify instruction.

        overrides cost property. ecdsa_verify instruction is introduced in
        Teal version 5. if the cost property is accessed for contracts with
        lesser version, value 0 is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 5:
            return 1700
        return 0

    def __str__(self) -> str:
        return f"ecdsa_verify {self._idx}"


class Ecdsa_pk_decompress(Instruction):
    """`ecdsa_pk_decompress v` decompress elliptic curve point to it's components.

    Immediates:
        v (NamedIntegerConstant): elliptic curve this point belongs to. currently
            supports "Secp256k1" curve only.

    Pops:
        A ([]byte): compressed representation of public key.

    Pushes:
        Y (top)([]byte): Y-component of public key.
        X ([]byte): X-component of public key.

    """

    def __init__(self, idx: str):
        super().__init__()
        self._idx = idx
        self._version: int = 5

    @property
    def cost(self) -> int:
        """cost of executing ecdsa_pk_decompress instruction.

        overrides cost property. ecdsa_pk_decompress instruction is introduced in
        Teal version 5. if the cost property is accessed for contracts with
        lesser version, value 0 is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 5:
            return 650
        return 0

    def __str__(self) -> str:
        return f"ecdsa_pk_decompress {self._idx}"


class Ecdsa_pk_recover(Instruction):
    """`ecdsa_pk_recover v` recovers the public key from signature, data and recovery id.

    Immediates:
        v (NamedIntegerConstant): elliptic curve this signature and point belongs to.
            currently supports "Secp256k1" curve only.

    Pops:
        D (top)([]byte): S component of the signature.
        C ([]byte): R component of the signature.
        B (int): recovery id. most likely number representing whether Y-component is odd or even.
        A ([]byte): data the signature is calculated on.

    Pushes:
        Y (top)([]byte): Y-component of the public key.
        X ([]byte): X-component of the public key.

    """

    def __init__(self, idx: str):
        super().__init__()
        self._idx = idx
        self._version: int = 5

    @property
    def cost(self) -> int:
        """cost of executing ecdsa_pk_recover instruction.

        overrides cost property. ecdsa_pk_recover instruction is introduced in
        Teal version 5. if the cost property is accessed for contracts with
        lesser version, value 0 is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 5:
            return 2000
        return 0

    def __str__(self) -> str:
        return f"ecdsa_pk_recover {self._idx}"


class Global(Instruction):
    """`global f` is used to access the value of global field f.

    Immediates:
        f (GlobalField): global field to get the value of.
            see global_field.py for all available global fields.

    Pushes:
        pushes the value of global field f.

    """

    def __init__(self, field: GlobalField):
        super().__init__()
        self._field: GlobalField = field

    @property
    def field(self) -> GlobalField:
        """Global field being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"global {self._field}"


class Dup(Instruction):
    """`dup` duplicates the top value on stack."""


class Dup2(Instruction):
    """`dup2` duplicates the top two values of the stack."""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class Select(Instruction):
    """`select` allows selecting one of two values based on another value.

    Pops:
        C (top)(int): value to check, base the condition on.
        B (any): value selected when C != 0.
        A (any): value selected when C == 0.

    Pushes:
        pushes B if C != 0 or else A.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3


class Cover(Instruction):
    """`cover n` allows moving top of the stack element to deeper into the stack.

    removes the element at the top of the stack and place it deeper in the stack such
    that n elements are above it.

    Immediates:
        n (int): depth or number of elements to push the top element to.

    Errors:
        fails if stack depth is less than to n.

    """

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 5

    def __str__(self) -> str:
        return f"cover {self._idx}"


class Uncover(Instruction):
    """`uncover n` allows moving element at given depth n to top of the stack.

    removes the element at depth n in the stack, shift above items down and place
    nth element on top of the stack

    Immediates:
        n (int): depth in stack to get the element from.

    Errors:
        fails if stack depth is less than or equal to n.

    """

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._version: int = 5

    def __str__(self) -> str:
        return f"uncover {self._idx}"


class Concat(Instruction):
    """`concat` concatenates two bytearrays and pushes the result.

    Pops:
        B (top)([]byte): second bytearray.
        A ([]byte): first bytearray.

    Pushes:
        pushes concatenated bytearray (A+B).

    Errors:
        fails if the result(A+B) has length greater than 4096 bytes.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class InstructionWithLabel(Instruction):
    """Base class to represent instructions which contain label"""

    def __init__(self, label: str):
        super().__init__()
        label = label.replace(" ", "")
        self._label = label

    @property
    def label(self) -> str:
        """String representing the label."""
        return self._label


class B(InstructionWithLabel):
    """`b target` represents a unconditional jump to target.

    Changes:
        Teal v2 to v3: can only branch forward skipping some code.
        Teal v4 onwards: can branch anywhere allowing loops.

    """

    def __init__(self, label: str):
        super().__init__(label)
        self._version: int = 2

    def __str__(self) -> str:
        return f"b {self._label}"


class BZ(InstructionWithLabel):
    """`bz target` branches to target if top of the stack is zero.

    Pops:
        X (top)(uint64): value to compare for the branch

    Changes:
        Teal v2 to v3: can only branch forward skipping some code.
        Teal v4 onwards: can branch anywhere allowing loops.

    """

    def __init__(self, label: str):
        super().__init__(label)
        self._version: int = 2

    def __str__(self) -> str:
        return f"bz {self._label}"


class BNZ(InstructionWithLabel):
    """`bnz target` branches to target if top of the stack is not zero.

    Pops:
        X (top)(uint64): value to compare for the branch

    Changes:
        Teal v1 to v3: can only branch forward skipping some code.
        Teal v4 onwards: can branch anywhere allowing loops.

    """

    def __str__(self) -> str:
        return f"bnz {self._label}"


class Label(InstructionWithLabel):
    """represents a simple label indicating start of the section or possible jump target"""

    def __str__(self) -> str:
        return f"{self._label}:"


class Callsub(InstructionWithLabel):
    """`callsub target` calls a subroutine target.

    callstack is different from data stack and only `callsub` and `retsub`
    manipulate it.
    """

    def __init__(self, label: str):
        super().__init__(label)
        self._return_point: Optional[Instruction] = None
        self._version: int = 4

    @property
    def return_point(self) -> Optional[Instruction]:
        """Return point of this call instruction.

        Execution returns to the next instruction of the call instruction
        after executing the called subroutine. This property returns instance
        of that instruction. This is helpful in construction of contract CFG and
        subroutine CFGs.
        """

        return self._return_point

    @return_point.setter
    def return_point(self, ins: Instruction) -> None:
        if self._return_point is not None:
            raise ValueError("Return point already set")
        self._return_point = ins

    def __str__(self) -> str:
        return f"callsub {self._label}"


class Return(Instruction):
    """`return` stops the execution and returns top of the stack as success value.

    Pops:
        X (uint64): success value.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class Retsub(Instruction):
    """`retsub` returns from a subroutine using the callstack"""

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class AppGlobalGet(Instruction):
    """`app_global_get` allows reading the global state of the current application.

    Pops:
        A ([]byte): global state key.

    Pushes:
        pushes the value of key A of the current application's global state. if the key
        does not exist, push zero(uint64).

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_global_get"


class AppGlobalGetEx(Instruction):
    """`app_global_get_ex` allows reading the global state of the any application.

    Pops:
        B (top)([]byte): global state key.
        A (uint64): value representing the application.

    Pushes:
        did_exist (top)(flag): 1 if the application existed or else 0.
        value (any): pushes the value of key B of the application A's global state. if the key
            does not exist, push zero(uint64).

    Changes:
        Till Teal v3: "A" value is a offset into ForeignApps transaction field.
        Teal v4 onwards: "A" can be application ID present in ForeignApps or CurrentApplication ID.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_global_get_ex"


class AppGlobalPut(Instruction):
    """`app_global_put` allows modifying the global state of the current application.

    write key A and value B to global state of the current application.

    Pops:
        B (top)(any): value to write.
        A ([]byte): global state key.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_global_put"


class AppGlobalDel(Instruction):
    """`app_global_del` allows deleting a key from global state of the current application.

    Delete key A from the global state of the application. Deleting a key which is already
    absent has no effect on the application global state. It does not cause the program to
    fail.

    Pops:
        A ([]byte): global state key.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_global_del"


class AppLocalGetEx(Instruction):
    """`app_local_get_ex` allows reading the local state of the an application for given account.

    Pops:
        C (top)([]byte): local state key.
        B (uint64): application to read the state of.
        A (any): account to read the local state from.

    Pushes:
        did_exist (top)(flag): 1 if the application existed or else 0.
        value (any): pushes the value of key C in the application B's local state
            of account A. if the key does not exist, push zero(uint64).

    Changes:
        Till Teal v3: "B" value is a offset into ForeignApps transaction field and "A" value is
            offset into Accounts transaction field
        Teal v4 onwards: "B" can be application ID present in ForeignApps or CurrentApplication ID
            and "A" value can be account address present in Accounts or Sender.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_local_get_ex"


class AppLocalGet(Instruction):
    """`app_local_get` allows reading the local state of the current application.

    Pops:
        B (top)([]byte): local state key.
        A (any): account to read the local state from.

    Pushes:
        pushes the value of key B of current application's local state of account A.
        if the key does not exist, push zero(uint64).

    Changes:
        Till Teal v3: "A" value is offset into Accounts transaction field
        Teal v4 onwards: "A" value can be account address present in Accounts or Sender.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_local_get"


class AppLocalPut(Instruction):
    """`app_local_put` allows modifying the local state of the current application.

    Update value of current application's local state with key B to new value C.

    Pops:
        C (top)(any): new value to write.
        B ([]byte): local state key.
        A (any): account to read the local state from.

    Changes:
        Till Teal v3: "A" value is offset into Accounts transaction field
        Teal v4 onwards: "A" value can be account address present in Accounts or Sender.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_local_put"


class AppLocalDel(Instruction):
    """`app_local_del` allows deleting a key from local state of the current application.

    Delete from account A local state key B of the current application.

    Pops:
        B (top)([]byte): local state key.
        A (any): account to delete the local state key from.

    Changes:
        Till Teal v3: "A" value is offset into Accounts transaction field
        Teal v4 onwards: "A" value can be account address present in Accounts or Sender.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_local_del"


class AssetHoldingGet(Instruction):
    """`asset_holding_get i` allows reading holding field of a given asset.

    Immediates:
        i (AssetHoldingField): field to get the value of.

    Pops:
        B (top)(uint64): asset to read the field from.
        A (any): account to read the asset holding field from.

    Pushes:
        did_exist (top)(flag): 1 if the asset existed or else 0.
        value (any): pushes the value of field asset B holding field i from account A.

    Changes:
        Till Teal v3: "B" value is a offset into ForeignAssets transaction field and "A" value is
            offset into Accounts transaction field
        Teal v4 onwards: "B" can be asset ID present in ForeignAssets and "A" value can be
            account address present in Accounts or Sender.

    """

    def __init__(self, field: AssetHoldingField):
        super().__init__()
        self._field: AssetHoldingField = field
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    @property
    def field(self) -> AssetHoldingField:
        """Asset holding field being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"asset_holding_get {self._field}"


class AssetParamsGet(Instruction):
    """`asset_params_get i` allows reading params field of a given asset.

    Immediates:
        i (AssetParamsField): field to get the value of.

    Pops:
        A (any): asset to read the field from.

    Pushes:
        did_exist (top)(flag): 1 if the asset existed or else 0.
        value (any): pushes the value of field asset A param field i.

    Changes:
        Till Teal v3: "A" value is a offset into ForeignAssets transaction field.
        Teal v4 onwards: "A" can be asset ID present in ForeignAssets.

    """

    def __init__(self, field: AssetParamsField):
        super().__init__()
        self._field: AssetParamsField = field
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    @property
    def field(self) -> AssetParamsField:
        """Asset Parameter field being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"asset_params_get {self._field}"


class AppParamsGet(Instruction):
    """`app_params_get i` allows reading param field of a given application.

    Immediates:
        i (AppParamsField): field to get the value of.

    Pops:
        A (any): application to read the field from.

    Pushes:
        did_exist (top)(flag): 1 if the application existed or else 0.
        value (any): pushes the value of field application A's param field i.

    Changes:
        Till Teal v3: "A" value is a offset into ForeignApps transaction field.
        Teal v4 onwards: "A" can be application ID present in ForeignApps.

    """

    def __init__(self, field: AppParamsField):
        super().__init__()
        self._field: AppParamsField = field
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL

    @property
    def field(self) -> AppParamsField:
        """Application parameter field being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"app_params_get {self._field}"


class AppOptedIn(Instruction):
    """`app_opted_in` allows contract to check if given account has opted-in or not.

    Pops:
        B (top)(uint64): value representing the application.
        A (any): value representing the account

    Pushes:
        pushes 1 if account A opted in for application B else 0.

    Changes:
        Till Teal v3: "B" value is a offset into ForeignApps transaction field and "A" value is
            offset into Accounts transaction field
        Teal v4 onwards: "B" can be application ID present in ForeignApps or CurrentApplication ID
            and "A" value can be account address present in Accounts or Sender.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "app_opted_in"


class Balance(Instruction):
    """`balance` reads the balance of an account in microalgos.

    Pops:
        A (any): account to read the balance of.

    Pushes:
        pushes the balance of account A in microalgos. The balance is
        observed after the effects of previous transactions in the group
        and after the fee for the current transaction is deducted.

    Changes:
        Till Teal v3: "A" value is offset into Accounts transaction field
        Teal v4 onwards: "A" value can be account address present in Accounts or Sender.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
        self._mode: ContractType = ContractType.STATEFULL


class MinBalance(Instruction):
    """`min_balance` pushes the minimum required balance for the given account.

    Pops:
        A (any): account to read the balance of.

    Pushes:
        pushes the minimum required balance of account A, in microalgos.

    Changes:
        Till Teal v3: "A" value is offset into Accounts transaction field
        Teal v4 onwards: "A" value can be account address present in Accounts or Sender.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 3
        self._mode: ContractType = ContractType.STATEFULL

    def __str__(self) -> str:
        return "min_balance"


class Itob(Instruction):
    """`itob` converts integer to big endian bytes.

    Pops:
        X (uint64): integer x to convert into bytes.

    Pushes:
        pushes big endian bytes of the given integer X.

    """


class Btoi(Instruction):
    """`btoi` converts bytes as big endian to uint64.

    Pops:
        X (uint64): bytes to convert.

    Pushes:
        pushes uint64 value after the conversion.

    """


class Addr(Instruction):
    """`addr X` pushes address X to top of the stack.

    Immediates:
        X ([]byte): address to push to the stack.

    Pushes:
        pushes the address X

    """

    def __init__(self, addr: str):
        super().__init__()
        self._addr = addr

    def __str__(self) -> str:
        return f"addr {self._addr}"


class Pop(Instruction):
    """`pop` pops one element from the stack."""


class Not(Instruction):
    """`!` not comparison operator.

    Pops:
        X (uint64): value to compare.

    Pushes:
        pushes 1 if X == 0 else 0

    """

    def __str__(self) -> str:
        return "!"


class Neq(Instruction):
    """`!=` not equal comparison operator.

    Pops:
        B (top)(any): second argument.
        A (any): first argument

    Pushes:
        pushes 1 if A is not equal to B else 0

    """

    def __str__(self) -> str:
        return "!="


class Eq(Instruction):
    """`==` equal to comparison operator.

    Pops:
        B (top)(any): second argument.
        A (any): first argument

    Pushes:
        pushes 1 if A is equal to B else 0

    """

    def __str__(self) -> str:
        return "=="


class Greater(Instruction):
    """`>` greater than comparison operator.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes 1 if A is greater than B else 0

    """

    def __str__(self) -> str:
        return ">"


class GreaterE(Instruction):
    """`>=` greater than or equal to comparison operator.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes 1 if A is greater than or equal to B else 0

    """

    def __str__(self) -> str:
        return ">="


class Less(Instruction):
    """`<` less than comparison operator.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes 1 if A is less than B else 0

    """

    def __str__(self) -> str:
        return "<"


class LessE(Instruction):
    """`<=` less than or equal to comparison operator.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes 1 if A is less than or equal to B else 0

    """

    def __str__(self) -> str:
        return "<="


class And(Instruction):
    """`&&` logical and.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes 1 if A is not zero and B is not zero else 0

    """

    def __str__(self) -> str:
        return "&&"


class Or(Instruction):
    """`||` logical and.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes 1 if A is not zero or B is not zero else 0

    """

    def __str__(self) -> str:
        return "||"


class Add(Instruction):
    """`+` arthimetic addition.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes A + B.

    Errors:
        fails on overflow and halts the execution failing the transaction.

    """

    def __str__(self) -> str:
        return "+"


class Sub(Instruction):
    """`-` arthimetic subtraction.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes A - B.

    Errors:
        fails if B > A.

    """

    def __str__(self) -> str:
        return "-"


class Mul(Instruction):
    """`*` arthimetic multiplication.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes A * B.

    Errors:
        fails on overflow and halts the execution failing the transaction.

    """

    def __str__(self) -> str:
        return "*"


class Div(Instruction):
    """`/` arthimetic divison.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes A divided by B (floor divison).

    Errors:
        fails if B == 0.

    """

    def __str__(self) -> str:
        return "/"


class Modulo(Instruction):
    """`%` arthimetic modulus.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes A modulo B.

    Errors:
        fails if B == 0.

    """

    def __str__(self) -> str:
        return "%"


class BitwiseOr(Instruction):
    """`|` bitwise or.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes A bitwise-or B.

    """

    def __str__(self) -> str:
        return "|"


class BitwiseAnd(Instruction):
    """`&` bitwise and.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes A bitwise-and B.

    """

    def __str__(self) -> str:
        return "&"


class BitwiseXor(Instruction):
    """`^` bitwise xor.

    Pops:
        B (top)(uint64): second argument.
        A (uint64): first argument

    Pushes:
        pushes A bitwise-xor B.

    """

    def __str__(self) -> str:
        return "^"


class BitwiseInvert(Instruction):
    """`~` bitwise invert.

    Pops:
        X (uint64): value to bitwise invert.

    Pushes:
        pushes value of bitwise invert of X.

    """

    def __str__(self) -> str:
        return "~"


class BitLen(Instruction):
    """`bitlen` calculates the bitlength of the given value.

    Pops:
        X (any): value to calculate the bitlength of.

    Pushes:
        pushes the bitlength of X. if X is a byte-array, then it is interpreted
        as big-endian unsigned integer.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class BModulo(Instruction):
    """`b%` arthimetic modulus.

    Pops:
        B (top)([]bytes): second argument which will be interpreted as
            big-endian unsigned integer.
        A ([]byte): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes byte representation of A modulo B.

    Errors:
        fails if B == 0.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    @property
    def cost(self) -> int:
        """cost of executing b% instruction.

        overrides cost property. b% instruction is introduced in Teal version 4.
        if the cost property is accessed for contracts with lesser version,
        value 0 is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 4:
            return 20
        return 0

    def __str__(self) -> str:
        return "b%"


class BNeq(Instruction):
    """`b!=` not equal comparison operator.

    Pops:
        B (top)(any): second argument which will be interpreted as
            big-endian unsigned integer.
        A (any): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes 1 if A is not equal to B else 0

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b!="


class BEq(Instruction):
    """`b==` equal to comparison operator.

    Pops:
        B (top)(any): second argument which will be interpreted as
            big-endian unsigned integer.
        A (any): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes 1 if A is equal to B else 0

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b=="


class BBitwiseAnd(Instruction):
    """`b&` bitwise and.

    Pops:
        B (top)([]byte): second argument which will be interpreted as
            big-endian unsigned integer.
        A ([]byte): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes byte representation of A bitwise-and B.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    @property
    def cost(self) -> int:
        """cost of executing b& instruction.

        overrides cost property. b& instruction is introduced in Teal version 4.
        if the cost property is accessed for contracts with lesser version,
        value 0 is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 4:
            return 6
        return 0

    def __str__(self) -> str:
        return "b&"


class BBitwiseOr(Instruction):
    """`b|` bitwise or.

    Pops:
        B (top)([]byte): second argument which will be interpreted as
            big-endian unsigned integer.
        A ([]byte): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes byte representation of A bitwise-or B.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    @property
    def cost(self) -> int:
        """cost of executing b| instruction.

        overrides cost property. b| instruction is introduced in Teal version 4.
        if the cost property is accessed for contracts with lesser version,
        value 0 is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 4:
            return 6
        return 0

    def __str__(self) -> str:
        return "b|"


class BAdd(Instruction):
    """`b+` arthimetic addition.

    Pops:
        B (top)([]byte): second argument which will be interpreted as
            big-endian unsigned integer.
        A ([]byte): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes byte representation of A + B.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    @property
    def cost(self) -> int:
        """cost of executing b+ instruction.

        overrides cost property. b+ instruction is introduced in Teal version 4.
        if the cost property is accessed for contracts with lesser version,
        value 0 is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 4:
            return 10
        return 0

    def __str__(self) -> str:
        return "b+"


class BSubtract(Instruction):
    """`b-` arthimetic subtraction.

    Pops:
        B (top)([]byte): second argument which will be interpreted as
            big-endian unsigned integer.
        A ([]byte): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes byte representation of A - B.

    Errors:
        fails if B > A.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    @property
    def cost(self) -> int:
        """cost of executing b- instruction.

        overrides cost property. b- instruction is introduced in Teal version 4.
        if the cost property is accessed for contracts with lesser version,
        value 0 is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 4:
            return 10
        return 0

    def __str__(self) -> str:
        return "b-"


class BDiv(Instruction):
    """`b/` arthimetic divison.

    Pops:
        B (top)([]byte): second argument which will be interpreted as
            big-endian unsigned integer.
        A ([]byte): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes byte representation of A divided by B (floor divison).

    Errors:
        fails if B == 0.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    @property
    def cost(self) -> int:
        """cost of executing b/ instruction.

        overrides cost property. b/ instruction is introduced in Teal version 4.
        if the cost property is accessed for contracts with lesser version,
        value 0 is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 4:
            return 20
        return 0

    def __str__(self) -> str:
        return "b/"


class BMul(Instruction):
    """`b*` arthimetic multiplication.

    Pops:
        B (top)([]byte): second argument which will be interpreted as
            big-endian unsigned integer.
        A ([]byte): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes byte representation of A * B.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    @property
    def cost(self) -> int:
        """cost of executing b* instruction.

        overrides cost property. b* instruction is introduced in Teal version 4.
        if the cost property is accessed for contracts with lesser version,
        value 0 is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 4:
            return 20
        return 0

    def __str__(self) -> str:
        return "b*"


class BGreaterE(Instruction):
    """`b>=` greater than or equal to comparison operator.

    Pops:
        B (top)([]byte): second argument which will be interpreted as
            big-endian unsigned integer.
        A ([]byte): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes 1 if A is greater than or equal to B else 0

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b>="


class BGreater(Instruction):
    """`b>` greater than comparison operator.

    Pops:
        B (top)([]byte): second argument which will be interpreted as
            big-endian unsigned integer.
        A ([]byte): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes 1 if A is greater than B else 0

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b>"


class BLessE(Instruction):
    """`b<=` less than or equal to comparison operator.

    Pops:
        B (top)([]byte): second argument which will be interpreted as
            big-endian unsigned integer.
        A ([]byte): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes 1 if A is less than or equal to B else 0

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b<="


class BLess(Instruction):
    """`b<` less than comparison operator.

    Pops:
        B (top)([]byte): second argument which will be interpreted as
            big-endian unsigned integer.
        A ([]byte): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes 1 if A is less than B else 0

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b<"


class BBitwiseXor(Instruction):
    """`b^` bitwise xor.

    Pops:
        B (top)([]byte): second argument which will be interpreted as
            big-endian unsigned integer.
        A ([]byte): first argument which will be interpreted as big-endian
            unsigned integer.

    Pushes:
        pushes byte representation of A bitwise-xor B.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    @property
    def cost(self) -> int:
        """cost of executing b^ instruction.

        overrides cost property. b^ instruction is introduced in Teal version 4.
        if the cost property is accessed for contracts with lesser version,
        value 0 is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 4:
            return 6
        return 0

    def __str__(self) -> str:
        return "b^"


class BBitwiseInvert(Instruction):
    """`b~` bitwise invert.

    Pops:
        X ([]byte): value to bitwise invert which will be interpreted as
            big-endian unsigned integer.

    Pushes:
        pushes byte representation of bitwise invert of X.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    def __str__(self) -> str:
        return "b~"

    @property
    def cost(self) -> int:
        """cost of executing b~ instruction.

        overrides cost property. b~ instruction is introduced in Teal version 4.
        if the cost property is accessed for contracts with lesser version,
        value 0 is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 4:
            return 4
        return 0


class BZero(Instruction):
    """`bzero` pushes byte array containing all zeroes.

    Pops:
        X (uint64): length of the bytearray.

    Pushes:
        byte array of length X containing all zeroes.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Log(Instruction):
    """`log` writes bytes to log state of the current application.

    Pops:
        X ([]byte): bytes to write to log state.

    Errors:
        fails if called more than MaxLogCalls(32) times in a program, or
        if sum of logged bytes exceeds 1024 bytes.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL


class Itxn_begin(Instruction):
    """`itxn_begin` signifies start of inner transaction.

    It initializes Sender to the application address, Fee to minimum allowable,
    taking into account MinTxnFee and credit from overpaying in earlier transactions.
    Sets FirstValid/LastValid to the values in the top-level transaction, and all other
    fields to zero values.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL


class Itxn_field(Instruction):
    """`itxn_field f` sets value of field f to top of the stack.

    Immediates:
        f (TransactionField): transaction field to set the value to.

    Pops:
        X (any): value of the field.

    Errors:
        Fails if X is of the wrong type for f or if length is wrong in case of
        byte arrays. In case X is account or asset, this instruction fails if
        X does not appear in txn.Accounts or txn.ForeignAssets of the top-level
        transaction.

    """

    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL

    @property
    def field(self) -> TransactionField:
        """Transaction field of inner transaction being set."""
        return self._field

    def __str__(self) -> str:
        return f"itxn_field {self._field}"


class Itxn_submit(Instruction):
    """`itxn_submit` executes the current inner transaction.

    This instruction resets the current transaction after executing
    so that it can not be resubmitted. A new `itxn_begin` is required
    to prepare another inner transaction.

    Errors:
        Fails if 16 inner transactions have already been executed.
        or fails if the inner transaction itself fails.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL


class Itxn(Instruction):
    """`itxn f` pushes the value of transaction field f of last inner transaction.

    Immediates:
        f (TransactionField): transaction field whose value is being accessed.
            see (transaction_field.py) for available transaction fields.

    Pushes:
        pushes the value of the transaction field `f`.

    """

    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL

    @property
    def field(self) -> TransactionField:
        """Transaction field being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"itxn {self._field}"


class Itxna(Instruction):
    """`itxna f i` pushes ith value of array transaction field f of last inner transaction.

    Few transaction fields namely "ApplicationArgs", "Accounts",
    "Applications", "Logs" are arrays and this instruction allows
    accesing their values by index.

    Immediates:
        f (TransactionField): Array transaction field whose value is being accessed.
        i (int): index into the array.

    Pushes:
        pushes value at index i of array transaction field f.

    """

    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 5
        self._mode: ContractType = ContractType.STATEFULL

    @property
    def field(self) -> TransactionField:
        """Array transaction field being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"itxna {self._field}"


class Txnas(Instruction):
    """`txnas f` pushes a value of array transaction field f using top of stack as index.

    Few transaction fields namely "ApplicationArgs", "Accounts",
    "Applications", "Logs" are arrays and this instruction allows
    accesing their values by index.

    Immediates:
        f (TransactionField): Array transaction field whose value is being accessed.

    Pops:
        X (int): index into the array.

    Pushes:
        pushes value at index X of array transaction field f.

    """

    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 5

    @property
    def field(self) -> TransactionField:
        """Array transaction field being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"txnas {self._field}"


class Gtxnas(Instruction):
    """`gtxnas t f` pushes a value of array transaction field f of transaction t in the group using top of the stack as index.

    Few transaction fields namely "ApplicationArgs", "Accounts",
    "Applications", "Logs" are arrays and this instruction allows
    accesing their values by index.

    Immediates:
        t (int): index of the transaction in the group
        f (TransactionField): Array transaction field whose value is being accessed.

    Pops:
        X (int): index into the array.

    Pushes:
        pushes value at index X of array transaction field f of transaction t.

    """

    def __init__(self, idx: int, field: TransactionField):
        super().__init__()
        self._idx: int = idx
        self._field: TransactionField = field
        self._version: int = 5

    @property
    def idx(self) -> int:
        """Index into array of array transaction field."""
        return self._idx

    @property
    def field(self) -> TransactionField:
        """Transaction field being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"Gtxnas {self._idx} {self._field}"


class Gtxnsas(Instruction):
    """`gtxnas f` pushes a value of array transaction field f of a transaction in the group.

    Few transaction fields namely "ApplicationArgs", "Accounts",
    "Applications", "Logs" are arrays and this instruction allows
    accesing their values by index.

    Immediates:
        f (TransactionField): Array transaction field whose value is being accessed.

    Pops:
        B (int): index into the array.
        A (int): index of the transaction in the group

    Pushes:
        pushes value at index B of array transaction field f of transaction A.

    """

    def __init__(self, field: TransactionField):
        super().__init__()
        self._field: TransactionField = field
        self._version: int = 5

    @property
    def field(self) -> TransactionField:
        """Transaction field being accessed."""
        return self._field

    def __str__(self) -> str:
        return f"gtxnsas {self._field}"


class Args(Instruction):
    """`args` pushes a LogicSig argument to stack using top of stack as index.

    Pops:
        X (uint64): index into LogicSig array argument.

    Pushes:
        pushes Xth LogicSig argument to stack.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 5
        self._mode: ContractType = ContractType.STATELESS


class Mulw(Instruction):
    """`mulw` multiplies two unit64 and pushes 128-bit long result.

    Pops:
        B (top)(uint64): second argument of multiplication.
        A (uint64): first argument of multiplication.

    Pushes:
        low (top)(uint64): value of lower 64 bits of the result.
        high (uint64): value of high 64 bits of result.

    """


class Addw(Instruction):
    """`addw` adds two unit64 and pushes out to 128-bit long result.

    Pops:
        B (top)(uint64): second argument of addition.
        A (uint64): first argument of addition.

    Pushes:
        low (top)(uint64): value of lower 64 bits of the result.
        high (uint64): value of high 64 bits of result.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2


class Divmodw(Instruction):
    """`divmodw` allows dividing two 128-bit numbers.

    Pops:
        D (top)(uint64): lower 64 bits of 128-bit divisor.
        C (uint64): high 64 bits of 128-bit divisor.
        B (uint64): lower 64 bits of 128-bit dividend.
        A (uint64): high 64 bits of 128-bit dividend.

    Pushes:
        remainder_low (top)(unit64): lower 64 bits of remainder.
        remainder_high (uint64): high 64 bits of remainder.
        quotient_low (uint64): lower 64 bits of quotient.
        quotient_high (uint64): high 64 bits of quotient.

    Errors:
        fails if divisor is zero.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    @property
    def cost(self) -> int:
        """cost of executing divmodw instruction.

        overrides cost property. divmodw instruction is introduced in Teal version 4.
        if the cost property is accessed for contracts with lesser version, value 0
        is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 4:
            return 20
        return 0


class Exp(Instruction):
    """`exp` allows calculating powers of a number.

    Pops:
        B (top)(uint64): exponent to raise the base to.
        A (uint64): base.

    Pushes:
        pushes A raised to the Bth power.

    Errors:
        fails if A == B == 0 or if A**B overflows.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Expw(Instruction):
    """`expw` allows calculating powers of a number with more space for the result.

    Pops:
        B (top)(uint64): exponent to raise the base to.
        A (uint64): base.

    Pushes:
        low (top)(uint64): lower 64 bits of A**B.
        high (uint64): high 64 bits of A**B

    Errors:
        fails if A == B == 0 or if A**B > 2**128 - 1.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    @property
    def cost(self) -> int:
        """cost of executing expw instruction.

        overrides cost property. expw instruction is introduced in Teal version 4.
        if the cost property is accessed for contracts with lesser version, value 0
        is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 4:
            return 10
        return 0


class Shl(Instruction):
    """`shl` shifts left the given element by given bits.

    Pops:
        B (top)(uint64): number of bits to shift.
        A (uint64): number to shift.

    Pushes:
        pushes A * 2**B modulo 2**64

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Shr(Instruction):
    """`shl` shifts right the given element by given bits.

    Pops:
        B (top)(uint64): number of bits to shift.
        A (uint64): number to shift.

    Pushes:
        pushes A divided by 2**B.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4


class Sqrt(Instruction):
    """`sqrt` calculates the integer square root of given number.

    Pops:
        X (uint64): number to calculate the square root of.

    Pushes:
        pushes the largest integer B such that B^2 <= X.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 4

    @property
    def cost(self) -> int:
        """cost of executing sqrt instruction.

        overrides cost property. sqrt instruction is introduced in Teal version 4.
        if the cost property is accessed for contracts with lesser version, value 0
        is returned instead of raising an error.
        """

        if self.bb and self.bb.teal:
            contract_version = self.bb.teal.version
        else:
            raise ValueError(
                "instruction cost is accessed without setting basic block or teal instance."
            )

        if contract_version >= 4:
            return 4
        return 0


class Intcblock(Instruction):
    """`intcblock x ...` resets and replaces integer constants in constant storage space.

    Immediates:
        x ... ([]uint64): numbers to store in constant storage space which
            can be referenced later by `intc` and `intc_*` instructions.

    """

    def __init__(self, int_list: List[int]):
        super().__init__()
        self._constants = int_list

    def __str__(self) -> str:
        return " ".join(["intcblock"] + list(map(str, self._constants)))


class Intc(Instruction):
    """`intc i` push integer constant loaded from constant storage space.

    Immediates:
        i (uint8): index into the integer constants array.

    Pushes:
        push Ith constant from intcblock to stack.

    """

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self) -> str:
        return f"intc {self._idx}"


class Intc0(Instruction):
    """`intc_0` push integer constant 0 from constant storage space.

    Pushes:
        push constant 0 from intcblock to stack.

    """

    def __str__(self) -> str:
        return "intc_0"


class Intc1(Instruction):
    """`intc_1` push integer constant 1 from constant storage space.

    Pushes:
        push constant 1 from intcblock to stack.

    """

    def __str__(self) -> str:
        return "intc_1"


class Intc2(Instruction):
    """`intc_2` push integer constant 2 from constant storage space.

    Pushes:
        push constant 2 from intcblock to stack.

    """

    def __str__(self) -> str:
        return "intc_2"


class Intc3(Instruction):
    """`intc_3` push integer constant 3 from constant storage space.

    Pushes:
        push constant 3 from intcblock to stack.

    """

    def __str__(self) -> str:
        return "intc_3"


class Bytec(Instruction):
    """`bytec i` push byte constant loaded from constant storage space.

    Immediates:
        i (uint8): index into the byte constants array.

    Pushes:
        push Ith constant from bytecblock to stack.

    """

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx

    def __str__(self) -> str:
        return f"bytec {self._idx}"


class Bytec0(Instruction):
    """`bytec_0` push byte constant 0 from constant storage space.

    Pushes:
        push constant 0 from bytecblock to stack.

    """

    def __str__(self) -> str:
        return "bytec_0"


class Bytec1(Instruction):
    """`bytec_1` push byte constant 1 from constant storage space.

    Pushes:
        push constant 1 from bytecblock to stack.

    """

    def __str__(self) -> str:
        return "bytec_1"


class Bytec2(Instruction):
    """`bytec_2` push byte constant 2 from constant storage space.

    Pushes:
        push constant 2 from bytecblock to stack.

    """

    def __str__(self) -> str:
        return "bytec_2"


class Bytec3(Instruction):
    """`bytec_3` push byte constant 3 from constant storage space.

    Pushes:
        push constant 3 from bytecblock to stack.

    """

    def __str__(self) -> str:
        return "bytec_3"


class Arg(Instruction):
    """`arg n` pushes n LogicSig argument to stack.

    Immediates:
        n (uint8): index into LogicSig arguments array.

    Pushes:
        pushes Nth LogicSig argument to stack.

    """

    def __init__(self, idx: int):
        super().__init__()
        self._idx = idx
        self._mode: ContractType = ContractType.STATELESS

    def __str__(self) -> str:
        return f"arg {self._idx}"


class Arg0(Instruction):
    """`arg_0` pushes 0th LogicSig argument to stack.

    Pushes:
        pushes LogicSig argument 0 to stack.

    """

    def __init__(self) -> None:
        super().__init__()
        self._mode: ContractType = ContractType.STATELESS

    def __str__(self) -> str:
        return "arg_0"


class Arg1(Instruction):
    """`arg_1` pushes 1st LogicSig argument to stack.

    Pushes:
        pushes LogicSig argument 1 to stack.

    """

    def __init__(self) -> None:
        super().__init__()
        self._mode: ContractType = ContractType.STATELESS

    def __str__(self) -> str:
        return "arg_1"


class Arg2(Instruction):
    """`arg_2` pushes 2nd LogicSig argument to stack.

    Pushes:
        pushes LogicSig argument 2 to stack.

    """

    def __init__(self) -> None:
        super().__init__()
        self._mode: ContractType = ContractType.STATELESS

    def __str__(self) -> str:
        return "arg_2"


class Arg3(Instruction):
    """`arg_3` pushes 3rd LogicSig argument to stack.

    Pushes:
        pushes LogicSig argument 3 to stack.

    """

    def __init__(self) -> None:
        super().__init__()
        self._mode: ContractType = ContractType.STATELESS

    def __str__(self) -> str:
        return "arg_3"


class Byte(Instruction):
    """`byte x` instruction pushes immediate value to the top of the stack.

    Immediates:
        x ([]byte): x is bytes to push represented in one of the supported formats.
            namely, base64 AAAA..., b64 AAAA..., base64(AAAA...), b64(AAAA...),
            base32 AAAA..., b32 AAAA..., base32(AAAA...), b32(AAAA...),
            0x0123..., "literal".

    Pushes:
        ([]byte): decoded byte value.

    """

    def __init__(self, bytesb: str):
        super().__init__()
        self._bytes = bytesb

    def __str__(self) -> str:
        return f"byte {self._bytes}"


class PushBytes(Instruction):
    """`pushbytes x` instruction pushes immediate value to the top of the stack.

    pushbytes is similar to byte instruction with the difference that immediate values of
    pushbytes are not treated as constants by the teal assembler whereas byte instruction
    immediate values are stored into separate storage called constants and byte instruction
    is replaced with instructions which load the value from the constant storage space.

    Immediates:
        x ([]byte): x is bytes to push represented in one of the supported formats.
            namely, base64 AAAA..., b64 AAAA..., base64(AAAA...), b64(AAAA...),
            base32 AAAA..., b32 AAAA..., base32(AAAA...), b32(AAAA...),
            0x0123..., "literal".

    Pushes:
        ([]byte): decoded byte value.

    """

    def __init__(self, bytesb: str):
        super().__init__()
        self._bytes = bytesb
        self._version: int = 3

    def __str__(self) -> str:
        return f"pushbytes {self._bytes}"


class Len(Instruction):
    """`len` calculates the length of the given byte array.

    Pops:
        X ([]byte): byte array to find the length of.

    Pushes:
        (uint64): pushes the length of the byte array X.

    """


class Bytecblock(Instruction):
    """`bytecblock x ...` resets and replaces byte constants in constant storage space.

    Immediates:
        x ... ([][]byte): bytes to store in constant storage space which
            can be referenced later by `bytec` and `bytec_*` instructions.

    """

    def __init__(self, bytes_list: List[str]):
        super().__init__()
        self._constants = bytes_list

    def __str__(self) -> str:
        return " ".join(["bytecblock"] + self._constants)


class Substring(Instruction):
    """`substring s e` extracts the bytes from the given position s to e.

    Immediates:
        s (uint8): starting position of the substring.
        e (uint8): ending position of the substring.

    Pops:
        A ([]byte): byte array to take the substring from.

    Pushes:
        pushes range of bytes from A starting from S up to but not including
        E.(A[s: e])

    Errors:
        fails if e < s and if e or s is larger than the array length.

    """

    def __init__(self, start: int, stop: int):
        super().__init__()
        self._start = start
        self._stop = stop
        self._version: int = 2

    def __str__(self) -> str:
        return f"substring {self._start} {self._stop}"


class Substring3(Instruction):
    """`substring3` extracts the bytes from the given range.

    Immediates:

    Pops:
        C (top)(uint64): ending position of the substring.
        B (uint64): starting position of the substring.
        A ([]byte): byte array to take the substring from.

    Pushes:
        pushes range of bytes from A starting from B up to but not including C.(A[B: C])

    Errors:
        fails if C < B and if B or C is larger than the array length.

    """

    def __init__(self) -> None:
        super().__init__()
        self._version: int = 2
