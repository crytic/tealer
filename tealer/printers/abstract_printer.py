import abc

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tealer.teal.teal import Teal
    from pathlib import Path


class IncorrectPrinterInitialization(Exception):
    pass


class AbstractPrinter(metaclass=abc.ABCMeta):  # pylint: disable=too-few-public-methods
    NAME = ""
    HELP = ""

    def __init__(self, teal: "Teal"):
        self.teal = teal

        if not self.NAME:
            raise IncorrectPrinterInitialization(
                f"NAME is not initialized {self.__class__.__name__}"
            )

        if not self.HELP:
            raise IncorrectPrinterInitialization(
                f"HELP is not initialized {self.__class__.__name__}"
            )

    @abc.abstractmethod
    def print(self, dest: Optional["Path"] = None) -> None:
        """TODO Documentation"""
