"""Detector for finding execution paths missing AssetCloseTo check."""

from typing import List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.teal.instructions.transaction_field import AssetCloseTo
from tealer.utils.analyses import detect_missing_txn_check

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput


class CanCloseAsset(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find execution paths missing AssetCloseTo check.

    In algorand, A transaction can close out the asset balance of a contract
    account and transfer all asset balance to the specified address. If the
    AssetCloseTo field of a transaction is set to an address and that transaction
    is approved by the contract then all the contract asset balance will be
    transferred to address in AssetCloseTo field.

    This detector tries to find execution paths that approve the algorand
    transaction("return 1") and doesn't check the AssetCloseTo field.
    """

    NAME = "canCloseAsset"
    DESCRIPTION = "Detect paths that can close the asset holdings of the sender"
    TYPE = DetectorType.STATELESS

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_TITLE = "Can Close Asset"
    WIKI_DESCRIPTION = "Detect paths that can close the asset holdings of the sender"
    WIKI_EXPLOIT_SCENARIO = """
```
#pragma version 2
txn Receiver
addr BAZ7SJR2DVKCO6EHLLPXT7FRSYHNCZ35UTQD6K2FI4VALM2SSFIWTBZCTA
==
txn AssetAmount
int 10
==
&&
...
```

receiver sets the AssetCloseTo transaction field of a Asset Transfer Transaction with above contract account as Sender which will result in removal of asset holding from the contract's account and sending the asset's to AssetCloseTo address.
"""

    WIKI_RECOMMENDATION = """
Always check that AssetCloseTo transaction field is set to a ZeroAddress or intended address if needed.
"""

    def detect(self) -> "SupportedOutput":
        """Detect execution paths with missing AssetCloseTo check.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        paths_without_check: List[List[BasicBlock]] = []
        detect_missing_txn_check(AssetCloseTo, self.teal.bbs[0], [], paths_without_check)

        description = "Lack of AssetCloseTo check allows to close the asset holdings"
        description += " of the account."
        filename = "can_close_asset"

        return self.generate_result(paths_without_check, description, filename)
