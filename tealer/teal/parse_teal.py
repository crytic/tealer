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

import sys
from typing import Optional, Dict, List

from tealer.teal.basic_blocks import BasicBlock
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
)
from tealer.teal.instructions.instructions import ContractType
from tealer.teal.instructions.parse_instruction import parse_line, ParseError
from tealer.teal.instructions.transaction_field import TransactionField
from tealer.teal.instructions.asset_holding_field import AssetHoldingField
from tealer.teal.instructions.asset_params_field import AssetParamsField
from tealer.teal.instructions.app_params_field import AppParamsField
from tealer.teal.instructions.acct_params_field import AcctParamsField
from tealer.teal.teal import Teal


def _detect_contract_type(instructions: List[Instruction]) -> ContractType:
    """Determine type of contract given it's instructions.

    It isn't possible to determine how a contract might be used, whether
    as an application or a signature in all cases. This function uses the
    fact that there are certain instructions in teal that are only valid if used
    in a certain kind of contract. So, this function looks for instructions
    that are valid in only one type and return that as the type for the given
    contract. if all instructions in the contract are valid for both types
    of contracts, then this function returns ContractType.ANY as it isn't
    sure how the contract might be used.

    Args:
        instructions: List of all the instructions present in the contract.

    Returns:
        Type of the contract indicated by ContractType enum symbol.
        ``STATEFULL`` if there's a instruction only valid in applications,
        ``STATELESS`` if there's a instruction only valid in signatures,
        ``ANY`` if there isn't any such instruction.
    """

    for ins in instructions:
        if ins.mode != ContractType.ANY:
            return ins.mode
    return ContractType.ANY


def create_bb(instructions: List[Instruction], all_bbs: List[BasicBlock]) -> None:
    """Construct basic blocks and add basic block sequential links.

    This function is the third pass of the teal parser. Instructions are
    divided into basic blocks based on the following rules:

    * A new basic block is created for each Label instruction.
    * Instructions B, Err, Return, Callsub, Retsub are exit instructions
        of a basic block. A new basic block is created for instructions
        following them.
    * A instruction with multiple next instructions is a exit instruction
        of the basic block. A new basic block is created for instructions
        following them.

    This function also adds sequential links between the constructed basic
    blocks. Two sequential basic blocks are linked if the exit instruction
    of the first basic block is sequentially previous instruction to the
    entry instruction of the second basic block.

    This is a "in place" function, given arguments are modified with the
    data this function is supposed to return.

    Args:
        instructions: List of parsed instruction objects.
        all_bbs: List of BasicBlock objects representing the teal contract.
            This is an "in place" argument, the basic blocks created in
            the function are appended to this list in the order they are created.
    """

    bb: Optional[BasicBlock] = BasicBlock()
    if bb:  # to make mypy happy
        all_bbs.append(bb)
    for ins in instructions:

        if isinstance(ins, Label) or not bb:
            # use bb if it is empty instead of creating new BasicBlock.
            if bb is None or len(bb.instructions) != 0:
                next_bb = BasicBlock()
                all_bbs.append(next_bb)
                if bb:
                    bb.add_next(next_bb)
                    next_bb.add_prev(bb)
                bb = next_bb
        bb.add_instruction(ins)
        ins.bb = bb

        if len(ins.next) > 1 and not isinstance(ins, Retsub):
            if not isinstance(ins.next[0], Label):
                next_bb = BasicBlock()
                all_bbs.append(next_bb)
                bb.add_next(next_bb)
                next_bb.add_prev(bb)
                bb = next_bb

        if len(ins.next) == 0 or isinstance(ins, (B, Err, Return, Callsub, Retsub)):
            bb = None


