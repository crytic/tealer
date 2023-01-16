"""
TODO: Move below information to appropriate location

Literal value instructions:

- Instructions which push literal values onto the stack.
- Literal values are part of the compiled program and can be calculated using static analysis.

    intcblock, intc, intc_0, intc_1, intc_2, intc_3
    int, pushint, pushints

    bytecblock, bytec, bytec_0, bytec_1, bytec_2, bytec_3
    addr, method, bytes, pushbytes, pushbytess

    global ZeroAddress

- pushints, pushbytess push multiple literal values on to the stack.


Transaction Information:
    Block producer controlled:
        arg, arg_0, arg_1, arg_2, arg_3, args,

    Transaction signer controlled:
        txn f, gtxn t f, txna f i, gtxna t f i, gtxns f, gtxnsa f i,
        txnas f, gtxnas t f, gtxnsas f

    Information global to all transactions in the group or in the chain:
        global f

    Application/Asset Ids created by previous transactions in the group:
        gaid t, gaids,


Application state manipulation:
- Instructions to access/manipulate current application's persistent state.

    Global and Local state:
        app_global_get, app_global_put, app_global_del,
        app_local_get, app_local_put, app_local_del,

    App Boxes:
        box_create, box_put, box_del, box_replace,
        box_len, box_get, box_extract


External state information:
- Instructions to access information of external apps, assets and accounts

    app_opted_in, app_local_get_ex, app_global_get_ex, app_params_get,      # apps
    asset_holding_get, asset_params_get,                                    # assets
    balance, min_balance, acct_params_get,                                  # accounts


Block Information:
    block f


Inner transactions(Calls):
    Instructions to create a inner transaction:
        itxn_begin, itxn_field, itxn_next, itxn_submit,

    Instructions to access information of recently submitted inner transaction:
        itxn f, itxna f i, gitxn t f, gitxna t f i, itxnas f, gitxnas t f,


Stack Manipulation Opcodes:

- Instructions which change the order of elements in the stack independent of the actual values of the elements.
- could be emulated during stack emulation

    bury n, popn n, dupn n, pop, dup,
    dup2, dig n, swap, cover n, uncover n,

    select, # select depends on the runtime information


Scratch Space:
    Instructions to manipulate scratch space:
        load, store, loads, stores,

    Instructions to access scratch space of previous transactions in the group:
        gload t i, gloads i, gloadss


Control Flow:
    (Might) Stop the execution:
        err, return, assert,

    Branch, Jump around the code:
        b target
        bnz target, bz target, switch, match,

        callsub, retsub,


Arthimetic Operations:
    +, -, /, *, %, sqrt, exp, shl, shr,
    addw, mulw, divw, divmodw, expw,        # wide math
    b+, b-, b/, b*, b%, bsqrt,              # byte (512-bits)


Bitwise Operations:
    |, &, ^, ~,
    b|, b&, b^, b~,         # byte (512-bits)


Connectors:
    &&
    ||

Comparison
    <, >, <=, >=, ==, !=, !
    b<, b>, b<=, b>=, b==, b!=


Int/Byte Manipulation:
    bzero,
    concat,
    len, bitlen,
    itob, btoi,
    getbit, setbit, getbyte, setbyte,
    substring s e, substring3,
    extract, extract3, extract_uint16, extract_uint32, extract_uint64,
    replace2, replace3,
    base64_decode, json_ref,


Cryptographic/Hash:
    sha256, keccak256, sha512_256, sha3_256,
    ed25519verify, ed25519verify_bare,
    ecdsa_verify, ecdsa_pk_decompress, ecdsa_pk_recover
    vrf_verify,


Logging Operations:
    log


Unclear/recent(v8) instructions:
    proto, frame_dig, frame_bury,
"""

from typing import List, Union, Dict

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import (
    Instruction,
)


class UnknownStackValue:
    """Represent a unknown stack value."""

    def __str__(self) -> str:
        return "UnknownStackValue()"

    def __repr__(self) -> str:
        return "UnknownStackValue()"


