from typing import Tuple, Type, List, TYPE_CHECKING

from tealer_rekey_plugin.detectors.rekeyto_stateless import CanRekey

if TYPE_CHECKING:
    from tealer.detectors.abstract_detector import AbstractDetector
    from tealer.printers.abstract_printer import AbstractPrinter


def make_plugin() -> Tuple[List[Type["AbstractDetector"]], List[Type["AbstractPrinter"]]]:
    plugin_detectors: List[Type["AbstractDetector"]] = [CanRekey]
    plugin_printers: List[Type["AbstractPrinter"]] = []

    return plugin_detectors, plugin_printers
