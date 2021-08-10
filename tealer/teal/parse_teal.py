from typing import Optional, Dict, List

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Instruction, Label, B, Err, Assert, BNZ, BZ, Return, Callsub, Retsub
from tealer.teal.instructions.parse_instruction import parse_line
from tealer.teal.teal import Teal


def create_bb(instructions: List[Instruction], all_bbs: List[BasicBlock]):
    bb: Optional[BasicBlock] = BasicBlock()
    all_bbs.append(bb)
    for ins in instructions:

        if isinstance(ins, Label) or not bb:
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


def parse_teal(source_code: str) -> Teal:
    instructions: List[Instruction] = []      # Parsed instructions list
    labels: Dict[str, Instruction] = {}       # Global map of label names to label instructions
    prev: Optional[Instruction] = None        # Flag: last instruction was an unconditional jump
    entries: List[Instruction] = []           # Current list of labels not closed by a retsub
    rets: Dict[str, List[Instruction]] = {}   # Lists of return points corresponding to labels
    call: Optional[Callsub] = None            # Flag: last instruction was a callsub

    lines = source_code.splitlines()
    idx = 0

    # First pass over the intructions list: Add non-jump instruction links and collect meta-data
    for line in lines:
        ins = parse_line(line.strip())
        idx = idx + 1
        if not ins:
            continue
        ins.line = idx

        # A label? Add it to the global label list and the currently open entry points list
        if isinstance(ins, Label):
            labels[ins.label] = ins
            entries.append(ins)

        # A retsub? Assign the current open entry points list to it and then reset the list
        if isinstance(ins, Retsub):
            ins.set_labels(entries[:])
            entries = []

        # If the prev. ins. was anything other than an unconditional jump, then link the two instructions
        if prev:
            ins.add_prev(prev)
            prev.add_next(ins)

        # If the prev. inst was a callsub, add the current instruction as a return point for the callsub label
        if call:
            if call.label in rets.keys():
                rets[call.label].append(ins)
            else:
                rets[call.label] = [ins]

        # Now prepare for the next-line instruction
        # A flag that says that this was an unconditional jump
        if isinstance(ins, (B, Err, Return, Callsub, Retsub)):
            prev = None
        else:
            prev = ins

        # A flag that says that this was a callsub
        if isinstance(ins, Callsub):
            call = ins
        else:
            call = None

        # Finally, add the instruction to the instruction list
        instructions.append(ins)

    # Second pass over the instructions list: Add instruction links for jumps
    for ins in instructions:

        # If a labeled jump, link the ins. to its label
        if isinstance(ins, (B, BZ, BNZ, Callsub)):
            ins.add_next(labels[ins.label])
            labels[ins.label].add_prev(ins)

        # If a retsub, link the ins. to its return point(s)
        if isinstance(ins, Retsub):
            for entry in ins.labels:
                if entry.label in rets.keys():
                    for ret in rets[entry.label]:
                        ins.add_next(ret)
                        ret.add_prev(ins)

    # Third pass over the instructions list: Construct the basic blocks and sequential links
    all_bbs: List[BasicBlock] = []
    create_bb(instructions, all_bbs)

    # Fourth pass over the instructiions list: Add jump-based basic block links
    for ins in instructions:
        # A branching instruction with more than one target (other than a retsub)
        if len(ins.next) > 1 and not isinstance(ins, Retsub):
            branch = ins.next[1]
            branch.bb.add_prev(ins.bb)
            ins.bb.add_next(branch.bb)
        # A single-target branching instruction (b or callsub or bz/bnz appearing as the last instruction in the list)
        if isinstance(ins, (B, Callsub)) or (ins == instructions[-1] and isinstance(ins, (BZ, BNZ))):
            dst = ins.next[0].bb
            dst.add_prev(ins.bb)
            ins.bb.add_next(dst)
        # A retsub
        if isinstance(ins, Retsub):
            for branch in ins.next:
                branch.bb.add_prev(ins.bb)
                ins.bb.add_next(branch.bb)



    return Teal(instructions, all_bbs)
