"""
NOTE: Incorrect or Inaccurate documentation. ignore for now.

tealer init

positional_arguments: (+), list of filesystem paths

optional_argument: --group-config yaml file

tealer detect



subcommands

- `init`
- `detect`
- `print`

#### init

positional arguments:
    programs        list of space-separated directories/files.

optional argument:
    --group-config  yaml configuration file.

Purpose:

program_files = []
for program in programs:
    if program is directory:
        list all files with .teal extension and add them to program_files.
    if program is file:
        add it to program_files

if group_config is not null:
    read the config
else:
    create a empty config

if a program file is already in group_config:
    remove it from program_files

For each program in program_files:
    analyze the program and append its information to the group_config.

Output updated group-config file
"""

import sys
from pathlib import Path
import inspect
import argparse

from typing import List, Type, Tuple, TYPE_CHECKING, Dict
from pkg_resources import iter_entry_points  # type: ignore

from tealer.detectors.abstract_detector import (
    AbstractDetector,
)
from tealer.printers.abstract_printer import AbstractPrinter
from tealer.detectors import all_detectors
from tealer.printers import all_printers
from tealer.exceptions import TealerException
from tealer.utils.command_line.group_config import (
    read_config_from_file,
)
from tealer.teal.parse_teal import parse_teal
from tealer.teal.parse_functions import construct_function
from tealer.utils.teal_enums import ContractType, contract_type_from_txt
from tealer.tealer import Tealer
from tealer.utils.output import subroutine_to_dot
from tealer.execution_context.transactions import Transaction, GroupTransaction

if TYPE_CHECKING:
    from tealer.teal.functions import Function
    from tealer.teal.teal import Teal
    from tealer.utils.command_line.group_config import (
        GroupConfig,
        GroupConfigFunctionCall,
    )


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


# pylint: disable=too-many-branches
def validate_command_line_options(args: argparse.Namespace) -> None:
    """Validate command line options and print message and exit the program

    - Only one of --init or --detect or --print must be selected
    - init
        - --contracts is required
        - --group-config is optional
    - detect
        - Only one of --contracts or --group_config is selected

    Args:
        args: Command line arguments
    """

    def print_and_exit(message: str) -> None:
        print(f"CommandLineError: {message}")
        sys.exit(1)

    no_of_subcommands = (
        int(args.init is True)
        + int(args.detectors_to_run is not None)
        + int(args.printers_to_run is not None)
    )
    if no_of_subcommands != 1:
        print('CommandLineError: "User must select only one of --init, --detect or --print"')
        sys.exit(1)

    if args.init:
        if args.contracts is None:
            print_and_exit(
                "--contracts is required for --init. Use optional --group-config option to add new contracts to existing configuration"
            )
    elif args.detectors_to_run is not None:
        if args.contracts is None and args.group_config is None:
            print_and_exit("--detect requires one of --contracts or --group-config")
        if args.contracts is not None and args.group_config is not None:
            print_and_exit(
                "--detect takes only one of --contracts or --group-config. Use --group-config with --init to add new contracts to existing configuration."
            )
    elif args.printers_to_run is not None:
        if args.contracts is None and args.group_config is None:
            print_and_exit("--print requires one of --contracts or --group-config")
        if args.contracts is not None and args.group_config is not None:
            print_and_exit(
                "--print takes only one of --contracts or --group-config. Use --group-config with --init to add new contracts to existing configuration."
            )

        if args.json is not None:
            print_and_exit("--json is not supported for --print.")

    # TODO: update args.network. args.network defaults to mainnet and is never None.
    # if args.network is not None and args.contracts is None:
    #     print_and_exit("--network is not supported when --contracts is not supplied.")

    if args.detectors_to_run is None:
        if (
            args.detectors_to_exclude is not None
            or args.exclude_stateless
            or args.exclude_stateful
            or args.filter_paths is not None
        ):
            print_and_exit(
                "--exclude, --exclude-stateless, --exclude-stateful and --filter-paths options are only available when --detect is selected."
            )


def handle_detect(args: argparse.Namespace) -> None:
    group_config = read_config_from_file(Path(args.group_config))
    tealer = init_tealer_from_config(group_config)

    for contract_name, contract in tealer.contracts.items():
        for function_name, function in contract.functions.items():
            dot_file_name = f"{contract_name}_{function_name}.dot"
            with open(dot_file_name, "w", encoding="utf-8") as f:
                f.write(subroutine_to_dot(function.main))


