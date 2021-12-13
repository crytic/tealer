import argparse
import inspect
import sys
from pathlib import Path
from typing import List, Any

from tealer.detectors import all_detectors
from tealer.detectors.abstract_detector import AbstractDetector
from tealer.teal.parse_teal import parse_teal
from tealer.utils.command_line import output_detectors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="TealAnalyzer",
        usage="teal_analyazer program.teal [flag]",
    )

    parser.add_argument("program", help="program.teal")

    parser.add_argument(
        "--print-cfg",
        help="Print the cfg",
        action="store_true",
    )

    parser.add_argument(
        "--list-detectors",
        help="List available detectors",
        action=ListDetectors,
        nargs=0,
        default=False,
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    return args


class ListDetectors(argparse.Action):  # pylint: disable=too-few-public-methods
    def __call__(
        self, parser: argparse.ArgumentParser, *args: Any, **kwargs: Any
    ) -> None:  # pylint: disable=signature-differs
        detectors = get_detectors()
        output_detectors(detectors)
        parser.exit()


def get_detectors() -> List[Any]:
    detectors = [getattr(all_detectors, name) for name in dir(all_detectors)]
    detectors = [d for d in detectors if inspect.isclass(d) and issubclass(d, AbstractDetector)]
    return detectors


def main() -> None:

    args = parse_args()

    with open(args.program) as f:
        print(f"Analyze {args.program}")
        teal = parse_teal(f.read())

    if args.print_cfg:
        print("CFG exported: cfg.dot")
        # teal.bbs_to_dot(Path("cfg.dot"))
        teal.render_cfg(Path("cfg.dot"))

    else:
        for Cls in get_detectors():
            d = Cls(teal)
            for r in d.detect():
                print(r)


if __name__ == "__main__":
    main()
