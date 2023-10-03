from typing import List, Tuple

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Instruction


def cmp_instructions(ins1: Instruction, ins2: Instruction) -> bool:
    return str(ins1) == str(ins2)


def order_basic_blocks(bbs: List[BasicBlock]) -> List[BasicBlock]:
    key = lambda bb: bb.entry_instr.line
    return sorted(bbs, key=key)


def cmp_basic_blocks(b1: BasicBlock, b2: BasicBlock) -> bool:
    if len(b1.instructions) != len(b2.instructions):
        print(
            f"number of instructions are different: {len(b1.instructions)}, {len(b2.instructions)}"
        )
        return False

    for ins1, ins2 in zip(b1.instructions, b2.instructions):
        if not cmp_instructions(ins1, ins2):
            print(f"instructions comparison faile: {ins1}, {ins2}")
            return False

    return True


def cmp_cfg(bbs1: List[BasicBlock], bbs2: List[BasicBlock]) -> bool:
    if len(bbs1) != len(bbs2):
        print(f"number of blocks are different: {len(bbs1)}, {len(bbs2)}")
        return False
    bbs1, bbs2 = map(order_basic_blocks, (bbs1, bbs2))

    for bb1, bb2 in zip(bbs1, bbs2):
        print(f"comparing bb1: {bb1.idx}, bb2: {bb2.idx}\nbb1:\n{bb1}\nbb2:\n{bb2}\n")
        if not cmp_basic_blocks(bb1, bb2):
            return False

        if len(bb1.prev) != len(bb2.prev):
            print(f"number of prev blocks are different: {len(bb1.prev)}, {len(bb2.prev)}")
            print(bb1.prev)
            print(bb2.prev)
            return False

        if len(bb1.next) != len(bb2.next):
            print(f"number of next blocks are different: {len(bb1.next)}, {len(bb2.next)}")
            print(bb1.next)
            print(bb2.next)
            return False

        bbs_prev_1, bbs_prev_2 = map(order_basic_blocks, (bb1.prev, bb2.prev))
        for bbp1, bbp2 in zip(bbs_prev_1, bbs_prev_2):
            if bbp1.entry_instr.line != bbp2.entry_instr.line:
                print("entry lines of previous blocks is different")
                print(bbp1.entry_instr.line, bbp2.entry_instr.line)
                return False

        bbs_next_1, bbs_next_2 = map(order_basic_blocks, (bb1.next, bb2.next))
        for bbn1, bbn2 in zip(bbs_next_1, bbs_next_2):
            if bbn1.entry_instr.line != bbn2.entry_instr.line:
                print("entry lines of next blocks is different")
                print(bbn1.entry_instr.line, bbn2.entry_instr.line)
                return False

    return True


def construct_cfg(
    ins_list: List[Instruction],
    ins_partitions: List[Tuple[int, int]],
    bbs_links: List[Tuple[int, int]],
) -> List[BasicBlock]:
    """cfg construction helper function.

    construct cfg using the list of instructions, basic block partitions
    and their relation.

    Args:
        ins_list: list of instructions of the program.
        ins_partitions (List[Tuple[int]]): list of tuple indicating starting and
                ending index into ins_list where ins_list[starting: ending] belong to a
                single basic_block.
        bbs_links (List[Tuple[int]]): links two basic blocks (b1, b2). indexes of basic block
                corresponds to index in ins_partition. order of indexes is important as this adds
                a directed edge from b1 to b2.

    Returns:
        List[BasicBlock]: returns a list of basic blocks representing the CFG.
    """
    for idx, ins in enumerate(ins_list, start=1):
        ins.line = idx

    bbs = []
    for (idx, (start, end)) in enumerate(ins_partitions):
        bb = BasicBlock()
        for ins in ins_list[start:end]:
            bb.add_instruction(ins)
        bb.idx = idx
        bbs.append(bb)

    for idx1, idx2 in bbs_links:
        bbs[idx1].add_next(bbs[idx2])
        bbs[idx2].add_prev(bbs[idx1])

    return bbs
