"""Module for tealer printers.

Printers are information summarizers. Printers make finding and evaluating
interesting information related to the contract easier. There's always abundant
information that can be extracted from a smart contract, manually going
through a smart contract for a every tiny bit of information is hard, boringgg
and error prone. Printers make this process of finding information easier.

This module contains Abstract base class for printers and implementation of
few printers that can used to retrieve interesting information.

Modules:
    abstract_printer: Defines abstract base class for printers in tealer.

    all_printers: Collects and exports printers defined in tealer.

    call_graph: Printer for exporting call-graph of the contract.

    function_cfg: Printer for exporting contract subroutines in dot format.

    human_summary: Printer to print summary of the contract.
"""
