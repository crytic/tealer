from typing import List, Type
from prettytable import PrettyTable

from tealer.detectors.abstract_detector import (
    DETECTOR_TYPE_TXT,
    AbstractDetector,
    classification_txt,
)
from tealer.printers.abstract_printer import AbstractPrinter


def _sort_detector_classes(
    detector_classes: List[Type[AbstractDetector]],
) -> List[Type[AbstractDetector]]:
    # Sort by type, impact, confidence, name and description
    return sorted(
        detector_classes,
        key=lambda element: (element.TYPE, element.IMPACT, element.CONFIDENCE, element.NAME),
    )


def output_detectors(detector_classes: List[Type[AbstractDetector]]) -> None:
    """Print information of given detectors in the form of a table.

    Along with the name of detector, additional information such as what
    does detector tries to find/detect, type of contracts the detector is
    supposed to work on, impact(severity) of the issues detected by it,
    confidence(precision) of the detector are displayed. All this information
    is displayed in a table with appropriate columns. The detectors(rows)
    will be ordered based on the type, impact, confidence such that
    high impact, confidence detectors are displayed first.

    Args:
        detector_classes: list of detector classes whose information
            will be displayed by this function.
    """

    detector_classes = _sort_detector_classes(detector_classes)

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
    """Print information of given printers in the form of a table.

    The name and the description of each printer is displayed. All
    printers are displayed in the form of a table with each row containing
    information about a single printer.

    Args:
        printer_classes: list of printer classes whose information
            will be displayed by this function.
    """

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


# pylint: disable=too-many-locals
def output_to_markdown(
    detector_classes: List[Type[AbstractDetector]],
    printer_classes: List[Type[AbstractPrinter]],
    filter_wiki: str,
) -> None:
    """Print information of detectors and printers in form of markdown table.

    Useful to automatically generate formatted description for available detectors and printers.
    Used to fill README.

    Args:
        detector_classes: List of available detectors.
        printer_classes: List of available printers.
        filter_wiki: Used to filter listed detectors based on NAME. A detector is listed if
            and only if filter_wiki is in its NAME.
    """

    def extract_help(cls: Type[AbstractDetector]) -> str:
        if cls.WIKI_URL == "":
            return cls.DESCRIPTION
        return f"[{cls.DESCRIPTION}]({cls.WIKI_URL})"

    detector_classes = _sort_detector_classes(detector_classes)

    detectors_list = []
    print(f"filter_wiki = {filter_wiki}")
    for detector in detector_classes:
        if not filter_wiki in detector.NAME:
            continue
        name = detector.NAME
        description = extract_help(detector)
        detector_type = DETECTOR_TYPE_TXT[detector.TYPE]
        detector_impact = detector.IMPACT
        detector_confidence = detector.CONFIDENCE
        detectors_list.append(
            (name, description, detector_type, detector_impact, detector_confidence)
        )

    idx = 1
    for (name, description, detector_type, impact, confidence) in detectors_list:
        print(
            f"{idx} | `{name}` | {description} | {detector_type} | {classification_txt[impact]} | {classification_txt[confidence]}"
        )
        idx = idx + 1

    print()
    printers_list = []
    for printer in printer_classes:
        argument = printer.NAME
        help_info = printer.HELP
        printers_list.append((argument, help_info))

    printers_list = sorted(printers_list, key=lambda element: (element[0]))
    idx = 1
    for (argument, help_info) in printers_list:
        print(f"{idx} | `{argument}` | {help_info}")
        idx = idx + 1


def output_wiki(detector_classes: List[Type[AbstractDetector]], filter_wiki: str) -> None:
    """Generate dectector documentation for github wiki.

    Args:
        detector_classes: List of detector classes.
        filter_wiki: filter string used to filter the detector classes. if this string
            is in a detector's name, then that detector is not included in the list.
    """
    detectors_list = _sort_detector_classes(detector_classes)

    for detector in detectors_list:
        if not filter_wiki in detector.NAME:
            continue
        check = detector.NAME
        applicable_to = DETECTOR_TYPE_TXT[detector.TYPE]
        impact = classification_txt[detector.IMPACT]
        confidence = classification_txt[detector.CONFIDENCE]
        title = detector.WIKI_TITLE
        description = detector.WIKI_DESCRIPTION
        exploit_scenario = detector.WIKI_EXPLOIT_SCENARIO
        recommendation = detector.WIKI_RECOMMENDATION

        print(f"\n## {title}")
        print("### Configuration")
        print(f"* Check: `{check}`")
        print(f"* Applicable to: `{applicable_to}`")
        print(f"* Severity: `{impact}`")
        print(f"* Confidence: `{confidence}`")
        print("\n### Description")
        print(description)
        if exploit_scenario:
            print("\n### Exploit Scenario:")
            print(exploit_scenario)
        print("\n### Recommendation")
        print(recommendation)
