from typing import Tuple, Type, List, TYPE_CHECKING

from tealer_plugin.detectors.example import Example

if TYPE_CHECKING:
    from tealer.detectors.abstract_detector import AbstractDetector
    from tealer.printers.abstract_printer import AbstractPrinter


def make_plugin() -> Tuple[List[Type["AbstractDetector"]], List[Type["AbstractPrinter"]]]:
    # import and add detectors, printers defined to the below lists
    plugin_detectors: List[Type["AbstractDetector"]] = [Example]
    plugin_printers: List[Type["AbstractPrinter"]] = []

    return plugin_detectors, plugin_printers
