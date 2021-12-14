from typing import List

from prettytable import PrettyTable

from tealer.detectors.abstract_detector import DETECTOR_TYPE_TXT, AbstractDetector


def output_detectors(detector_classes: List[AbstractDetector]) -> None:
    detectors_list = []
    for detector in detector_classes:
        name = detector.NAME
        description = detector.DESCRIPTION
        detector_type = DETECTOR_TYPE_TXT[detector.TYPE]
        detectors_list.append((name, description, detector_type))
    table = PrettyTable(["Num", "Check", "What it Detects", "Type"])

    # Sort by type, name, and description
    detectors_list = sorted(
        detectors_list, key=lambda element: (element[2], element[0], element[1])
    )
    idx = 1
    for (name, description, detector_type) in detectors_list:
        table.add_row([idx, name, description, detector_type])
        idx = idx + 1
    print(table)
