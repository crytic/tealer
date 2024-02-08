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
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import List, Any, Type, Tuple, TYPE_CHECKING, Optional, Union, Sequence

from importlib.metadata import version

from tealer.detectors.abstract_detector import AbstractDetector, DetectorType
from tealer.exceptions import TealerException
from tealer.printers.abstract_printer import AbstractPrinter
from tealer.utils.algoexplorer import (
    get_application_using_app_id,
    logic_sig_from_contract_account,
    logic_sig_from_txn_id,
)
from tealer.utils.command_line.command_output import (
    output_detectors,
    output_printers,
    output_to_markdown,
    output_wiki,
)
from tealer.utils.command_line.common import (
    get_detectors_and_printers,
    validate_command_line_options,
    # handle_detect,
    init_tealer_from_single_contract,
    init_tealer_from_config,
)
from tealer.utils.command_line.group_config import (
    read_config_from_file,
)
from tealer.utils.output import ROOT_OUTPUT_DIRECTORY, ExecutionPaths
from tealer.utils.regex.regex import run_regex
from tealer.utils.teal_enums import ExecutionMode

if TYPE_CHECKING:
    from tealer.teal.teal import Teal
    from tealer.utils.output import ListOutput


# from slither: slither/__main__.py
def choose_detectors(
    args: argparse.Namespace,
    all_detector_classes: List[Type[AbstractDetector]],
    teal: Optional["Teal"] = None,
) -> List[Type[AbstractDetector]]:
    """Select detectors from available list based on command line arguments.

    Detectors are selected using the values of command line arguments
    ``--detect``, ``--exclude``, ``--exclude-stateless``, ``--exclude-stateful``.
    If the default detectors are run, exclude the stateless detector for stateful app, and stateful detectors
    for stateless code. The detectors can still be executed if they are added manually through --detect

    Args:
        args: Namespace object representing the command line arguments selected
            by the user.
        all_detector_classes: list of all available detectors.
        teal: The Teal contract.

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

    if args.detectors_to_run is None:
        detectors_to_run = all_detector_classes
        # IF there is no detectors provided:
        # - Stateful: run everything expect the stateless detectors
        # - Stateless: run only stateless and stateless & stateful
        if teal is not None and teal.mode == ExecutionMode.STATEFUL:
            detectors_to_run = [d for d in detectors_to_run if d.TYPE != DetectorType.STATELESS]
        if teal is not None and teal.mode == ExecutionMode.STATELESS:
            detectors_to_run = [
                d
                for d in detectors_to_run
                if d.TYPE in [DetectorType.STATELESS, DetectorType.STATELESS_AND_STATEFULL]
            ]
    else:
        for detector in args.detectors_to_run.split(","):
            detector_name = detector.strip()
            if detector_name in detectors:
                detectors_to_run.append(detectors[detector_name])
            else:
                raise TealerException(f"Error: {detector_name} is not a detector")

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
        all_printer_classes: list of all available printers.

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


def generic_options(parser: argparse.ArgumentParser) -> None:
    """
    Add the generic cli flags options

    Args:
        parser: the parser to update
    """

    parser.add_argument(
        "--contracts",
        help="List of files/directories to search for .teal files",
        action="store",
        nargs="+",
    )

    parser.add_argument(
        "--group-config",
        help="The group configuration file",
        action="store",
    )

    parser.add_argument(
        "--network",
        help='Algorand network to fetch the contract from, ("mainnet" or "testnet"). defaults to "mainnet".',
        action="store",
        default="mainnet",
    )


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
        usage="tealer [detect | print | regex ] --contracts ...",
    )

    subparsers = parser.add_subparsers(dest="subcommand")

    group_detector = subparsers.add_parser("detect", help="Run the detectors")
    generic_options(group_detector)

    available_printers = ", ".join(p.NAME for p in printer_classes)
    group_printer = subparsers.add_parser("print", help="Use a printer")
    group_printer.add_argument(
        "printers_to_run",
        action="store",
        help=f"Comma-separated list of printers to use, defaults to None. Available printers: {available_printers}",
    )
    generic_options(group_printer)

    group_regex = subparsers.add_parser("regex", help="Use the regex engine")
    group_regex.add_argument("regex_file", action="store", help="Regular expression file")
    generic_options(group_regex)

    group_misc = parser.add_argument_group("Additional options")

    parser.add_argument(
        "--version",
        help="displays the current version",
        version=version("tealer"),
        action="version",
    )

    available_detectors = ", ".join(d.NAME for d in detector_classes)

    group_detector.add_argument(
        "--detectors",
        help="Comma-separated list of detectors, defaults to all, "
        f"available detectors: {available_detectors}",
        action="store",
        dest="detectors_to_run",
        default=available_detectors,
    )

    group_detector.add_argument(
        "--exclude",
        help="Comma-separated list of detectors that should be excluded.",
        action="store",
        dest="detectors_to_exclude",
        nargs="+",  # Allows multiple arguments
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
        "--filter-paths",
        help="Excludes execution paths matching the regex from detector's output.",
        action="store",
        dest="filter_paths",
        default=None,
    )

    group_detector.add_argument(
        "--list-detectors",
        help="List available detectors",
        action=ListDetectors,
        nargs=0,
        default=False,
    )

    group_misc.add_argument(
        "--json",
        help='Export the results as a JSON file ("--json -" to export to stdout)',
        action="store",
        default=None,
    )

    group_printer.add_argument(
        "--list-printers",
        help="List available printers",
        action=ListPrinters,
        nargs=0,
        default=False,
    )

    parser.add_argument("--debug", help=argparse.SUPPRESS, action="store_true", default=False)
    parser.add_argument("--markdown", help=argparse.SUPPRESS, action=OutputMarkdown, default=False)

    parser.add_argument(
        "--wiki-detectors", help=argparse.SUPPRESS, action=OutputWiki, default=False
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


class OutputMarkdown(argparse.Action):  # pylint: disable=too-few-public-methods
    def __call__(
        self,
        parser: Any,
        args: Any,
        values: Optional[Union[str, Sequence[Any]]],
        option_string: Any = None,
    ) -> None:
        detectors, printers = get_detectors_and_printers()
        assert isinstance(values, str)
        output_to_markdown(detectors, printers, values)
        parser.exit()


class OutputWiki(argparse.Action):  # pylint: disable=too-few-public-methods
    def __call__(
        self,
        parser: Any,
        args: Any,
        values: Optional[Union[str, Sequence[Any]]],
        option_string: Any = None,
    ) -> None:
        detectors, _ = get_detectors_and_printers()
        assert isinstance(values, str)
        output_wiki(detectors, values)
        parser.exit()


def handle_output(
    args: argparse.Namespace,
    detector_results: List["ListOutput"],
    teal: "Teal",
    error: Optional[str],
) -> None:
    """Util function to output tealer results.

    Tealer supports displaying the results in json format or raw format.
    Format is decided on whether ``--json`` command line argument is set or not.

    Args:
        args: Namespace object representing the command line arguments selected
            by the user.
        detector_results: results of running the selected detectors.
        teal: The contract.
        error: Error string if any detector or printer resulted in an error.
    """
    expanded_detector_results: "ListOutput" = []
    for result in detector_results:
        expanded_detector_results.extend(result)

    output_directory = ROOT_OUTPUT_DIRECTORY / Path(teal.contract_name)
    os.makedirs(output_directory, exist_ok=True)
    if args.json is None:

        if error is not None:
            print(f"Error: {error}")
            sys.exit(-1)

        detectors_with_0_results: List["AbstractDetector"] = []
        for output in expanded_detector_results:
            if not output.generate_output(output_directory):
                detectors_with_0_results.append(output.detector)
        if detectors_with_0_results:
            detectors_with_0_results_str = ", ".join(d.NAME for d in detectors_with_0_results)
            print(f"\n 0 results found for {detectors_with_0_results_str}.")
    else:
        json_results = [output.to_json() for output in expanded_detector_results]

        json_output = {
            "success": error is not None,
            "error": error,
            "result": json_results,
        }

        if args.json == "-":
            print(json.dumps(json_output, indent=2))
        else:
            filename = output_directory / Path(args.json)
            print(f"json output is written to {filename}")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(json_output, indent=2))


def fetch_contract(args: argparse.Namespace) -> Tuple[str, str]:
    program: str = args.contracts[0]
    network: str = args.network
    b32_regex = "[A-Z2-7]+"
    if program.isdigit():
        # is a number so a app id
        print(f'Fetching application using id "{program}"')
        return get_application_using_app_id(network, int(program)), f"app-{program}"
    if len(program) == 52 and re.fullmatch(b32_regex, program) is not None:
        # is a txn id: base32 encoded. length after encoding == 52
        print(f'Fetching logic-sig contract that signed the transaction "{program}"')
        return logic_sig_from_txn_id(network, program), f"txn-{program[:8].lower()}"
    if len(program) == 58 and re.fullmatch(b32_regex, program) is not None:
        # is a address. base32 encoded. length after encoding == 58
        print(f'Fetching logic-sig of contract account "{program}"')
        return logic_sig_from_contract_account(network, program), f"lsig-acc-{program[:8].lower()}"
    # file path
    print(f'Reading contract from file: "{program}"')
    try:
        contract_name = program[: -len(".teal")] if program.endswith(".teal") else program
        contract_name = contract_name.lower()
        with open(program, encoding="utf-8") as f:
            return f.read(), contract_name
    except FileNotFoundError as e:
        raise TealerException from e


# pylint: disable=too-many-locals,too-many-branches
def main() -> None:
    """Entry point of the tealer tool.

    This function is called when tealer command is executed or tealer is
    executed as a script. This function directs execution flow of the tool
    based on the command line arguments given by the user.
    """

    detector_classes, printer_classes = get_detectors_and_printers()
    args = parse_args(detector_classes, printer_classes)
    validate_command_line_options(args)

    default_log = logging.INFO if not args.debug else logging.DEBUG
    for (logger_name, logger_level) in [
        ("Detectors", default_log),
        ("TransactionCtxAnalysis", default_log),
        ("Parsing", default_log),
        ("Tealer", default_log),
    ]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_level)

    results_detectors: List["ListOutput"] = []
    error = None

    if (
        args.subcommand == "detect"
        and args.detectors_to_run is not None
        and args.group_config is not None
    ):
        # handle this case specially for now.
        # handle_detect(args)
        # sys.exit(1)
        group_config = read_config_from_file(Path(args.group_config))
        tealer = init_tealer_from_config(group_config)
        detector_classes = choose_detectors(args, detector_classes)
        for detector in detector_classes:
            tealer.register_detector(detector)
        group_results = tealer.run_detectors()[0]
        for output in group_results:
            # dest is ignored
            output.generate_output(Path("."))
        sys.exit(1)

    try:  # pylint: disable=too-many-nested-blocks
        contract_source, contract_name = fetch_contract(args)
        tealer = init_tealer_from_single_contract(contract_source, contract_name)

        # TODO: handle this as a subcommand instead of a flag
        if args.subcommand == "regex":
            default_path = Path("regex_result.dot")
            if len(tealer.contracts) != 1:
                print("Regex works only for single contract")
                return
            run_regex(tealer.contracts[contract_name], args.regex_file, default_path)
            return

        # TODO: decide on default classification for detectors in group transaction context.

        if args.subcommand == "print":
            printer_classes = choose_printers(args, printer_classes)

            for printer_cls in printer_classes:
                tealer.register_printer(printer_cls)

            _results_printers = tealer.run_printers()
            return

        if args.subcommand == "detect":
            detector_classes = choose_detectors(
                args, detector_classes, tealer.contracts[contract_name]
            )
            for detector_cls in detector_classes:
                tealer.register_detector(detector_cls)

            results_detectors = tealer.run_detectors()

            if args.filter_paths is not None:
                for detector_result in results_detectors:
                    if isinstance(detector_result, ExecutionPaths):
                        detector_result.filter_paths(args.filter_paths)
                    else:
                        for result in detector_result:
                            result.filter_paths(args.filter_paths)
            # Current does not return
            # This is to call handle_output, which also catch the error
            # This should be refactored (TODO)

        else:
            print(f"{args.subcommand} not implemented")
            return

    except TealerException as e:
        error = str(e)

    # TODO: refactor this logic
    if error or args.subcommand == "detect":
        handle_output(args, results_detectors, tealer.contracts[contract_name], error)


if __name__ == "__main__":
    main()
