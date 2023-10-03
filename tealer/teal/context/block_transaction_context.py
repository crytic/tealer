from typing import List, Optional, Dict
from dataclasses import dataclass, field

from tealer.exceptions import TealerException
from tealer.utils.teal_enums import ALL_TRANSACTION_TYPES
from tealer.utils.algorand_constants import MAX_GROUP_SIZE, MAX_UINT64


@dataclass
class AddrFieldValue:
    any_addr: bool = True
    no_addr: bool = False
    possible_addr: List[str] = field(default_factory=list)


class BlockTransactionContext:  # pylint: disable=too-few-public-methods, too-many-instance-attributes

    _gtxn_at_index_context: Optional[List["BlockTransactionContext"]] = None
    _abs_context: Optional[List["BlockTransactionContext"]] = None
    _relative_context: Optional[Dict[int, "BlockTransactionContext"]] = None

    def __init__(self, tail: bool = False) -> None:
        if not tail:
            self._gtxn_at_index_context = [
                BlockTransactionContext(True) for _ in range(MAX_GROUP_SIZE)
            ]
            self._abs_context = [BlockTransactionContext(True) for _ in range(MAX_GROUP_SIZE)]
            self._relative_context = {
                offset: BlockTransactionContext(True)
                for offset in range(-(MAX_GROUP_SIZE - 1), MAX_GROUP_SIZE)
                if offset != 0
            }

        # set default values
        if tail:
            # information from gtxn {i} instructions.
            self.group_indices = []
            self.group_sizes = []
            self.is_gtxn_context = True
        else:
            self.group_sizes = list(range(1, MAX_GROUP_SIZE + 1))
            self.group_indices = list(range(0, MAX_GROUP_SIZE))
            self.is_gtxn_context = False
        self.transaction_types = list(ALL_TRANSACTION_TYPES)
        self.rekeyto: AddrFieldValue = AddrFieldValue()
        self.closeto: AddrFieldValue = AddrFieldValue()
        self.assetcloseto: AddrFieldValue = AddrFieldValue()
        self.sender: AddrFieldValue = AddrFieldValue()
        self.max_fee: int = MAX_UINT64
        self.max_fee_unknown: bool = False  # True if max possible fee is bounded and unknown

    def gtxn_context(self, txn_index: int) -> "BlockTransactionContext":
        """context information collected from gtxn {txn_index} field instructions

        Args:
            txn_index: Transaction index.

        Returns:
            context information collected from "gtxn {txn_index} field" instructions.
            The information is of the txn executing this contract when it's index in the group
            is :txn_index:

        Raises:
            TealerException: Raises error if gtxn_context of a gtxn_context is accessed or if the
                transaction index is greater than MAX_GROUP_SIZE.
        """
        if self._gtxn_at_index_context is None:
            raise TealerException()
        if txn_index >= MAX_GROUP_SIZE:
            raise TealerException()
        return self._gtxn_at_index_context[txn_index]

    def absolute_context(self, txn_index: int) -> "BlockTransactionContext":
        """context information of the transaction at `txn_index`

        Args:
            txn_index: Transaction index

        Returns:
            The context information of the transaction at the give absolute index.

        Raises:
            TealerException: Raises error if abs_context of a tail context is accessed or if the transaction
                index is greater than MAX_GROUP_SIZE.
        """
        if self._abs_context is None:
            raise TealerException()
        if txn_index >= MAX_GROUP_SIZE:
            raise TealerException()
        return self._abs_context[txn_index]

    def relative_context(self, offset: int) -> "BlockTransactionContext":
        """context information of the transaction at `offset` from the current transaction

        Args:
            offset: Transaction offset

        Returns:
            The context information of the transaction at the offset from the executing this contract

        Raises:
            TealerException: Raises error if r of a tail context is accessed or if the offset is not valid
        """
        if self._relative_context is None:
            raise TealerException()
        if offset not in self._relative_context:
            raise TealerException()
        return self._relative_context[offset]
