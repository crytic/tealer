# pylint: disable=too-few-public-methods
from typing import Type, cast
from dataclasses import dataclass


class DataclassMeta(type):
    def __new__(cls, name, bases, classdict): # type: ignore
        new_cls = super().__new__(cls, name, bases, classdict)
        return cast(DataclassMeta, dataclass(frozen=True)(new_cls))


class GlobalField(metaclass=DataclassMeta):
    version: int = 1

    def __str__(self) -> str:
        return self.__class__.__qualname__


class GroupSize(GlobalField):
    pass


class MinTxnFee(GlobalField):
    pass


class ZeroAddress(GlobalField):
    pass


class MinBalance(GlobalField):
    pass


class MaxTxnLife(GlobalField):
    pass


class LogicSigVersion(GlobalField):
    version: int = 2


class Round(GlobalField):
    version: int = 2


class LatestTimestamp(GlobalField):
    version: int = 2


class CurrentApplicationID(GlobalField):
    version: int = 2


class CreatorAddress(GlobalField):
    version: int = 3


class CurrentApplicationAddress(GlobalField):
    version: int = 5


class GroupID(GlobalField):
    version: int = 5
