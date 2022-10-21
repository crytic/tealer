"""Entry point of **Tealer** when executed as a script.

Tealer is a static analysis tool for Algorand Smart Contracts written
in TEAL. Tealer takes the source(teal) code of the smart contract as
input, parses and runs detectors, printers on the parsed code.

Detectors are analyzers which go through the parsed code and look for
certain patterns in the program which are of interest to anyone invested
in the security of the contract.

Printers are information summarizers. Printers make finding and evaluating
interesting information related to the contract easier. There's always abundant
information that can be extracted from a smart contract, manually going
through a smart contract for a every tiny bit of information is hard, boringgg
and error prone. Printers make this process of finding information easier and
colorful(will be after adding colors and ofcourse emojis, who doesn't like them <3).

Tealer comes with builtin detectors for finding common security issues and builtin
printers for printing information interesting in general. Additional to that,
tealer allows adding user defined detectors, printers in the form of plugins.
With the plugin support, tealer makes adding new detectors, printers easier and
allows to get away with the minimum amount of work.

Once installed, Tealer adds a command ``tealer`` to the system which will invoke
the ``main()`` function when executed. Tealer comes with few command line
arguments which help users in selecting and running specific detectors, printers
based on the need.

The normal execution flow of tealer is:

* Select the detectors, printers to run on the contract.
    * Collect the list of detectors, printers that come with tealer.
    * Find the plugins installed in the system and collect their detectors, printers.
    * Choose the detectors, printers based on the user command line arguments.
* Read the contract teal source code.
* Parse the source code and generate Teal object.
    * Parse each line of the source as a teal instruction.
    * Construct basic blocks using branch instructions and other rules.
    * Construct Control Flow Graph(CFG) of the contract.
    * Detect basic info like version, mode and create a Teal object.
* Run the selected detectors, printers on the contract.
    * Detectors, Printers are registered, run on the contract using Teal object API.
    * The results are displayed in json format or normally based on command line argument.

The following are few of the command line arguments a user can use to get the best out of tealer:

To know available detectors and printers, both tealer builtins as well as installed plugins:

--list-detectors - prints a pretty table listing the available detectors.
--list-printers - prints a pretty table listing the available printers.

To choose detectors to run from the available list:

--detect - takes in comma separated list of detectors to run. runs all of them if not given.
--exclude - takes in comma separated list of detectors to exclude from running detectors list.
--exclude-stateless - excludes detectors that are supposed to run on stateless smart contracts.
--exclude-stateful - excludes detectors that are supposed to run on stateful smart contracts.

To choose printers to run from the available list:

--print - takes in comma separated list of printers to run. doesn't run any if not given.

"""

import argparse
import inspect
import sys
import json
from pathlib import Path
from typing import List, Any, Type, Tuple, TYPE_CHECKING, Optional

from pkg_resources import iter_entry_points, require  # type: ignore

from tealer.detectors import all_detectors
from tealer.detectors.abstract_detector import AbstractDetector, DetectorType
from tealer.printers import all_printers
from tealer.printers.abstract_printer import AbstractPrinter
from tealer.teal.parse_teal import parse_teal
from tealer.utils.command_line import output_detectors, output_printers
from tealer.utils.output import cfg_to_dot
from tealer.exceptions import TealerException

if TYPE_CHECKING:
    from tealer.teal.teal import Teal
    from tealer.utils.output import SupportedOutput


# from slither: slither/__main__.py
def choose_detectors(
    args: argparse.Namespace, all_detector_classes: List[Type[AbstractDetector]]
) -> List[Type[AbstractDetector]]:
    """Select detectors from available list based on command line arguments.

    Detectors are selected using the values of command line arguments
    ``--detect``, ``--exclude``, ``--exclude-stateless``, ``--exclude-stateful``.

    Args:
        args: Namespace object representing the command line arguments selected
            by the user.
        all_detector_classes: list of all available detectors.

    Returns:
        list of chosen detectors from the available list using the tealer
        command line arguments.

    Raises:
        TealerException: raises exception if name of detector selected using the
            command line argument is not present in the given availble list of
            detectors.
    """

    detectors_to_run = []
    detectors = {d.NAME: d for d in all_detector_classes}

    if args.detectors_to_run == "all":
        detectors_to_run = all_detector_classes
    else:
        for detector in args.detectors_to_run.split(","):
            if detector in detectors:
                detectors_to_run.append(detectors[detector])
            else:
                raise TealerException(f"Error: {detector} is not a detector")

    if args.detectors_to_exclude:
        detectors_to_run = [d for d in detectors_to_run if d.NAME not in args.detectors_to_exclude]

    if args.exclude_stateful:
        detectors_to_run = [d for d in detectors_to_run if d.TYPE != DetectorType.STATEFULL]

    if args.exclude_stateless:
        detectors_to_run = [d for d in detectors_to_run if d.TYPE != DetectorType.STATELESS]

    return detectors_to_run


