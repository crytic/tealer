from typing import List

from tealer.teal.basic_blocks import BasicBlock


class Subroutine:
    def __init__(
        self,
        blocks: List[BasicBlock],
        exit_blocks: List[BasicBlock],
        input_size: int,
        output_size: int,
    ) -> None:
        self._blocks = blocks
        self._exit_blocks = exit_blocks
        self._input_size = input_size
        self._output_size = output_size
        self._input_types = []
        self._output_types = []

    @property
    def blocks(self) -> List[BasicBlock]:
        return self._blocks

    @property
    def exit_blocks(self) -> List[BasicBlock]:
        return self._exit_blocks

    @property
    def input_size(self) -> int:
        return self._input_size

    @property
    def output_size(self) -> int:
        return self._output_size

    @property
    def input_types(self) -> List[str]:
        return self._input_types

    @input_types.setter
    def input_types(self, t) -> None:
        self._input_types = t

    @property
    def output_types(self) -> List[str]:
        return self._output_types

    @output_types.setter
    def output_types(self, t) -> None:
        self._output_types = t