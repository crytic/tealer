from typing import List, Optional

from tealer.exceptions import TealerException


class BlockTransactionContext:  # pylint: disable=too-few-public-methods

    _group_transactions_context: Optional[List["BlockTransactionContext"]] = None

    def __init__(self, tail: bool = False) -> None:
        if not tail:
            self._group_transactions_context = [BlockTransactionContext(True) for _ in range(16)]

        # set default values
        self.group_sizes = list(range(1, 17))

    def gtxn_context(self, txn_index: int) -> "BlockTransactionContext":
        """context information collected from gtxn {txn_index} field instructions"""
        if self._group_transactions_context is None:
            raise TealerException()
        if txn_index >= 16:
            raise TealerException()
        return self._group_transactions_context[txn_index]