def _first_pass(
    lines: List[str],
    labels: Dict[str, Label],
    rets: Dict[str, List[Instruction]],
    instructions: List[Instruction],
) -> None:
    """Parse instructions and add sequential instruction links.

    This function is the first pass of the teal parser. Source code
    lines are parsed into corresponding Instruction objects and non-jump
    instructions are linked. Adding instructions links is linking two
    instruction objects as previous and next. Non-jump instruction links
    are links between instructions that are previous, next in terms of
    execution flow as well as previous, next in terms of source code i.e
    links that are directly evident from just those two instructions that
    are continous in source code. Jump links are links between branch
    instructions and their destination, callsub and their destination,
    retsub and their return points, etc. This function adds non-jump or
    sequential instruction links.

    This is a "in place" function, given arguments are modified with the
    data this function is supposed to return.

    Args:
        lines: List of source code lines of a teal contract.
        labels: Dict map from teal label string to the parsed label instruction.
            instance. This argument is an "in place" argument and will be
            populated by the function while parsing.
        rets: Dict map from teal label string of a subroutine to list of it's
            return point instructions. subroutines are supported from teal v4 and
            can be called with callsub instruction using the label of the subroutine.
            The execution flow is passed from the subroutine to next instruction of
            the callsub after executing the subroutine. This variable stores all those
            return points(next instruction after callsub) for each subroutine label
            in the contract.
            This argument is an "in place" argument and will be populated by the
            function while parsing.
        instructions: List of parsed instruction objects.
            This argument is also an "in place" argument and will be populated
            by the function while parsing.
    """

    # First pass over the intructions list: Add non-jump instruction links and collect meta-data
    idx = 0
    prev: Optional[Instruction] = None  # Flag: last instruction was an unconditional jump
    call: Optional[Callsub] = None  # Flag: last instruction was a callsub

    for line in lines:
        try:
            ins = parse_line(line.strip())
        except ParseError as e:
            print(f"Parse error at line {idx}: {e}")
            sys.exit(1)
        idx = idx + 1
        if not ins:
            continue
        ins.line = idx

        # A label? Add it to the global label list
        if isinstance(ins, Label):
            labels[ins.label] = ins

        # If the prev. ins. was anything other than an unconditional jump, then link the two instructions
        if prev:
            ins.add_prev(prev)
            prev.add_next(ins)

        # If the prev. inst was a callsub, add the current instruction as a return point for the callsub label
        if call:
            call.return_point = ins
            if call.label in rets.keys():
                rets[call.label].append(ins)
            else:
                rets[call.label] = [ins]

        # Now prepare for the next-line instruction
        # A flag that says that this was an unconditional jump
        prev = ins
        if isinstance(ins, (B, Err, Return, Callsub, Retsub)):
            prev = None

        # A flag that says that this was a callsub
        call = None
        if isinstance(ins, Callsub):
            call = ins

        # Finally, add the instruction to the instruction list
        instructions.append(ins)


def _second_pass(
    instructions: List[Instruction],
    labels: Dict[str, Label],
    rets: Dict[str, List[Instruction]],
) -> None:
    """Add jump or non-sequential instruction links.

    This function is second pass of the teal parser. Adding jump links is
    linking two instruction objects where execution flow is passed
    from the first instruction to the second instruction because of
    a jump. A jump is passing execution from one instruction to the
    next that are not sequential. A execution jump might happen because
    of branch, callsub, retsub instructions in TEAL. This function links
    such pairs of instructions as previous, next.

    Args:
        instructions: List of parsed instruction objects.
        labels: Dict map from teal label string to the parsed label instruction.
        rets: Dict map from teal label string of a subroutine to list of it's
            return point instructions.
    """

    # Second pass over the instructions list: Add instruction links for jumps
    for ins in instructions:

        # If a labeled jump, link the ins. to its label
        if isinstance(ins, (B, BZ, BNZ, Callsub)):
            ins.add_next(labels[ins.label])
            labels[ins.label].add_prev(ins)

    # link retsub instructions to return points of corresponding subroutines
    retsubs: Dict[str, List[Retsub]] = {}  # map each subroutine label to list of it's retsubs
    for subroutine in rets:
        label = labels[subroutine]
        retsubs[subroutine] = []

        # use dfs to find all retsub instructions starting from subroutine label instruction
        stack: List[Instruction] = []
        visited: List[Instruction] = []

        stack.append(label)
        while len(stack) > 0:
            ins = stack.pop()
            visited.append(ins)

            if isinstance(ins, Retsub):
                retsubs[subroutine].append(ins)
                continue

            for next_ins in ins.next:
                # don't follow callsub path, which initself is another subroutine
                if isinstance(next_ins, Callsub):
                    if next_ins.return_point is None:
                        continue
                    next_ins = next_ins.return_point

                if next_ins not in visited:
                    stack.append(next_ins)

    # link retsub to return points
    for subroutine in rets:
        for return_point in rets[subroutine]:
            for retsub_ins in retsubs[subroutine]:
                retsub_ins.add_next(return_point)
                return_point.add_prev(retsub_ins)


