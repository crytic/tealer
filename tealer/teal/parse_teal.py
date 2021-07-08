from typing import Optional, Dict, List

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Instruction, Label, B, Err, Assert, BNZ, BZ, Return
from tealer.teal.instructions.parse_instruction import parse_line
from tealer.teal.teal import Teal


def create_bb(instructions: List[Instruction], all_bbs: List[BasicBlock]):
    bb: Optional[BasicBlock] = BasicBlock()
    all_bbs.append(bb)
    for ins in instructions:

        if isinstance(ins, Label):
            next_bb = BasicBlock()
            all_bbs.append(next_bb)
            if bb:
                bb.add_next(next_bb)
                next_bb.add_prev(bb)
            bb = next_bb
        bb.add_instruction(ins)
        ins.bb = bb

        if len(ins.next) > 1:
            if not isinstance(ins.next[0], Label):
                next_bb = BasicBlock()
                all_bbs.append(next_bb)
                bb.add_next(next_bb)
                next_bb.add_prev(bb)
                bb = next_bb

        if len(ins.next) == 0 or isinstance(ins, B):
            bb = None


def parse_teal(source_code: str) -> Teal:
    instructions: List[Instruction] = []
    labels: Dict[str, Instruction] = {}
    prev: Optional[Instruction] = None

    lines = source_code.splitlines()
    idx = 0
    for line in lines:
        ins = parse_line(line)
        idx = idx + 1
        if not ins:
            continue
        ins.line = idx

        if isinstance(ins, Label):
            labels[ins.label] = ins

        if prev:
            ins.add_prev(prev)
            prev.add_next(ins)

        if isinstance(ins, (B, Err, Return)):
            prev = None
        else:
            prev = ins

        instructions.append(ins)

    for ins in instructions:
        if isinstance(ins, (B, BZ, BNZ)):
            ins.add_next(labels[ins.label])
            labels[ins.label].add_prev(ins)

    # bb = BasicBlock()
    all_bbs: List[BasicBlock] = []  # [bb]
    create_bb(instructions, all_bbs)
    # create_bb(bb, instructions[0], all_bbs)

    for ins in instructions:
        if len(ins.next) > 1:
            branch = ins.next[1]
            branch.bb.add_prev(ins.bb)
            ins.bb.add_next(branch.bb)
        if isinstance(ins, B):
            dst = ins.next[0].bb
            dst.add_prev(ins.bb)
            ins.bb.add_next(dst)

    return Teal(instructions, all_bbs)
