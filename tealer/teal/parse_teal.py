"""Parser for teal contracts.

A TEAL contract is represented using Teal class in tealer. Teal class
comes with methods to register, run analyzers(detectors) and
printers on the parsed contract. Parsing a teal contract is
creating the Control Flow Graph(CFG) of the teal contract,
constructing Teal class instance with the CFG, subroutines and
other related information.

Additional to parsing the teal contracts, subroutines defined in
the contract are identified if there are any, versions of instructions
are verified against the contract version and also attempts to detect mode
of the contract. All the information is stored in the Teal class
representing the contract.

Contracts are parsed in four passes:

#. Parses instructions and adds sequential instruction links.
#. Adds jump based instruction links.
#. Constructs basic blocks and adds sequential basic block links.
#. Adds jump based basic block links.

The final result of parsing is the Control Flow Graph(CFG) of the
contract represented by sequence of the basic blocks.

"""
# pylint: disable=too-many-lines

import sys
import logging
from typing import Optional, Dict, List, Tuple
from collections import defaultdict

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.subroutine import Subroutine
from tealer.teal.instructions.instructions import (
    Instruction,
    Label,
    B,
    Err,
    BNZ,
    BZ,
    Return,
    Callsub,
    Retsub,
    Pragma,
    Switch,
    Match,
    Intcblock,
    Bytecblock,
    Txn,
    Method,
)

from tealer.teal.instructions.parse_instruction import parse_line, ParseError
from tealer.teal.instructions.transaction_field import TransactionField, ApplicationID
from tealer.teal.instructions.asset_holding_field import AssetHoldingField
from tealer.teal.instructions.asset_params_field import AssetParamsField
from tealer.teal.instructions.app_params_field import AppParamsField
from tealer.teal.instructions.acct_params_field import AcctParamsField
from tealer.teal.teal import Teal
from tealer.utils.arc4_abi import get_method_selector
from tealer.utils.teal_enums import ExecutionMode


logger_parsing = logging.getLogger("Parsing")
logging.basicConfig()


def _detect_execution_mode(instructions: List[Instruction]) -> ExecutionMode:
    """Determine type of contract given its instructions.

    If any of the instructions is supported in only one execution mode then return that as
    contract's execution mode. Otherwise, return ExecutionMode.ANY

    Args:
        instructions: List of all the instructions present in the contract.

    Returns:
        Returns the execution mode of the contract: Stateful, Stateless or Any.
    """

    for ins in instructions:
        if ins.mode != ExecutionMode.ANY:
            return ins.mode
    return ExecutionMode.ANY


def create_bb(instructions: List[Instruction], all_bbs: List[BasicBlock]) -> None:
    """Construct basic blocks and add basic block default edges.

    Third pass of the teal parser. Instructions are
    divided into basic blocks based on the following rules:

    * Label instruction is destination for multiple instructions. A new
        basic block is created for each Label instruction.
    * Instructions B, Err, Return, Callsub, Retsub are exit instructions
        of a basic block. A new basic block is created for instructions
        following them.
    * A instruction with multiple next instructions is a exit instruction
        of the basic block. A new basic block is created for instructions
        following them.

    This function also adds default edges between the constructed basic
    blocks. Two basic blocks have default edge if the entry instruction
    of the second basic block is default next instruction for the exit instruction
    of the first basic block.

    Args:
        instructions: List of instructions.
        all_bbs: (in-place) List of BasicBlocks representing the teal contract.
    """

    bb = BasicBlock()
    all_bbs.append(bb)
    for ins in instructions:

        # if instruction is label and basic block is not empty:
        #   Create a new basic block and add default edge
        # if basic block is empty, no need to create new one.
        if isinstance(ins, Label) and len(bb.instructions) != 0:
            next_bb = BasicBlock()
            all_bbs.append(next_bb)
            bb.add_next(next_bb)
            next_bb.add_prev(bb)
            bb = next_bb

        bb.add_instruction(ins)
        ins.bb = bb

        # `BZ`, `BNZ`, `match` and `switch` have more than one next instruction.
        # `Callsub` has only one next instruction and it is the default next instruction
        # For these instructions, execution continues on the next instruction by default.
        if len(ins.next) > 1 or isinstance(ins, Callsub):
            # if the instruction is the last instruction, do not create a new *empty* block.
            if ins == instructions[-1]:
                continue
            next_bb = BasicBlock()
            all_bbs.append(next_bb)
            # add sequential link
            bb.add_next(next_bb)
            next_bb.add_prev(bb)
            bb = next_bb

        # Err, Return, Retsub will have `len(ins.next) == 0` and `B`.
        if len(ins.next) == 0 or isinstance(ins, B):
            # if the instruction is the last instruction, do not create a *empty* block.
            if ins == instructions[-1]:
                continue
            next_bb = BasicBlock()
            all_bbs.append(next_bb)
            # Do not add any edges. There are no default edges and Jump edges are added in the next pass.
            bb = next_bb


