"""Printer to print human readable summary of the contract.

Summary includes :
* Contract version.
* Type of the contract as detected by tealer.
* Number of basic blocks in the contract.
* Number of instructions in the contract.
* Number of subroutines defined in the contract.
* Name of each subroutine defined in the contract.
* Number of issues found by detectors each class of impact.
* Check whether contract code is complex or not.

"""

from typing import TYPE_CHECKING

from tealer.printers.abstract_printer import AbstractPrinter
from tealer.utils.code_complexity import compute_cyclomatic_complexity

if TYPE_CHECKING:
    from pathlib import Path


# pylint: disable=too-few-public-methods
class PrinterHumanSummary(AbstractPrinter):
    """Printer to print summary of the contract"""

    NAME = "human-summary"
    HELP = "Print a human-readable summary of the contract"
    WIKI_URL = "https://github.com/crytic/tealer/wiki/Printer-documentation#human-summary"

    def _is_complex_code(self) -> str:
        """Check whether contract code is complex or not.

        Returns:
            (str): returns "Yes" if cyclomatic complexity of the contract
            is greater than 7 or else returns "No".
        """

        is_complex = False
        if compute_cyclomatic_complexity(self.teal.bbs) > 7:
            is_complex = True

        result = "Yes" if is_complex else "No"
        return result

        # pylint: disable=too-many-locals
        # TODO: Decide on how printers should behave in group context
        # def _get_detectors_result(self) -> Tuple[List, int, int, int, int, int]:
        #     """Return dectector results and number of issues found in the contract for each `impact` class.

        #     Returns:
        #         (Tuple[List, int, int, int, int, int]): returns list of results found by all the detectors and
        #         number of issues found by detectors of impact optimization, informational, low, medium, high in
        #         the same order.

        #     """
        #     from tealer.utils.command_line.common import (  # pylint: disable=import-outside-toplevel
        #         get_detectors_and_printers,
        #     )

        #     detector_classes, _ = get_detectors_and_printers()
        #     detectors = [d(self.teal) for d in detector_classes]

        #     checks_optimization = [
        #         d for d in detectors if d.IMPACT == DetectorClassification.OPTIMIZATION
        #     ]
        #     checks_informational = [
        #         d for d in detectors if d.IMPACT == DetectorClassification.INFORMATIONAL
        #     ]
        #     checks_low = [d for d in detectors if d.IMPACT == DetectorClassification.LOW]
        #     checks_medium = [d for d in detectors if d.IMPACT == DetectorClassification.MEDIUM]
        #     checks_high = [d for d in detectors if d.IMPACT == DetectorClassification.HIGH]

        #     issues_optimization = [c.detect().paths for c in checks_optimization]
        #     issues_optimization = [c for c in issues_optimization if c]

        #     issues_informational = [c.detect().paths for c in checks_informational]
        #     issues_informational = [c for c in issues_informational if c]

        #     issues_low = [c.detect().paths for c in checks_low]
        #     issues_low = [c for c in issues_low if c]

        #     issues_medium = [c.detect().paths for c in checks_medium]
        #     issues_medium = [c for c in issues_medium if c]

        #     issues_high = [c.detect().paths for c in checks_high]
        #     issues_high = [c for c in issues_high if c]

        #     all_results = (
        #         issues_optimization + issues_informational + issues_low + issues_medium + issues_high
        #     )

        #     return (
        #         all_results,
        #         len(issues_optimization),
        #         len(issues_informational),
        #         len(issues_low),
        #         len(issues_medium),
        #         len(issues_high),
        #     )

        # def get_detectors_result(self) -> str:
        # """Return textual summary of number of issues found by detectors.

        # Textual summary contains number of issues found in the contract
        # for each class of impact(severity).

        # Returns:
        #     (str): textual summary of number of issues found by detectors.
        # """

        # (
        #     _,
        #     optimization,
        #     informational,
        #     low,
        #     medium,
        #     high,
        # ) = self._get_detectors_result()

        # txt = f"Number of optimization issues: {optimization}\n"
        # txt += f"Number of informational issues: {informational}\n"
        # txt += f"Number of low issues: {low}\n"
        # txt += f"Number of medium issues: {medium}\n"
        # txt += f"Number of high issues: {high}\n"

        # return txt

    def print(self) -> None:
        """Print summary of the contract to stdout.

        Currently displays version, mode, number of basic blocks, instructions, subroutines,
        Names of subroutines, number of results found by detectors for each level of impact.
        """

        teal = self.teal

        txt = "\n"
        txt += f"Program version: {teal.version}\n"
        txt += f"Mode: {str(teal.mode)}\n"
        txt += f"Number of basic blocks: {len(teal.bbs)}\n"
        txt += f"Number of instructions: {len(teal.instructions)}\n"

        txt += f"Number of subroutines: {len(teal.subroutines.items())}\n"
        txt += "Subroutines:\n"
        for sub_name in teal.subroutines:
            txt += f"\t{sub_name}\n"
            block_ids = ", ".join(repr(bi) for bi in teal.subroutines[sub_name].blocks)
            txt += f'\t\t"{block_ids}"\n'
        # txt += f"is_complex: {self._is_complex_code()}\n" # update printer after deciding on its semantics
        print(txt)
        # print(self.get_detectors_result())
