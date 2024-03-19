from abc import ABC, abstractmethod
from typing import List, Any, TypeVar, Generic, TYPE_CHECKING

from tealer.teal.basic_blocks import BasicBlock

AbstractValues = TypeVar("AbstractValues")

if TYPE_CHECKING:
    from tealer.teal.teal import Teal


class AbstractDataflow(ABC, Generic[AbstractValues]):
    def __init__(self, teal: "Teal"):
        self.teal = teal

    @abstractmethod
    def _merge_predecessor(self, bb: BasicBlock) -> AbstractValues:
        pass

    @abstractmethod
    def _is_fix_point(self, bb: BasicBlock, values: AbstractValues) -> bool:
        pass

    @abstractmethod
    def _transfer_function(self, bb: BasicBlock) -> AbstractValues:
        pass

    @abstractmethod
    def _store_values_in(self, bb: BasicBlock, values: AbstractValues) -> None:
        pass

    @abstractmethod
    def _store_values_out(self, bb: BasicBlock, values: AbstractValues) -> None:
        pass

    @abstractmethod
    def _filter_successors(self, bb: BasicBlock) -> List[BasicBlock]:
        pass

    @abstractmethod
    def result(self) -> Any:
        pass

    def explore(self, bb: BasicBlock, is_entry_node: bool = False) -> None:

        values = self._merge_predecessor(bb)

        if not is_entry_node and self._is_fix_point(bb, values):
            return

        self._store_values_in(bb, values)
        values = self._transfer_function(bb)
        self._store_values_out(bb, values)

        successors = self._filter_successors(bb)
        for successor in successors:
            self.explore(successor)

    def run_analysis(self) -> None:
        self.explore(self.teal.bbs[0], is_entry_node=True)
