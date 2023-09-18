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

from typing import List, Union, Dict, Type, Tuple
from functools import lru_cache


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
    ins_out_values_index: ins_out_values_index stores the index inside the list of instruction
    out values. When a instruction pushes multiple out values, every out value will have same
    `instruction` and `args`. ins_out_values_index allows representing out values uniquely.


    e.g

    int 10
    int 11
    mulw

    Stack:

        |               |
         ---------------
        |               |
         ---------------

    `int 10` -> pops 0 values and pushes 1 value

        |               |
         ---------------
        |  A = Int(10)  |
         ---------------

    `int 11` -> pops 0 values and pushes 1 value

        |               |
         ---------------
        |  B = Int(11)  |
         ---------------
        |  A = Int(10)  |
         ---------------

    mulw -> pops 2 values and pushes 2 values.

        |               |
         ---------------
        |       Y       |
         ---------------
        |       X       |
         ---------------

    A = KnownStackValue(ins = Int(10), args = [], ins_out_values_index = 0)
    B = KnownStackValue(ins = Int(11), args = [], ins_out_values_index = 0)

    mulw pops `a` and `b` and pushes `X` and `Y`.
    mulw_out_values = mulw(a, b)
    X = mulw_out_values[0]
    Y = mulw_out_values[1]

    X == KnownStackValue(ins = Mulw(), args = [A, B], ins_out_values_index = 0)
    Y == KnownStackValue(ins = Mulw(), args = [A, B], ins_out_values_index = 1)
    """

    def __init__(self, ins: Instruction, args: List, ins_out_values_index: int = 0) -> None:
        self._ins = ins
        self._args: List[Union[KnownStackValue, UnknownStackValue]] = args
        self._ins_out_values_index = ins_out_values_index

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

        Returns:
            Arguments of the current instruction that are taken from the stack.
        """
        return self._args

    @property
    def ins_out_values_index(self) -> int:
        """index into the list of out values pushed by self.instruction.

        An instruction can push multiple stack values. In order to differentiate
        between multiple values generated by the execution of the same instruction,
        the ins_out_values_index is used.

        The stack values pushed first by the instruction will have index 0. The stack value
        pushed next will have index 1 and so on.

        stack:
                 ---- ----
                |    |
                 ---- ----
        int 10
                 ---- ----
                | 10 |
                 ---- ----
        int 11
                 ---- ---- ----
                | 10 | 11 |
                 ---- ---- ----
        mulw
                 ---- ---- ----
                |  X |  Y |
                 ---- ---- ----

        (X, Y) = mulw(10, 11)

        mulw_in_values = Int(10), Int(11)
        mulw_out_values = [X, Y]

        X.ins_out_values_index == 0
        Y.ins_out_values_index == 1

        X.instruction == Y.instruction == Mulw()
        X.args == Y.args = [Int(10), Int(11)]

        Returns:
            index of this value in the list of output values of self.instruction.
        """
        return self._ins_out_values_index

    def __str__(self) -> str:
        # args = ", ".join(str(i) for i in self._args)
        # return f"{self._ins.__class__.__name__}(<{args}>)"
        args = "[" + ", ".join(str(i) for i in self.args) + "]"
        # return f"KnownStackValue(ins = {str(self._ins.__class__.__name__)}, args = {args})"
        return f"KnownStackValue(ins = {repr(self._ins)}, args = {args})"

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

    def push_n_values(self, values: List[StackValue]) -> None:
        self._values.extend(values)

    def pop_n_values(self, count: int) -> List[StackValue]:
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


@lru_cache(maxsize=None)
def construct_stack_ast(bb: BasicBlock) -> Dict[Instruction, KnownStackValue]:
    r"""Emulates instructions in the basic block and return values(AST) produced by each instruction.

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

    Args:
        bb: A basic block of the CFG.

    Returns:
        A dict with each instruction of the bb as key. The values are the stack value representation
        of that instruction. The value should be used to access the inputs of the instruction. These
        inputs only includes stack arguments not the immediate arguments.
    """
    stack = Stack()
    ins_stack_value = {}
    for ins in bb.instructions:
        # TODO: emulate other stack manipulating instructions if necessary:
        #   swap, dup, dup2, dupn n, bury n, dig n, cover n, uncover n,
        # - Replace int like instructions with int values. Same for byte like instructions
        # - Only track necessary instructions values.
        ins_in_values = stack.pop_n_values(ins.stack_pop_size)  # pops `pop_size` number of values
        ins_out_values: List[StackValue] = []
        for i in range(ins.stack_push_size):
            ins_out_values.append(KnownStackValue(ins, ins_in_values, i))
        stack.push_n_values(ins_out_values)

        # store the instruction reference and its arguments(input values).
        # we only care about the instruction input values for now.
        ins_stack_value[ins] = KnownStackValue(ins, ins_in_values)
    return ins_stack_value


