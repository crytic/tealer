from typing import TYPE_CHECKING, Optional, Dict, List

from tealer.utils.teal_enums import TransactionType

if TYPE_CHECKING:
    from tealer.teal.functions import Function

# pylint: disable=too-few-public-methods, too-many-instance-attributes
class Transaction:
    def __init__(self) -> None:
        self.type: TransactionType = TransactionType.Any
        self.has_logic_sig: bool = False
        self.logic_sig: Optional["Function"] = None
        self.application: Optional["Function"] = None
        self.absoulte_index: Optional[int] = None
        self.relative_indexes: Dict[int, Transaction] = {}
        self.group_transaction: Optional[GroupTransaction] = None
        self.transacton_id: str = ""


# pylint: disable=too-few-public-methods
class GroupTransaction:
    def __init__(self) -> None:
        self.transactions: List[Transaction] = []
        self.absolute_indexes: Dict[int, Transaction] = {}
        self.operation_name: str = ""