class KnownStackValue:
    """Represent values which are known during the local stack emulation.

    A stack value is represented using the instruction, arguments and the position.

    instruction: Every stack value is a result of executing a instruction. instruction
        property contains the reference to that instruction's object.
    args: A instruction consumes values from the stack. `args` represents the list of stack values
        which are consumed by `self.instruction` to produce the result(s).
    position: A instruction might produce multiple values. position represents the index in the list
        of produced values.

    e.g

    int 10
    int 11
    mulw

    values pushed by each instruction are:
        "int 10" -> KnownStackValue(ins = Int(10), args = [])
        "int 11" -> KnownStackValue(ins = Int(11), args = [])
        "mulw" ->
            KnownStackValue(
                ins = Mulw(),
                args = [Int(10), Int(11)],
                position = 0,
            ),
            KnownStackValue(
                ins = Mulw(),
                args = [Int(10), Int(11)],
                position = 1,
            )

        Value which is pushed first will have position 0.
    """

    def __init__(self, ins: Instruction, args: List, position: int = 0) -> None:
        self._ins = ins
        self._args: List[Union[KnownStackValue, UnknownStackValue]] = args
        self._position = position

    @property
    def instruction(self) -> Instruction:
        return self._ins

    @property
    def args(self) -> List[Union["KnownStackValue", UnknownStackValue]]:
        """List of stack values consumed by self.instruction.

        self.args[0] is the last popped(first pushed) value from the stack.
        self.args[-1] is the first popped value from the stack:
            self.args[-1] is on top of the stack right before the execution
            of self.instruction.
        """
        return self._args

    @property
    def position(self) -> int:
        return self._position

    def __str__(self) -> str:
        # args = ", ".join(str(i) for i in self._args)
        # return f"{self._ins.__class__.__name__}(<{args}>)"
        args = "[" + ", ".join(str(i) for i in self.args) + "]"
        return f"KnownStackValue(ins = {str(self._ins.__class__.__name__)}, args = {args})"

    def __repr__(self) -> str:
        return str(self)


StackValue = Union[KnownStackValue, UnknownStackValue]


class Stack:
    """Represent a stack.

    Elements are stored in a list. Top of the stack is at the end of the List.

    Stack is assumed to have infinite UnknownStackValue below the current pointer.
    """

    def __init__(self) -> None:
        self._values: List[StackValue] = []

    def push(self, value: StackValue) -> None:
        self._values.append(value)

    def pop(self, count: int) -> List[StackValue]:
        """Pop elements from the stack.

        Args:
            count: Number of elements to pop.

        Returns:
            list of popped values. First popped value is at the end of the list.
        """
        if count == 0:
            return []
        if len(self._values) >= count:
            vals = self._values[-count:]
            self._values = self._values[:-count]
            return vals
        remaining_elements: List[StackValue] = [
            UnknownStackValue() for _ in range(count - len(self._values))
        ]
        vals = remaining_elements + self._values
        self._values = []
        return vals

    def __str__(self) -> str:
        return "[" + ",".join([str(value) for value in self._values]) + "]"

    def __repr__(self) -> str:
        return str(self)


def emulate_stack(bb: BasicBlock) -> Dict[Instruction, KnownStackValue]:
    r"""Emulates instructions in the basic block and return values produced by each instruction.

    Because we do not know the values of the stack before executing this basic block, stack is assumed
    to have infinite number of UnknownStackValue(s).

    For each instruction in the basic block, this function calculates the AST consisting of instructions.

    int 1
    int 2
    ==              // <1>
    addr "..."
    txn RekeyTo
    !=              // <2>
    &&
    byte "X"
    byte "Y"
    ==              // <3>
    &&

    Tree:
                        And
                      /     \\
                    And       Eq     <- <3>
                  /    \    /     \\
        <1> ->  Eq     Neq  Byte   Byte
              /   \   /   \\
            Int  Int Addr  Txn RekeyTo

    int 1
    &&
    assert
    Returned dict:
        {
            Int(1): KnownStackValue(ins = Int(1), args = []),
            And(): KnownStackValue(
                    ins = And(),
                    args = [
                    UnknownStackValue,
                    KnownStackValue(ins = Int(1), args = []),
                ]),
            Assert(): KnownStackValue(
                    ins = Assert(),
                    args = [
                        KnownStackValue(
                            ins = And(),
                            args = [
                            UnknownStackValue,
                            KnownStackValue(ins = Int(1), args = []),
                        ]),
                ]),
        }
    """
    stack = Stack()
    ins_stack_value = {}
    for ins in bb.instructions:
        # TODO: emulate other stack manipulating instructions if necessary:
        #   swap, dup, dup2, dupn n, bury n, dig n, cover n, uncover n,
        popped_values = stack.pop(ins.stack_pop_size)
        for i in range(ins.stack_push_size):
            stack.push(KnownStackValue(ins, popped_values, i))
        ins_stack_value[ins] = KnownStackValue(ins, popped_values)
    return ins_stack_value