def _add_instruction_comments(ins: Instruction) -> None:
    if isinstance(ins, Txn) and isinstance(ins.field, ApplicationID):
        ins.tealer_comments.append("ApplicationID is 0 in Creation Txn")
    elif isinstance(ins, Method):
        method_signature = ins.method_signature
        method_signature.strip('"')  # quotes are not removed while parsing
        method_selector = get_method_selector(method_signature)
        ins.tealer_comments.append(f"method-selector: {method_selector}")


def first_pass(  # pylint: disable=too-many-branches
    lines: List[str],
    labels: Dict[str, Label],
    subroutines: Dict[str, List[Callsub]],
    instructions: List[Instruction],
) -> Tuple[List[Intcblock], List[Bytecblock]]:
    """Parse instructions and add default instruction edges.

    First pass of the teal parser. Source code lines are parsed into corresponding Instruction objects and default
    edges are added to the instructions.
    * default edges are edges between two continuous instructions where execution might pass from the first
        instruction to the second instruction.
    * Jump edges are edges between two non-continuous instructions where execution might pass from the first instruction
        to the second.

    Args:
        lines: List of source code lines of a teal contract.
        labels: (in-place) Map from teal label string to the parsed label instruction.
            instance.
        subroutines: (in-place) Map from subroutine name to callsub instructions calling the subroutine.
        instructions: (in-place) List of parsed instructions.

    Returns:
        intcblock_ins: List of `intcblock` instructions in the contract.
        bytecblock_ins: List of `bytecblock` instructions in the contract.
    """

    # First pass over the intructions list: Add default edges and collect other information.
    idx = 0
    prev: Optional[Instruction] = None  # Flag: last instruction was an unconditional jump
    intcblock_ins: List[Intcblock] = []  # List of intcblock instructions present in the contract
    bytecblock_ins: List[Bytecblock] = []  # List of bytecblock instructions present in the contract

    instruction_comments: List[str] = []
    for line in lines:
        try:
            if line.strip().startswith("//"):
                # is a comment without any instruction
                instruction_comments.append(line)
                ins = None
            else:
                ins = parse_line(line)
                if ins and instruction_comments:
                    ins.comments_before_ins = list(instruction_comments)
                    instruction_comments = []
        except ParseError as e:
            print(f"Parse error at line {idx}: {e}")
            sys.exit(1)
        idx = idx + 1
        if not ins:
            continue

        if isinstance(ins, Intcblock):
            intcblock_ins.append(ins)
        elif isinstance(ins, Bytecblock):
            bytecblock_ins.append(ins)

        ins.line = idx
        _add_instruction_comments(ins)

        # A label? Add it to the global label list
        if isinstance(ins, Label):
            labels[ins.label] = ins

        # If the prev. ins. was anything **other** than an unconditional jump or unconditional exit:
        #   then add default between the two instructions
        if prev:
            ins.add_prev(prev)
            prev.add_next(ins)

        # A flag that says that this was an unconditional jump or unconditional exit instructions.
        # `Callsub`` is not an unconditional jump instruction.
        # `B` is unconditional jump.
        # `Err, Return` is unconditional exit of the program.
        # `Retsub` is unconditional exit of the subroutine.
        prev = ins
        if isinstance(ins, (B, Err, Return, Retsub)):
            prev = None

        # if ins is callsub, add the label to subroutines and store callsub instruction.
        if isinstance(ins, Callsub):
            subroutines[ins.label].append(ins)

        # Finally, add the instruction to the instruction list
        instructions.append(ins)
    return intcblock_ins, bytecblock_ins


