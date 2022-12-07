from typing import List, Optional

from tealer.utils.teal_enums import ALL_TRANSACTION_TYPES
from tealer.exceptions import TealerException
from tealer.utils.algorand_constants import MAX_GROUP_SIZE


class BlockTransactionContext:  # pylint: disable=too-few-public-methods

    _group_transactions_context: Optional[List["BlockTransactionContext"]] = None

    any_rekeyto: bool = True  # default to any rekeyto address
    none_rekeyto: bool = False

    any_closeto: bool = True  # default to any rekeyto address
    none_closeto: bool = False

    any_assetcloseto: bool = True  # default to any rekeyto address
    none_assetcloseto: bool = False

    def __init__(self, tail: bool = False) -> None:
        if not tail:
            self._group_transactions_context = [BlockTransactionContext(True) for _ in range(16)]

        # set default values
        if tail:
            # information from gtxn {i} instructions.
            self.group_indices = []
            self.group_sizes = []
        else:
            self.group_sizes = list(range(1, MAX_GROUP_SIZE + 1))
            self.group_indices = list(range(0, MAX_GROUP_SIZE))
        self.transaction_types = list(ALL_TRANSACTION_TYPES)
        self.rekeyto: List[str] = []
        self.closeto: List[str] = []
        self.assetcloseto: List[str] = []

    def gtxn_context(self, txn_index: int) -> "BlockTransactionContext":
        """context information collected from gtxn {txn_index} field instructions"""
        if self._group_transactions_context is None:
            raise TealerException()
        if txn_index >= MAX_GROUP_SIZE:
            raise TealerException()
        return self._group_transactions_context[txn_index]