def _flatten_ast(root: StackValue, node_ins: Type[Instruction]) -> List[StackValue]:
    r"""Return all the leaf values given the root of the instruction AST.

    node_ins instruction is one of `And`, `Or`.
    `And` and `Or` consume two values. These two values are the children of the node.

    Inner nodes are values whose `instruction` is a instance of `node_ins`.
    Leaf values are values whose `instruction` is not `node_ins`.

      &&
    /    \
   ==     &&
        /    \
       &&     ||
      /  \   /  \
     ==  >  !   !=
    /\   /\

    All the nodes in the tree are represented by `StackValue`. A StackValue can be unknown or known.
    unknown stack values are considered to be leaf values and are stored.
    A known stack value contains the instruction and arguments consumed by that instruction. These
    arguments are also stack values and are treated as children.

    In above example, if `node_ins` is `And` then values with instruction, `==, >, ||`, are all treated
    as leaf blocks and are NOT traversed further.

    int 1
    int 2
    ==
    addr "..."
    txn RekeyTo
    !=
    &&
    byte "X"
    byte "Y"
    ==
    &&

    Tree:
                        And
                      /     \
                    And       Eq
                  /    \    /     \
                Eq     Neq  Byte   Byte
              /   \   /    \
            Int  Int Addr  Txn RekeyTo

    node_ins = And

    ^^Only And instruction values are considered as nodes. remaining values are treated as leaves
    and are not traversed.

    After traversing, this functions returns the leaf values:
        [
            Eq(Int(<>), Int(<>)),
            Neq(Addr(<>), Txn(<>)),
            Eq(Byte(<>), Byte(<>))
        ]

    This function essentially flattens the given tree:
        And(And(<1>, <2>), And(And(<3>, <4>), And(<5>, <6>)))
        node_ins = And
        => returns [<1>, <2>, <3>, <4>, <5>, <6>]

        Or(Or(Or(<1>, <2>), Or(<3>, <4>)), Or(<5>, <6>))
        node_ins = Or
        => returns [<1>, <2>, <3>, <4>, <5>, <6>]

    Args:
        root: root stack value of the instruction tree
        node_ins: node_ins is used to differentiate to identify leaf nodes.

    Returns:
        List of leaf nodes. Leaf nodes are stack values whose instruction is not :node_ins: and
        All stack values in the path from the root to the leaf node have :node_ins: instruction.
    """
    if isinstance(root, UnknownStackValue):
        return [root]
    if not isinstance(root.instruction, node_ins):
        # is not node_ins stack value. so a leaf
        return [root]
    left, right = root.args[0], root.args[1]
    return _flatten_ast(left, node_ins) + _flatten_ast(right, node_ins)


@lru_cache(maxsize=None)
def compute_equations(
    root: KnownStackValue, node_ins: Type[Instruction]
) -> Tuple[List[KnownStackValue], bool]:
    """Compute equations from And or Or expression.

    Args:
        root: Root of the instruction AST
        node_ins: The instruction whose result is being flattend. see documentation for _flatten_ast
            function above.

    Returns:
        equations: List of values on which, the result of **root** depends.

            And(And(<1>, <2>), And(And(<3>, <4>), And(<5>, <6>)))
            node_ins = And
            => returns [<1>, <2>, <3>, <4>, <5>, <6>]

            Or(Or(Or(<1>, <2>), Or(<3>, <4>)), Or(<5>, <6>))
            node_ins = Or
            => returns [<1>, <2>, <3>, <4>, <5>, <6>]

        has_unknown_value: True if the result of **root** depends on a unknown value.
    """
    equations = _flatten_ast(root, node_ins)
    has_unkown_value = False
    known_equations = []
    for eq in equations:
        if isinstance(eq, UnknownStackValue):
            has_unkown_value = True
        else:
            known_equations.append(eq)
    return known_equations, has_unkown_value


def get_stack_value_for_ins(ins: "Instruction") -> KnownStackValue:
    return construct_stack_ast(ins.bb)[ins]