def _fourth_pass(instructions: List[Instruction]) -> None:
    """Add jump or non-sequential basic block links.

    This function is the fourth pass of the teal parser. Jump links
    are added between two basic blocks if there is a jump link from
    exit instruction of the first basic block to the entry instruction
    of the second basic block.

    Args:
        instructions: List of parsed instruction objects.
    """

    # Fourth pass over the instructiions list: Add jump-based basic block links
    for ins in instructions:
        # A branching instruction with more than one target (other than a retsub)
        if len(ins.next) > 1 and not isinstance(ins, Retsub):
            branch = ins.next[1]
            if branch.bb and ins.bb:
                branch.bb.add_prev(ins.bb)
            if ins.bb and branch.bb:
                ins.bb.add_next(branch.bb)
        # A single-target branching instruction (b or callsub or bz/bnz appearing as the last instruction in the list)
        if isinstance(ins, (B, Callsub)) or (
            ins == instructions[-1] and isinstance(ins, (BZ, BNZ))
        ):
            dst = ins.next[0].bb
            if dst and ins.bb:
                dst.add_prev(ins.bb)
            if ins.bb and dst:
                ins.bb.add_next(dst)
        # A retsub
        if isinstance(ins, Retsub):
            for branch in ins.next:
                if branch.bb and ins.bb:
                    branch.bb.add_prev(ins.bb)
                if ins.bb and branch.bb:
                    ins.bb.add_next(branch.bb)


def _add_basic_blocks_idx(bbs: List[BasicBlock]) -> List[BasicBlock]:
    """Set index of basic blocks based on their entry instruction line number.

    Basic Blocks are ordered in the increasing order based on the
    line number of their entry instructions. Index starts from 0.

    Args:
        bbs: List of BasicBlock objects representing the teal contract.
    """

    bbs = sorted(bbs, key=lambda x: x.entry_instr.line)
    for i, bb in enumerate(bbs):
        bb.idx = i
    return bbs


def _identify_subroutine_blocks(label: "Label") -> List["BasicBlock"]:
    """find all the basic blocks part of a subroutine given it's label instruction.

    Args:
        label ("Label"): label instruction of the subroutine.
        bbs (List["BasicBlock"]): CFG of the contract.

    Returns:
        List["BasicBlock"]: list of all basic blocks part of a subroutine.
    """

    if label.bb is None:
        return []

    subroutines_blocks: List["BasicBlock"] = []
    stack: List["BasicBlock"] = []

    stack.append(label.bb)
    while len(stack) > 0:
        bb = stack.pop()
        subroutines_blocks.append(bb)

        # check for retsub before exploring as retsubs are connected to return points
        if isinstance(bb.exit_instr, Retsub):
            continue

        # callsub return point is part of the subroutine
        if isinstance(bb.exit_instr, Callsub):
            return_point = bb.exit_instr.return_point

            if return_point and return_point.bb not in subroutines_blocks:
                if return_point.bb is not None:
                    stack.append(return_point.bb)
            continue

        for next_bb in bb.next:
            if next_bb not in subroutines_blocks:
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

    print("\nchecking instruction, field versions with contract version\n")
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
        if ins.mode == ContractType.STATEFULL:
            stateful_ins.append(ins)
        elif ins.mode == ContractType.STATELESS:
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


def parse_teal(source_code: str) -> Teal:
    """Parse algorand smart contracts written in teal.

    Parsing teal cotracts consists of four passes:

    #. Parses instructions and adds sequential instruction links.
    #. Adds jump based instruction links.
    #. Constructs basic blocks and adds sequential basic block links.
    #. Adds jump based basic block links.

    This function also performs basic version checks on the instructions
    and fields.

    Teal object is created with the parsed instructions, basic blocks and
    subroutines identified in the contract.

    Args:
        source_code: TEAL source code of the contract.

    Returns:
        Teal object representing the given contract created with the related
        information.
    """

    instructions: List[Instruction] = []  # Parsed instructions list
    labels: Dict[str, Label] = {}  # Global map of label names to label instructions
    rets: Dict[str, List[Instruction]] = {}  # Lists of return points corresponding to labels

    lines = source_code.splitlines()

    _first_pass(lines, labels, rets, instructions)
    _second_pass(instructions, labels, rets)

    # Third pass over the instructions list: Construct the basic blocks and sequential links
    all_bbs: List[BasicBlock] = []
    create_bb(instructions, all_bbs)

    _fourth_pass(instructions)

    all_bbs = _add_basic_blocks_idx(all_bbs)
    mode = _detect_contract_type(instructions)

    version = 1
    if isinstance(instructions[0], Pragma):
        version = instructions[0].program_version

    _verify_version(instructions, version)

    subroutines = []
    if version >= 4:
        for subroutine_label in rets:
            label_ins = labels[subroutine_label]
            subroutines.append(_identify_subroutine_blocks(label_ins))

    teal = Teal(instructions, all_bbs, version, mode, subroutines)

    # set teal instance to it's basic blocks
    for bb in teal.bbs:
        bb.teal = teal

    return teal
