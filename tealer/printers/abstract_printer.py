import abc

from tealer.teal.teal import Teal


class AbstractPrinter(metaclass=abc.ABCMeta):  # pylint: disable=too-few-public-methods
    def __init__(self, teal: Teal):
        self.teal = teal

    @abc.abstractmethod
    def print(self) -> None:
        """TODO Documentation"""
