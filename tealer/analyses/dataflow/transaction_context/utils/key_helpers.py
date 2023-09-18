"""

For a given field multiple types of possible values can be calculated.
The possible values of the field of the transaction
    1. executing the contract/function irrespective of the transaction's group index.
    2. executing the contract when the transaction group index is a particular value.
    3. at a given absolute index irrespective of which contract is executed.
    4. at a given relative index irrespective of which contract is executed.

see transaction_context/__init__.py for more information.
"""

from typing import TYPE_CHECKING, Tuple

from tealer.teal.instructions.instructions import (
    Txn,
    Gtxn,
)
from tealer.teal.instructions.parse_transaction_field import TX_FIELD_TXT_TO_OBJECT

if TYPE_CHECKING:
    from tealer.teal.instructions.instructions import Instruction


def get_gtxn_at_index_key(idx: int, base_key: str) -> str:
    """Analysis to represent type (2) information for base_key field

    Args:
        idx: index of the transaction in the group (0 to MAX_GROUP_SIZE - 1)
        base_key: The key used to represent type (1) information of the field.

    Returns:
        Returns the key used to represent type (2) information in the analysis
    """
    return f"GTXN_AT_INDEX_{idx:02d}_{base_key}"


def is_gtxn_at_index_key(analysis_key: str) -> bool:
    """Return True if the analysis key represents type (2) information

    Args:
        analysis_key: The key.

    Returns:
        Returns True if analysis_key starts with "GTXN_AT_INDEX" or else False.
    """
    return analysis_key.startswith("GTXN_AT_INDEX")


def get_ind_base_for_gtxn_at_key(analysis_key: str) -> Tuple[int, str]:
    """Calculate the index and base key for the txn_at_index type key.

    Args:
        analysis_key: A key used to represent type (2) information.

    Returns:
        Returns the transaction index and the base key for the analysis_key.
    """
    # will fail if the key is not a TXN_AT_INDEX key.
    ind, base_key = analysis_key.split("_")[-2:]
    return int(ind), base_key


# This function is not used currently. Will be used when group transaction support is added
# for absolute indexes.
def get_absolute_index_key(idx: int, base_key: str) -> str:
    """Analysis to represent type (3) information for base_key field

    Args:
        idx: index of the transaction in the group (0 to MAX_GROUP_SIZE - 1)
        base_key: The key used to represent type (1) information of the field.

    Returns:
        Returns the key used to represent type (3) information in the analysis
    """
    return f"GTXN_ABS_{idx:02d}_{base_key}"


# This function is not used currently. Will be used when group transaction support is added
# for relative indexes.
def get_relative_index_key(offset: int, base_key: str) -> str:
    """Analysis to represent type (2) information for base_key field

    Args:
        offset: index of the transaction in the group  (-(MAX_GROUP_SIZE - 1) to (MAX_GROUP - 1))
        base_key: The key used to represent type (1) information of the field.

    Returns:
        Returns the key used to represent type (4) information in the analysis
    """
    return f"GTXN_RELATIVE_{offset:02d}_{base_key}"


# TODO: The function is copied as it is from DataflowTransactionContext. Update the implementation
# when adding support for absolute indices and relative indices.
def is_txn_or_gtxn(analysis_key: str, ins: "Instruction") -> bool:
    """return True if ins is of form txn {key} or gtxn {ind} {key} else False

    "key" should be string representation of the field. e.g if field is RekeyTo, then
    key should also be "RekeyTo".

    Args:
        analysis_key: The key used to represent values of a field in the analysis.
        ins: An instruction.

    Returns:
        Returns True if the instruction :ins: access the value of the field tracked by
        the key :key:.
    """
    if is_gtxn_at_index_key(analysis_key):
        idx, field = get_ind_base_for_gtxn_at_key(analysis_key)
        return (
            isinstance(ins, Gtxn)
            and ins.idx == idx
            and isinstance(ins.field, TX_FIELD_TXT_TO_OBJECT[field])
        )
    return isinstance(ins, Txn) and isinstance(ins.field, TX_FIELD_TXT_TO_OBJECT[analysis_key])
