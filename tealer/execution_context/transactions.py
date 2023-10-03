from typing import TYPE_CHECKING, Optional, Dict, List

from tealer.utils.teal_enums import TransactionType

# from tealer.exceptions import TealerException

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
        # t1.relative_indexes[-1] = t2 => t2.group_index() == t1.group_index() - 1
        self.relative_indexes: Dict[int, Transaction] = {}
        self.group_transaction: Optional[GroupTransaction] = None
        self.transacton_id: str = ""


# pylint: disable=too-few-public-methods
class GroupTransaction:
    def __init__(self) -> None:
        self.transactions: List[Transaction] = []
        self.absolute_indexes: Dict[int, Transaction] = {}
        # {t1: (t2, -2)} => t1.group_index() == t2.group_index() - 2
        self.group_relative_indexes: Dict[Transaction, Dict[Transaction, int]] = {}
        self.operation_name: str = ""


def fill_group_relative_indexes(group: "GroupTransaction") -> None:
    # group_relative_indexes: Dict[Transaction, Dict[Transaction, int]] = {}
    for txn in group.transactions:
        group.group_relative_indexes[txn] = {}

    for txn in group.transactions:
        for offset in txn.relative_indexes:
            other_txn = txn.relative_indexes[offset]
            # other_txn.group_index() = txn.group_index() + offset
            group.group_relative_indexes[other_txn][txn] = offset


# def fill_indexes(group: GroupTransaction):
#     """Calculate the absolute indexes and relative indexes using the indexes from the config.

#     """

#     for txn in group.transactions:
#         if txn.absoulte_index is not None:
#             for offset in txn.relative_indexes:
#                 other_txn = txn.relative_indexes[offset]
#                 other_txn_abs = txn.absoulte_index + offset
#                 if other_txn.absoulte_index is None:
#                     other_txn.absoulte_index = other_txn_abs
#                     group.absolute_indexes[other_txn_abs] = other_txn
#                 # else:
#                 #     if other_txn.absoulte_index != other_txn_abs:
#                         # raise TealerException("Invalid group configuration")
#         for offset in txn.relative_indexes:
#             other_txn = txn.relative_indexes[offset]
#             this_txn_offset = -1 * offset
#             if this_txn_offset not in other_txn.relative_indexes:
#                 other_txn.relative_indexes[this_txn_offset] = txn