def second_pass(  # pylint: disable=too-many-branches
    instructions: List[Instruction],
    labels: Dict[str, Label],
) -> None:
    """Add jump edges between instructions.

    Second pass of the teal parser.
    * Jump edges are edges between two non-continuous instructions where execution might pass from the first instruction
        to the second.
    * Jump instructions: `B`, `BZ`, `BNZ`, `match`, `switch`.

    Args:
        instructions: List of instructions.
        labels: Map from teal label string to the parsed label instruction.
    """
    logger_parsing.debug("Second Pass")
    # Second pass over the instructions list: Add instruction links for jumps
    for ins in instructions:

        # If a labeled jump to a single instruction, link the ins to its label
        if isinstance(ins, (B, BZ, BNZ)):
            ins.add_next(labels[ins.label])
            labels[ins.label].add_prev(ins)

        # if switch or match, link the ins to its labels
        if isinstance(ins, (Switch, Match)):
            for ins_label in ins.labels:
                ins.add_next(labels[ins_label])
                labels[ins_label].add_prev(ins)


def fourth_pass(basic_blocks: List[BasicBlock]) -> None:  # pylint: disable=too-many-branches
    """Add jump edges between basic blocks.

    Fourth pass of the teal parser. Jump edges
    are added between two basic blocks if there is a jump edge from
    exit instruction of the first basic block to the entry instruction
    of the second basic block.

    Args:
        basic_blocks: List of basic blocks.
    """

    # Fourth pass over the basic blocks: Add jump edges between basic blocks
    for bb in basic_blocks:
        ins = bb.exit_instr
        for next_ins in ins.next:
            next_bb = next_ins.bb
            if next_bb not in bb.next:
                assert bb not in next_bb.prev
                bb.add_next(next_bb)
                next_bb.add_prev(bb)


def _add_basic_blocks_idx(bbs: List[BasicBlock]) -> List[BasicBlock]:
    """Set index of basic blocks based on their entry instruction line number.

    Basic Blocks are ordered in the increasing order based on the
    line number of their entry instructions. Index starts from 0.

    Args:
        bbs: List of BasicBlock objects representing the teal contract.

    Returns:
        Returns :bbs: after sorting and updating their indexes(idx).
    """

    bbs = sorted(bbs, key=lambda x: x.entry_instr.line)
    for i, bb in enumerate(bbs):
        bb.idx = i
    return bbs


def identify_subroutine_blocks(entry_block: "BasicBlock") -> List["BasicBlock"]:
    """find all the basic blocks part of a subroutine using DFS.

    Args:
        entry_block: Entry block of the subroutine.

    Returns:
        Returns the list of all basic blocks part of a subroutine.
    """

    subroutines_blocks: List["BasicBlock"] = []
    stack: List["BasicBlock"] = []

    stack.append(entry_block)
    while len(stack) > 0:
        bb = stack.pop()
        subroutines_blocks.append(bb)

        for next_bb in bb.next:
            if next_bb not in subroutines_blocks and next_bb not in stack:
                stack.append(next_bb)

    return subroutines_blocks


