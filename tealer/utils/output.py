from typing import List, Dict, Any

from tealer.teal.basic_blocks import BasicBlock


def order_basic_blocks(bbs: List[BasicBlock]) -> List[BasicBlock]:
    key = lambda bb: bb.entry_instr.line
    return sorted(bbs, key=key)


def bbs_to_json(bbs: List[BasicBlock]) -> List[Dict[str, Any]]:
    """convert list of basic blocks to dict representation"""
    bbs = order_basic_blocks(bbs)

    id_to_index = {id(bb): index for index, bb in enumerate(bbs)}

    elements = []
    for bb in bbs:
        elem = {
            "type": "BasicBlock",
            "id": id_to_index[id(bb)],
            "instructions": [str(ins) for ins in bb.instructions],
            "prev": [id_to_index[id(prev_bb)] for prev_bb in bb.prev],
            "next": [id_to_index[id(next_bb)] for next_bb in bb.next],
        }

        elements.append(elem)

    return elements
