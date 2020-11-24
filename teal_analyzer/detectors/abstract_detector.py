import abc

from teal_analyzer.teal.teal import Teal


class AbstractDetector(metaclass=abc.ABCMeta):  # pylint: disable=too-few-public-methods
    def __init__(self, teal: Teal):
        self.teal = teal

    @abc.abstractmethod
    def detect(self):
        """TODO Documentation"""
        return []