def _verify_version(ins_list: List[Instruction], program_version: int) -> bool:
    """Verify contract instructions and fields are supported in given teal version.

    verify that instructions and fields used in the contract are supported in the
    Teal version specified by the contract. This function doesn't raise an exception
    in case of error, only returns a boolean representing the presence of it and
    prints related information to stderr.

    Args:
        ins_list (List[Instruction]): list of contract instructions.
        program_version (int): Teal version to check against the instruction and
            fields version.

    Returns:
        (bool): returns true if there is any error i.e if any of the instructions or fields are
        not supported in the contract version Or if the contract contains instructions that are
        specific to both Signature and Application Mode.
    """

    stateful_ins: List[Instruction] = []
    stateless_ins: List[Instruction] = []
    error = False

    for ins in ins_list:
        if program_version < ins.version:
            print(
                f"{ins.line}: {ins} instruction is not supported in Teal version {program_version}"
                f", it is supported from Teal version {ins.version}",
                file=sys.stderr,
            )
            error = True
        else:
            field = getattr(ins, "field", None)
            if field is not None and isinstance(
                field,
                (
                    TransactionField,
                    AssetHoldingField,
                    AssetParamsField,
                    AppParamsField,
                    AcctParamsField,
                ),
            ):
                if program_version < field.version:
                    print(
                        f"{ins.line}: {ins}, field {field} is not supported in Teal version {program_version}"
                        f", it is supported from Teal version {field.version}",
                        file=sys.stderr,
                    )
                    error = True
        if ins.mode == ExecutionMode.STATEFUL:
            stateful_ins.append(ins)
        elif ins.mode == ExecutionMode.STATELESS:
            stateless_ins.append(ins)

    if stateless_ins and stateful_ins:
        print(
            "\nprogram contains instructions specific to both Application and Signature Mode",
            file=sys.stderr,
        )
        print("Instructions supported only in Signature Mode:", file=sys.stderr)
        for ins in stateless_ins:
            print(f"\t{ins.line}: {ins}", file=sys.stderr)
        print("\nInstructions supported only in Application Mode:", file=sys.stderr)
        for ins in stateful_ins:
            print(f"\t{ins.line}: {ins}", file=sys.stderr)
        error = True

    return error


def _fill_intc_bytec_info(
    intcblock_ins: List[Intcblock],
    bytecblock_ins: List[Bytecblock],
    entry_block: BasicBlock,
    teal: Teal,
) -> None:
    """Find intcblock, bytecblock instructions and fill that information in Teal class

    Tealer determines intc_*/bytec_* instruction values if and only if intcblock, bytecblock
    instructions are used only once and that too in the entry block itself.

    This is the case for most of the contracts as intcblock/bytecblock instructions are generated
    internally by the assembler or PyTeal compiler.

    Args:
        intcblock_ins: List of all "intcblock" instructions in the contract.
        bytecblock_ins: List of all "bytecblock" instructions in the contract.
        entry_block: Entry block of the contract.
        teal: The contract.
    """
    if len(intcblock_ins) == 1 and intcblock_ins[0].bb == entry_block:
        teal.set_int_constants(intcblock_ins[0].constants)

    if len(bytecblock_ins) == 1 and bytecblock_ins[0].bb == entry_block:
        teal.set_byte_constants(bytecblock_ins[0].constants)