# def list_contract_files(directory: Path) -> List[Path]:
#     teal_files = []
#     for file in directory.iterdir():
#         if file.is_file() and file.name.endswith(".teal"):
#             teal_files.append(directory / file)
#     return teal_files


def _get_function_from_config(
    function_call_config: "GroupConfigFunctionCall", contracts: Dict[str, "Teal"]
) -> "Function":
    if function_call_config.contract not in contracts:
        raise TealerException(f"{function_call_config.contract} not found in listed contracts")
    contract_obj = contracts[function_call_config.contract]
    if function_call_config.function not in contract_obj.functions:
        raise TealerException(
            f"{function_call_config.function} not found in {contract_obj.contract_name} functions."
        )
    return contract_obj.functions[function_call_config.function]


# pylint: disable=too-many-locals
def init_tealer_from_config(config: "GroupConfig") -> "Tealer":
    contracts: Dict[str, "Teal"] = {}
    for contract_config in config.contracts:
        with open(contract_config.file_path, encoding="utf-8") as f:
            teal = parse_teal(f.read(), contract_config.name)
        given_contract_type = contract_type_from_txt(contract_config.contract_type)
        teal.contract_type = given_contract_type
        # ignore version and subroutines
        contract_functions: Dict[str, "Function"] = {}
        for function_config in contract_config.functions:
            func = construct_function(teal, function_config.dispatch_path, function_config.name)
            contract_functions[function_config.name] = func

        teal.functions = contract_functions
        contracts[contract_config.name] = teal

    group_objs_list: List[GroupTransaction] = []
    for txn_config in config.groups:
        txn_id_to_obj: Dict[str, "Transaction"] = {}
        for txn in txn_config:
            txn_obj = Transaction()
            if txn.has_logic_sig is not None:
                txn_obj.has_logic_sig = txn.has_logic_sig
            txn_obj.absoulte_index = txn.absolute_index

            if txn.application is not None:
                app_function = _get_function_from_config(txn.application, contracts)
                if app_function.contract.contract_type == ContractType.LogicSig:
                    raise TealerException(
                        f"{txn.application.contract} is a logic-sig but is given as an application."
                    )
                txn_obj.application = app_function

            if txn.logic_sig is not None:
                logic_sig_function = _get_function_from_config(txn.logic_sig, contracts)
                if logic_sig_function.contract.contract_type != ContractType.LogicSig:
                    raise TealerException(
                        f"{txn.logic_sig.contract} is an application but is given as a logic-sig."
                    )
                txn_obj.logic_sig = logic_sig_function

            if txn.txn_id in txn_id_to_obj:
                raise TealerException(f"{txn.txn_id} is repeated in the same group.")
            txn_id_to_obj[txn.txn_id] = txn_obj

        group_obj = GroupTransaction()
        group_obj.transactions = list(txn_id_to_obj.values())

        for txn in txn_config:
            txn_obj = txn_id_to_obj[txn.txn_id]
            txn_obj.group_transaction = group_obj
            if txn.relative_indexes is not None:
                for other_txn_id in txn.relative_indexes:
                    if other_txn_id not in txn_id_to_obj:
                        raise TealerException(
                            f"other_txn_id: {other_txn_id} is not present in the same group"
                        )
                    offset = txn.relative_indexes[other_txn_id]
                    txn_obj.relative_indexes[offset] = txn_id_to_obj[other_txn_id]

            if txn_obj.absoulte_index is not None:
                group_obj.absolute_indexes[txn_obj.absoulte_index] = txn_obj

        group_objs_list.append(group_obj)

    return Tealer(contracts, group_objs_list)


def init_tealer_from_single_contract(contract_src: str, contract_name: str) -> "Tealer":
    teal = parse_teal(contract_src, contract_name)
    contracts: Dict[str, "Teal"] = {contract_name: teal}
    contract_functions: Dict[str, "Function"] = {}
    contract_functions[contract_name] = construct_function(teal, ["B0"], contract_name)
    teal.functions = contract_functions

    txn_obj = Transaction()
    if teal.contract_type == ContractType.LogicSig:
        txn_obj.has_logic_sig = True
        txn_obj.logic_sig = contract_functions[contract_name]
    else:
        # contract is either Approval or ClearState
        txn_obj.application = contract_functions[contract_name]

    group_obj = GroupTransaction()
    group_obj.transactions = [txn_obj]
    group_objs_list = [group_obj]

    return Tealer(contracts, group_objs_list)
