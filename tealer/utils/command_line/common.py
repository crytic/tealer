import inspect

from typing import List, Type, Tuple
from pkg_resources import iter_entry_points  # type: ignore

from tealer.detectors.abstract_detector import (
    AbstractDetector,
)
from tealer.printers.abstract_printer import AbstractPrinter
from tealer.detectors import all_detectors
from tealer.printers import all_printers
from tealer.exceptions import TealerException


def collect_plugins() -> Tuple[List[Type[AbstractDetector]], List[Type[AbstractPrinter]]]:
    """collect detectors and printers installed in form of plugins.

    plugins are collected using the entry point group `teal_analyzer.plugin`.
    The entry point of each plugin has to return tuple containing list of detectors and
    list of printers defined in the plugin when called.

    Returns:
        (Tuple[List[Type[AbstractDetector]], List[Type[AbstractPrinter]]]): detectors and
        printers added in the form of plugins.

    Raises:
        TealerException: raises exception if a plugin's detector is not a subclass of AbstractDetector
            or if a plugin's printer is not a subclass of AbstractPrinter.
    """
    detector_classes: List[Type[AbstractDetector]] = []
    printer_classes: List[Type[AbstractPrinter]] = []
    for entry_point in iter_entry_points(group="teal_analyzer.plugin", name=None):
        make_plugin = entry_point.load()

        plugin_detectors, plugin_printers = make_plugin()
        detector = None
        if not all(issubclass(detector, AbstractDetector) for detector in plugin_detectors):
            raise TealerException(
                f"Error when loading plugin {entry_point}, {detector} is not a detector"
            )
        printer = None
        if not all(issubclass(printer, AbstractPrinter) for printer in plugin_printers):
            raise TealerException(
                f"Error when loading plugin {entry_point}, {printer} is not a printer"
            )

        detector_classes += plugin_detectors
        printer_classes += plugin_printers

    return detector_classes, printer_classes


# from slither: slither/__main__.py
def get_detectors_and_printers() -> Tuple[
    List[Type[AbstractDetector]], List[Type[AbstractPrinter]]
]:
    """Get list of detectors and printers available to tealer.

    Detectors, Printers are considered available to tealer either if they
    are defined in the tealer itself or if they are defined in one of the
    tealer plugins installed in the system.

    Returns:
        list of detectors, list of printers defined in tealer and plugins
        combined.
    """

    detector_classes = [getattr(all_detectors, name) for name in dir(all_detectors)]
    detector_classes = [
        d for d in detector_classes if inspect.isclass(d) and issubclass(d, AbstractDetector)
    ]

    printer_classes = [getattr(all_printers, name) for name in dir(all_printers)]
    printer_classes = [
        d for d in printer_classes if inspect.isclass(d) and issubclass(d, AbstractPrinter)
    ]

    plugins_detectors, plugins_printers = collect_plugins()

    detector_classes += plugins_detectors
    printer_classes += plugins_printers

    return detector_classes, printer_classes
