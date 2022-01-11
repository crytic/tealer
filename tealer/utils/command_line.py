from typing import List, Type

from prettytable import PrettyTable

from tealer.detectors.abstract_detector import (
    DETECTOR_TYPE_TXT,
    AbstractDetector,
    classification_txt,
)
from tealer.printers.abstract_printer import AbstractPrinter


def output_detectors(detector_classes: List[Type[AbstractDetector]]) -> None:
    detectors_list = []
    for detector in detector_classes:
        name = detector.NAME
        description = detector.DESCRIPTION
        detector_type = DETECTOR_TYPE_TXT[detector.TYPE]
        detector_impact = detector.IMPACT
        detector_confidence = detector.CONFIDENCE
        detectors_list.append(
            (name, description, detector_type, detector_impact, detector_confidence)
        )
    table = PrettyTable(["Num", "Check", "What it Detects", "Type", "Impact", "Confidence"])

    # Sort by type, impact, confidence, name, and description
    detectors_list = sorted(
        detectors_list,
        key=lambda element: (element[2], element[3], element[4], element[0], element[1]),
    )
    idx = 1
    for (name, description, detector_type, impact, confidence) in detectors_list:
        table.add_row(
            [
                idx,
                name,
                description,
                detector_type,
                classification_txt[impact],
                classification_txt[confidence],
            ]
        )
        idx = idx + 1
    print(table)


def output_printers(printer_classes: List[Type[AbstractPrinter]]) -> None:
    printers_list = []
    for printer in printer_classes:
        name = printer.NAME
        printer_help = printer.HELP
        printers_list.append((name, printer_help))

    table = PrettyTable(["Num", "Printer", "What it Does"])

    printers_list = sorted(printers_list, key=lambda element: (element[0]))

    for (idx, (name, printer_help)) in enumerate(printers_list, start=1):
        table.add_row([idx, name, printer_help])

    print(table)
