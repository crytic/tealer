import argparse
import sys
from pathlib import Path

from tealer.detectors.groupsize import MissingGroupSize
from tealer.detectors.rekeyto import MissingRekeyTo
from tealer.printers.can_delete import DeleteApplication
from tealer.printers.can_update import UpdateApplication
from tealer.teal.parse_teal import parse_teal


def parse_args():
    parser = argparse.ArgumentParser(
        description="TealAnalyzer", usage="teal_analyazer program.teal [flag]",
    )

    parser.add_argument("program", help="program.teal")

    parser.add_argument(
        "--print-cfg", help="Print the cfg", action="store_true",
    )

    parser.add_argument(
        "--print-delete", help="Print all the paths that can delete the app", action="store_true",
    )

    parser.add_argument(
        "--print-update", help="Print all the paths that can update the app", action="store_true",
    )

    parser.add_argument(
        "--check-rekeyto",
        help="Check if some paths use a group transaction without checking for rekeyto",
        action="store_true",
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    return args


def main():

    args = parse_args()

    with open(args.program) as f:
        print(f"Analyze {args.program}")
        teal = parse_teal(f.read())

    if args.print_cfg:
        print("CFG exported: cfg.dot")
        teal.bbs_to_dot(Path("cfg.dot"))

    elif args.print_update:
        d = UpdateApplication(teal)
        d.print()

    elif args.print_delete:
        d = DeleteApplication(teal)
        d.print()

    else:
        for Cls in [MissingGroupSize, MissingRekeyTo]:
            d = Cls(teal)
            for r in d.detect():
                print(r)


if __name__ == "__main__":
    main()
