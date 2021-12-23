from pathlib import Path
from typing import List

from tealer.detectors.abstract_detector import AbstractDetector, DetectorType
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import (
    Eq,
    Greater,
    GreaterE,
    Instruction,
    Int,
    Less,
    LessE,
    Return,
    Txn,
)
from tealer.teal.instructions.transaction_field import Fee


def _is_fee_check(ins1: Instruction, ins2: Instruction) -> bool:
    if isinstance(ins1, Txn) and isinstance(ins1.field, Fee):
        return isinstance(ins2, Int)
    return False


class MissingFeeCheck(AbstractDetector):
    NAME = "feeCheck"
    DESCRIPTION = "Detect paths with a missing Fee check"
    TYPE = DetectorType.STATELESS

    def _check_fee(
        self,
        bb: BasicBlock,
        current_path: List[BasicBlock],
        paths_without_check: List[List[BasicBlock]],
    ) -> None:
        # check for loops
        if bb in current_path:
            return
        
        current_path = current_path + [bb]
        
        stack: List[Instruction] = []

        for ins in bb.instructions:

            if isinstance(ins, Less) or isinstance(ins, LessE):
               if len(stack) >= 2:
                   one = stack[-1]
                   two = stack[-2]
                   # int .. <[=?] txn fee or txn fee <[=?] int .. 
                   if _is_fee_check(one, two) or _is_fee_check(two, one):
                       return
            if isinstance(ins, Greater) or isinstance(ins, GreaterE):
                if len(stack) >= 2:
                    one = stack[-1]
                    two = stack[-2]
                    # int .. >[=?] txnfee or txn fee >[=?] int ..
                    if _is_fee_check(one, two) or _is_fee_check(two, one):
                        return
            if isinstance(ins, Eq):
                if len(stack) >= 2:
                    one = stack[-1]
                    two = stack[-2]
                    #  txn fee == int .. or txn fee == int ..
                    if _is_fee_check(one, two) or _is_fee_check(two, one):
                        return

            if isinstance(ins, Return):
                if len(ins.prev) == 1:
                    prev = ins.prev[0]
                    if isinstance(prev, Int) and prev.value == 0:
                        return
                
                paths_without_check.append(current_path)
                return
            
            stack.append(ins)
        
        for next_bb in bb.next:
            self._check_fee(next_bb, current_path, paths_without_check)

    def detect(self, json=False) -> List[str]:
        paths_without_check: List[List[BasicBlock]] = []
        self._check_fee(self.teal.bbs[0], [], paths_without_check)

        if json:
            return [self.paths_to_json(paths_without_check)]
        
        all_results_txt: List[str] = []
        idx = 1
        for path in paths_without_check:
            filename = Path(f"missing_fee_check_{idx}.dot")
            idx += 1
            description = "Lack of fee check allows draining the funds of sender account"
            description += f"\n\tCheck the path in {filename}\n"
            all_results_txt.append(description)
            self.teal.bbs_to_dot(filename, path)
        
        return all_results_txt