def parse_teal(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    source_code: str, contract_name: str = ""
) -> Teal:
    """Parse algorand smart contracts written in teal.

    Parsing teal cotracts consists of four passes:

    #. Parses instructions and adds default edges between instructions.
    #. Adds jump edges between links.
    #. Constructs basic blocks and adds default edges between basic block.
    #. Adds jump edges between basic blocks.

    Args:
        source_code: TEAL source code of the contract.
        contract_name: Name of the contract.

    Returns:
        Teal representing the given contract.
    """

    instructions: List[Instruction] = []  # Parsed instructions list
    labels: Dict[str, Label] = {}  # Global map of label names to label instructions
    # Map from subroutine name to callsub instructions calling it
    subroutine_callsubs: Dict[str, List[Callsub]] = defaultdict(list)

    lines = source_code.splitlines()

    intcblock_ins, bytecblock_ins = first_pass(lines, labels, subroutine_callsubs, instructions)
    logger_parsing.debug(f"subroutine_callsubs = {subroutine_callsubs}")
    second_pass(instructions, labels)
    logger_parsing.debug("instruction and nexts")
    for ins in instructions:
        logger_parsing.debug(f"     {ins}, next: {ins.next}")

    # Third pass over the instructions list: Construct the basic blocks and sequential links
    all_bbs: List[BasicBlock] = []
    create_bb(instructions, all_bbs)

    fourth_pass(all_bbs)

    all_bbs = _add_basic_blocks_idx(all_bbs)
    mode = _detect_execution_mode(instructions)

    version = 1
    if isinstance(instructions[0], Pragma):
        version = instructions[0].program_version

    _verify_version(instructions, version)

    all_reachable_blocks: List["BasicBlock"] = []
    subroutines_and_blocks: Dict[str, List["BasicBlock"]] = {}
    for subroutine_name in subroutine_callsubs:
        subroutine_entry_block = labels[subroutine_name].bb
        subroutine_blocks = identify_subroutine_blocks(subroutine_entry_block)
        subroutines_and_blocks[subroutine_name] = subroutine_blocks
        all_reachable_blocks += subroutine_blocks

    contract_entry_block = all_bbs[0]
    main_entry_point_blocks = identify_subroutine_blocks(contract_entry_block)
    all_reachable_blocks += main_entry_point_blocks

    subroutines: Dict[str, "Subroutine"] = {}
    for subroutine_name in subroutine_callsubs:
        label_ins = labels[subroutine_name]
        subroutine_entry_block = label_ins.bb
        # add tealer comment "Subroutine: {label}" to the subroutine entry block
        subroutine_entry_block.tealer_comments.append(f"Subroutine {subroutine_name}")
        # list all blocks of the subroutine using DFS
        subroutine_blocks = subroutines_and_blocks[subroutine_name]
        subroutine_obj = Subroutine(subroutine_name, subroutine_entry_block, subroutine_blocks)
        # set callsub blocks calling the subroutine
        callsub_blocks = [ins.bb for ins in subroutine_callsubs[subroutine_name]]
        callsub_blocks = [bb for bb in callsub_blocks if bb in all_reachable_blocks]
        subroutine_obj.caller_blocks = callsub_blocks
        # for each callsub instruction, set the called subroutine
        for ins in subroutine_callsubs[subroutine_name]:
            ins.called_subroutine = subroutine_obj

        # set subroutine to each basic block
        for bi in subroutine_blocks:
            bi.subroutine = subroutine_obj
        subroutines[subroutine_name] = subroutine_obj

    main_program_name = "__main__"
    main_program = Subroutine(main_program_name, contract_entry_block, main_entry_point_blocks)
    for bi in main_entry_point_blocks:
        bi.subroutine = main_program

    # TODO: Handle unreachable basic blocks.
    # Note: PyTeal generated contracts have unreachable code.
    for bi in all_bbs:
        if bi not in all_reachable_blocks:
            # bi is unreachable
            for bnext in bi.next:
                bnext.prev.remove(bi)
                bi.next.remove(bnext)

            for ins_next in bi.exit_instr.next:
                ins_next.prev.remove(bi.exit_instr)
                bi.exit_instr.next.remove(ins_next)

            for ins in bi.instructions:
                instructions.remove(ins)

    all_reachable_blocks = sorted(list(set(all_reachable_blocks)), key=lambda bi: bi.idx)
    teal = Teal(version, mode, instructions, all_reachable_blocks, main_program, subroutines)

    # set teal instance for it's basic blocks
    for bb in teal.bbs:
        bb.teal = teal
        bb.tealer_comments.insert(0, f"block_id = {bb.idx}; cost = {bb.cost}")

    for subroutine in [main_program] + list(subroutines.values()):
        subroutine.contract = teal

    teal.contract_name = contract_name
    _fill_intc_bytec_info(intcblock_ins, bytecblock_ins, teal.main.entry, teal)

    return teal
