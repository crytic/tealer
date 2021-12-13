from enum import Enum


# pylint: disable=comparison-with-callable
# Copy from https://github.com/crytic/slither/blob/master/slither/utils/comparable_enum.py
from typing import Any


class ComparableEnum(Enum):
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
        return "%s" % (str(self.value))

    def __hash__(self) -> int:
        return hash(self.value)
