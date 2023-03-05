"""Defines abstract base class for printers in tealer.

This module contains implementation of abstract class which
defines the attributes, common methods and must implement methods
of printers. All printers in tealer must inherit from this class
and set attributes, override abstract methods.

Classes:
    AbstractPrinter: Abstract class to represent printers in tealer.
"""

import abc

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tealer.teal.teal import Teal
    from pathlib import Path


class IncorrectPrinterInitialization(Exception):
    """Exception class to represent incorrect printer intialization.

    This exception will be used if any of the necessary attributes
    of the AbstractPrinter are not set by the inheriting printer class.
    """


class AbstractPrinter(metaclass=abc.ABCMeta):  # pylint: disable=too-few-public-methods
    """Abstract class to represent printers in tealer.

    All printers in tealer must inherit from this class and override the
    abstract methods with functionality specific to them. This class defines
    the api methods that must be implemented by every printers. ``print``
    method of each printer will be called to execute the printer. Every
    printer must implement ``print`` method.

    Attrributes:
        NAME: Name of the printer. printer name will be used while
            displaying information about the printer and also for selecting
            the printer from command line.
        HELP: Description of the printer.

    Args:
        teal: Teal instance representing the contract. Printer will run on
            the contract represented by :teal:

    Raises:
        IncorrectPrinterInitialization: Exception is raised if NAME, HELP
            attributes are not set by the inheriting printer class.
    """

    NAME = ""
    HELP = ""
    WIKI_URL = ""

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

        if not self.WIKI_URL:
            raise IncorrectPrinterInitialization(
                f"WIKI_URL is not initialized for {self.__class__.__name__}"
            )

    @abc.abstractmethod
    def print(self) -> None:
        """entry method of the printer.

        All printers must override this method with the functionality
        specific to them. This method is the entry point of the printer
        and will be called to execute it.
        """
