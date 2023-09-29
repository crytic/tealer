"""Module for tealer detectors.

Detectors are analyzers which go through the parsed code and look for
certain patterns in the program which are of interest to anyone invested
in the security of the contract.

This module contains Abstract base class for printers and implementation of
few detectors that detect common issues in algorand smart contracts.

Modules:
    abstract_detector: Defines abstract base class for detectors.

    all_detectors: Collects and exports detectors defined in tealer.
"""