# from slither: slither/__main__.py
def choose_printers(
    args: argparse.Namespace, all_printer_classes: List[Type[AbstractPrinter]]
) -> List[Type[AbstractPrinter]]:
    """Select printers from available list based on command line arguments.

    printers are selected using the value of command line argument
    ``--print`` which is comma separated list of printer names to run.

    Args:
        args: Namespace object representing the command line arguments selected
            by the user.
        all_detector_classes: list of all available printers.

    Returns:
        list of chosen printers from the available list based on tealer
        command line arguments.

    Raises:
        TealerException: raises exception if name of printer selected using the
            command line argument is not present in the given availble list of
            printers.
    """

    if args.printers_to_run is None:
        return []

    printers = {printer.NAME: printer for printer in all_printer_classes}
    printers_to_run = []
    for printer in args.printers_to_run.split(","):
        if printer in printers:
            printers_to_run.append(printers[printer])
        else:
            raise TealerException(f"{printer} is not a printer")
    return printers_to_run


def parse_args(
    detector_classes: List[Type[AbstractDetector]], printer_classes: List[Type[AbstractPrinter]]
) -> argparse.Namespace:
    """parse command line arguments of tealer.

    Args:
        detector_classes: list of detectors available to tealer. Used to display
            available detectors in tealer command help message.
        printer_classes: list of printers available to tealer. Used to display
            available printers in tealer command help message.

    Returns:
        Namespace object representing the parsed command line arguments.
    """

    parser = argparse.ArgumentParser(
        description="TealAnalyzer",
        usage="tealer program.teal [flag]",
    )

    parser.add_argument("program", help="program.teal")

    parser.add_argument(
        "--version",
        help="displays the current version",
        version=require("tealer")[0].version,
        action="version",
    )

    parser.add_argument(
        "--print-cfg",
        nargs="?",
        help="export cfg in dot format to given file, default cfg.dot",
        const="cfg.dot",
    )

    parser.add_argument(
        "--json-cfg",
        nargs="?",
        help="export cfg in JSON format to given file, default cfg.json",
        const="cfg.json",
    )

    group_detector = parser.add_argument_group("Detectors")
    group_printer = parser.add_argument_group("Printers")
    group_misc = parser.add_argument_group("Additional options")

    group_detector.add_argument(
        "--list-detectors",
        help="List available detectors",
        action=ListDetectors,
        nargs=0,
        default=False,
    )

    available_detectors = ", ".join(d.NAME for d in detector_classes)
    group_detector.add_argument(
        "--detect",
        help="Comma-separated list of detectors, defaults to all, "
        f"available detectors: {available_detectors}",
        action="store",
        dest="detectors_to_run",
        default="all",
    )

    group_detector.add_argument(
        "--exclude",
        help="Comma-separated list of detectors that should be excluded.",
        action="store",
        dest="detectors_to_exclude",
        default=None,
    )

    group_detector.add_argument(
        "--exclude-stateless",
        help="Exclude detectors of stateless type",
        action="store_true",
        default=False,
    )

    group_detector.add_argument(
        "--exclude-stateful",
        help="Exclude detectors of stateful type",
        action="store_true",
        default=False,
    )

    group_detector.add_argument(
        "--all-paths-in-one",
        help="highlights all the vunerable paths in a single file.",
        action="store_true",
        default=False,
    )

    group_printer.add_argument(
        "--list-printers",
        help="List available printers",
        action=ListPrinters,
        nargs=0,
        default=False,
    )

    available_printers = ", ".join(p.NAME for p in printer_classes)
    group_printer.add_argument(
        "--print",
        help="Comma-separated list of printers, defaults to None,"
        f" available printers: {available_printers}",
        action="store",
        dest="printers_to_run",
        default=None,
    )

    group_misc.add_argument(
        "--json",
        help='Export the results as a JSON file ("--json -" to export to stdout)',
        action="store",
        default=None,
    )

    group_misc.add_argument(
        "--dest",
        help="destination to save the output files, defaults to current directory",
        action="store",
        default=".",
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    return args


# from slither: slither/__main__.py
class ListDetectors(argparse.Action):  # pylint: disable=too-few-public-methods
    """Argparse Action class to display available detectors.

    This Action will be invoked if ``--list-detectors`` command line
    argument is selected. Upon invocation, prints a table listing the available
    detectors along with their name, description, type, impact and confidence.
    """

    def __call__(
        self, parser: argparse.ArgumentParser, *args: Any, **kwargs: Any
    ) -> None:  # pylint: disable=signature-differs
        detectors, _ = get_detectors_and_printers()
        output_detectors(detectors)
        parser.exit()


# from slither: slither/__main__.py
class ListPrinters(argparse.Action):  # pylint: disable=too-few-public-methods
    """Argparse Action class to display available printers.

    This Action will be invoked if ``--list-printers`` command line
    argument is selected. Upon invocation, prints a table listing the available
    printers along with their name and description.
    """

    def __call__(
        self, parser: argparse.ArgumentParser, *args: Any, **kwargs: Any
    ) -> None:  # pylint: disable=signature-differs
        _, printers = get_detectors_and_printers()
        output_printers(printers)
        parser.exit()


def collect_plugins() -> Tuple[List[Type[AbstractDetector]], List[Type[AbstractPrinter]]]:
    """collect detectors and printers installed in form of plugins.

    plugins are collected using the entry point group `teal_analyzer.plugin`.
    The entry point of each plugin has to return tuple containing list of detectors and
    list of printers defined in the plugin when called.

    Returns:
        (Tuple[List[Type[AbstractDetector]], List[Type[AbstractPrinter]]]): detectors and
        printers added in the form of plugins.

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


def handle_print_cfg(args: argparse.Namespace, teal: "Teal") -> None:
    """Util function to handle print cfg command line argument.

    This function is invoked when command line argument ``--print-cfg``
    is used by the user to export the CFG of the contract in dot format.

    Args:
        args: Namespace object representing the command line arguments selected
            by the user.
        teal: Teal object representing the contract being analyzed.
    """

    filename = args.print_cfg
    if not filename.endswith(".dot"):
        filename += ".dot"

    filename = Path(args.dest) / Path(filename)
    print(f"\nCFG exported to file: {filename}")
    cfg_to_dot(teal.bbs, filename)


def handle_detectors_and_printers(
    args: argparse.Namespace,
    teal: "Teal",
    detectors: List[Type[AbstractDetector]],
    printers: List[Type[AbstractPrinter]],
) -> Tuple[List["SupportedOutput"], List]:
    """Util function to register and run detectors, printers.

    Args:
        args: Namespace object representing the command line arguments selected
            by the user.
        teal: Teal object representing the contract being analyzed.
        detectors: Detector classes to register and run.
        printers: Printer classes to register and run.

    Returns:
        returns list of detector results and list of printer results.
    """

    for detector_cls in detectors:
        teal.register_detector(detector_cls)

    for printer_cls in printers:
        teal.register_printer(printer_cls)

    return teal.run_detectors(), teal.run_printers(Path(args.dest))


def handle_output(
    args: argparse.Namespace,
    detector_results: List["SupportedOutput"],
    _printer_results: List,
    error: Optional[str],
) -> None:
    """Util function to output tealer results.

    Tealer supports displaying the results in json format or raw format.
    Format is decided on whether ``--json`` command line argument is set or not.

    Args:
        args: Namespace object representing the command line arguments selected
            by the user.
        detector_results: results of running the selected detectors.
        _printer_results: results of running the selected printers.
    """

    if args.json is None:

        if error is not None:
            print(f"Error: {error}")
            sys.exit(-1)

        for output in detector_results:
            output.write_to_files(args.dest, args.all_paths_in_one)
    else:
        json_results = [output.to_json() for output in detector_results]

        json_output = {
            "success": error is not None,
            "error": error,
            "result": json_results,
        }

        if args.json == "-":
            print(json.dumps(json_output, indent=2))
        else:
            filename = Path(args.dest) / Path(args.json)
            print(f"json output is written to {filename}")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(json_output, indent=2))


def main() -> None:
    """Entry point of the tealer tool.

    This function is called when tealer command is executed or tealer is
    executed as a script. This function directs execution flow of the tool
    based on the command line arguments given by the user.
    """

    detector_classes, printer_classes = get_detectors_and_printers()
    args = parse_args(detector_classes, printer_classes)

    detector_classes = choose_detectors(args, detector_classes)
    printer_classes = choose_printers(args, printer_classes)

    results_detectors: List["SupportedOutput"] = []
    _results_printers: List = []
    error = None
    try:
        with open(args.program, encoding="utf-8") as f:
            print(f"Analyzing {args.program}")
            teal = parse_teal(f.read())

        if args.print_cfg is not None:
            handle_print_cfg(args, teal)
            return

        if args.json_cfg is not None:
            bbs = [bb.to_dict() for bb in teal.bbs]
            subs = [
                {
                    "label": sub.blocks[0].entry_instr.label,
                    "input": sub.input_types,
                    "output": sub.output_types,
                }
                for sub in teal.subroutines
            ]
            with (open(args.json_cfg, "w") as file):
                import json

                json.dump({"blocks": bbs, "subroutines": subs}, file)

        results_detectors, _results_printers = handle_detectors_and_printers(
            args, teal, detector_classes, printer_classes
        )

    except TealerException as e:
        error = str(e)

    handle_output(args, results_detectors, _results_printers, error)


if __name__ == "__main__":
    main()
