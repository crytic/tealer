from typing import List, Tuple, Optional, TYPE_CHECKING

from tealer.printers.abstract_printer import AbstractPrinter
from tealer.teal.instructions.instructions import Label, contract_type_to_txt
from tealer.utils.code_complexity import compute_cyclomatic_complexity

if TYPE_CHECKING:
    from pathlib import Path


class PrinterHumanSummary(AbstractPrinter):
    """Printer to print summary of the contract"""

    NAME = "human-summary"
    HELP = "Print a human-readable summary of the contracts"

    def _is_complex_code(self) -> str:
        """check whether contract code is complex or not using cyclomatic complexity.

        Returns:
            (str): returns "Yes" if cyclomatic complexity of the contract is greater than 7 or
            else returns "No".

        """
        is_complex = False
        if compute_cyclomatic_complexity(self.teal.bbs) > 7:
            is_complex = True

        result = "Yes" if is_complex else "No"
        return result

    def _get_detectors_result(self) -> Tuple[List, int, int, int, int, int]:
        """return dectector results and number of issues found in the contract for each `impact` class.

        Returns:
            (Tuple[List, int, int, int, int, int]): returns list of results found by all the detectors and
            number of issues found by detectors of impact optimization, informational, low, medium, high in
            the same order.

        """
        checks_optimization = self.teal.detectors_optimization
        checks_informational = self.teal.detectors_informational
        checks_low = self.teal.detectors_low
        checks_medium = self.teal.detectors_medium
        checks_high = self.teal.detectors_high

        issues_optimization = [c.detect() for c in checks_optimization]
        issues_optimization = [c for c in issues_optimization if c]

        issues_informational = [c.detect() for c in checks_informational]
        issues_informational = [c for c in issues_informational if c]

        issues_low = [c.detect() for c in checks_low]
        issues_low = [c for c in issues_low if c]

        issues_medium = [c.detect() for c in checks_medium]
        issues_medium = [c for c in issues_medium if c]

        issues_high = [c.detect() for c in checks_high]
        issues_high = [c for c in issues_high if c]

        all_results = (
            issues_optimization + issues_informational + issues_low + issues_medium + issues_high
        )

        return (
            all_results,
            len(issues_optimization),
            len(issues_informational),
            len(issues_low),
            len(issues_medium),
            len(issues_high),
        )

    def get_detectors_result(self) -> str:
        """return textual summary of number of issues found by detectors for each `impact` class.

        Returns:
            (str): textual summary of number of issues found by detectors.

        """
        (
            _,
            optimization,
            informational,
            low,
            medium,
            high,
        ) = self._get_detectors_result()

        txt = f"Number of optimization issues: {optimization}\n"
        txt += f"Number of informational issues: {informational}\n"
        txt += f"Number of low issues: {low}\n"
        txt += f"Number of medium issues: {medium}\n"
        txt += f"Number of high issues: {high}\n"

        return txt

    def print(self, dest: Optional["Path"] = None) -> None:
        """Prints summary of the contract to stdout.

        Currently displays version, mode, number of basic blocks, instructions, subroutines,
        Names of subroutines, number of results found by detectors for each level of impact.

        """
        teal = self.teal

        txt = "\n"
        txt += f"Program version: {teal.version}\n"
        txt += f"Mode: {contract_type_to_txt[teal.mode]}\n"
        txt += f"Number of basic blocks: {len(teal.bbs)}\n"
        txt += f"Number of instructions: {len(teal.instructions)}\n"

        txt += f"Number of subroutines: {len(teal.subroutines)}\n"
        txt += "Subroutines:\n"
        for sub in teal.subroutines:
            if isinstance(sub[0].entry_instr, Label):
                sub_name = sub[0].entry_instr.label
            else:
                sub_name = str(sub[0].entry_instr)
            txt += f"\t{sub_name}\n"
        txt += "\n"

        txt_detector_results = self.get_detectors_result()
        txt += txt_detector_results

        txt += f"is_complex: {self._is_complex_code()}\n"

        print(txt)
