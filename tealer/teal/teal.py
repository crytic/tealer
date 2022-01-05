from typing import List

from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.instructions import Instruction, ContractType


class Teal:
    def __init__(
        self,
        instructions: List[Instruction],
        bbs: List[BasicBlock],
        version: int,
        mode: ContractType,
    ):
        self._instructions = instructions
        self._bbs = bbs
        self._version = version
        self._mode = mode

    @property
    def instructions(self) -> List[Instruction]:
        return self._instructions

    @property
    def bbs(self) -> List[BasicBlock]:
        return self._bbs

    @property
    def version(self) -> int:
        return self._version

    @version.setter
    def version(self, ver: int) -> None:
        self._version = ver

    @property
    def mode(self) -> ContractType:
        return self._mode

    @mode.setter
    def mode(self, m: ContractType) -> None:
        self._mode = m
