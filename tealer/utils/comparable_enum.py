"""Defines a comparable enum class.

This module implements a comparable enum class which extends
``Enum`` class with capabilities for comparing two symbolic names
of defined in the same enumeration.

Classes:
    ComparableEnum: Enum subclass with additional comparison capability
        i.e enumerations defined with ComparableEnum can be compared.
"""

from enum import Enum

from typing import Any


# from slither: slither/utils/comparable_enum.py
class ComparableEnum(Enum):
    """Class to represent comparable enum types."""

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ComparableEnum):
            return self.value == other.value
        return False

    def __ne__(self, other: Any) -> bool:
        if isinstance(other, ComparableEnum):
            return self.value != other.value
        return False

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, ComparableEnum):
            return self.value < other.value
        return False

    def __repr__(self) -> str:
        return f"{self.value}"

    def __hash__(self) -> int:
        return hash(self.value)
