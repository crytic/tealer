from typing import List, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from tealer.teal.teal import Teal
    from tealer.execution_context.transactions import GroupTransaction


class Tealer:
    """Base class for the tool"""

    def __init__(self, contracts: Dict[str, "Teal"], groups: List["GroupTransaction"]):
        self._contracts = contracts
        self._groups = groups

    @property
    def contracts(self) -> Dict[str, "Teal"]:
        return self._contracts

    @property
    def contracts_list(self) -> List["Teal"]:
        return list(self._contracts.values())

    @property
    def groups(self) -> List["GroupTransaction"]:
        return self._groups
