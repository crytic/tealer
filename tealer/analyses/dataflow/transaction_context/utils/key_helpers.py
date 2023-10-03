"""
For a given field multiple types of possible values can be calculated.
The possible values of the field of the transaction
    1. executing the contract/function irrespective of the transaction's group index.
    2. executing the contract when the transaction group index is a particular value.
    3. at a given absolute index irrespective of which contract is executed.
    4. at a given relative index irrespective of which contract is executed.

see transaction_context/__init__.py for more information.
"""

from typing import TYPE_CHECKING, Tuple, Optional, Type

from tealer.teal.instructions.parse_transaction_field import TX_FIELD_TXT_TO_OBJECT
from tealer.analyses.dataflow.transaction_context.utils.group_helpers import (
    IndexType,
    get_index_and_field,
)

if TYPE_CHECKING:
    from tealer.analyses.utils.stack_ast_builder import KnownStackValue
    from tealer.teal.instructions.transaction_field import TransactionField


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


def get_ind_base_for_gtxn_type_keys(analysis_key: str) -> Tuple[int, str]:
    """Calculate the index and base key for the txn_at_index, absolute, relative type keys.

    Args:
        analysis_key: A key

    Returns:
        Returns the transaction index and the base key for the analysis_key.
    """
    # will fail if the key is not a TXN_AT_INDEX key.
    ind, base_key = analysis_key.split("_")[-2:]
    return int(ind), base_key


def get_absolute_index_key(idx: int, base_key: str) -> str:
    """Analysis to represent type (3) information for base_key field

    Args:
        idx: index of the transaction in the group (0 to MAX_GROUP_SIZE - 1)
        base_key: The key used to represent type (1) information of the field.

    Returns:
        Returns the key used to represent type (3) information in the analysis
    """
    return f"GTXN_ABS_{idx:02d}_{base_key}"


def is_absolute_index_key(analysis_key: str) -> bool:
    """Return True if the analysis key represents type (3) information

    Args:
        analysis_key: The key.

    Returns:
        Returns True if analysis_key is a absolute type of key.
    """
    return analysis_key.startswith("GTXN_ABS_")


def get_relative_index_key(offset: int, base_key: str) -> str:
    """Analysis to represent type (2) information for base_key field

    Args:
        offset: index of the transaction in the group  (-(MAX_GROUP_SIZE - 1) to (MAX_GROUP - 1))
        base_key: The key used to represent type (1) information of the field.

    Returns:
        Returns the key used to represent type (4) information in the analysis
    """
    return f"GTXN_RELATIVE_{offset:02d}_{base_key}"


def is_relative_index_key(analysis_key: str) -> bool:
    """Return True if the analysis key represents type (4) information

    Args:
        analysis_key: The key.

    Returns:
        Returns True if analysis_key is a relative type of key.
    """
    return analysis_key.startswith("GTXN_RELATIVE_")


# pylint: disable=too-many-branches
def is_value_matches_key(
    analysis_key: str,
    stack_value: "KnownStackValue",
    key_field: Optional[Type["TransactionField"]] = None,
) -> bool:
    """return True if the stack_value is value of the field tracked by the analysis_key else False.

    Type of keys:
        Self: The value of the current transaction irrespective of its index in the group
        GTXN_AT_INDEX: The value of the transaction field executing this contract when this transaction is at the index.
        Absolute: The field value of the transaction at an absolute index irrespective of the contract being executed at that index.
        Relative: The field value of the transaction at an offset from the current transaction irrespective of the contract being executed at that offset.

    Args:
        analysis_key: The key tracking a field
        stack_value: The value currently being checked
        key_field: The transaction field if it cannot be calculated from the analysis_key

    Returns:
        Returns True if the stack_value is the value of the field tracked by the analysis_key else False.
    """
    value_is_field, value_index, value_field = get_index_and_field(stack_value)
    if not value_is_field:
        return False
    assert value_index is not None and value_field is not None
    if value_index.index_type == IndexType.Unknown:
        return False

    if key_field is None:
        if (
            is_gtxn_at_index_key(analysis_key)
            or is_absolute_index_key(analysis_key)
            or is_relative_index_key(analysis_key)
        ):

            _, field_str = get_ind_base_for_gtxn_type_keys(analysis_key)
        else:
            field_str = analysis_key
        field = TX_FIELD_TXT_TO_OBJECT[field_str]
    else:
        field = key_field

    if not isinstance(value_field, field):
        return False

    if is_gtxn_at_index_key(analysis_key) or is_absolute_index_key(analysis_key):
        # difference between Gtxn_at_key and absolute_index comes from merging of Type(1) information before propagating.
        # It is handled in DataflowTransactionContext._update_gtxn_constraints
        if value_index.index_type != IndexType.Absolute:
            return False

        idx, _ = get_ind_base_for_gtxn_type_keys(analysis_key)
        if value_index.value == idx:
            return True
        return False

    if is_relative_index_key(analysis_key):
        if value_index.index_type != IndexType.Relative:
            return False
        offset, _ = get_ind_base_for_gtxn_type_keys(analysis_key)
        if value_index.value == offset:
            return True
        return False

    # Txn/Self key
    if value_index.index_type == IndexType.Self:
        return True
    return False
