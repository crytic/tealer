"""Collects and exports detectors defined in tealer.

Exported detectors are:

* ``canDelete``: CanDelete detects paths missing DeleteApplication check.
* ``canUpdate``: CanUpdate detects paths missing UpdateApplication check.
* ``groupSize``: MissingGroupSize detects paths missing GroupSize check.
* ``rekeyTo``: MissingRekeyTo detects paths missing RekeyTo check.
* ``canCloseAccount``: CanCloseAccount detects paths missing CloseRemainderTo check.
* ``canCloseAsset``: CanCloseAsset detects paths missing AssetCloseTo check.
* ``feeCheck``: MissingFeeCheck detects paths missing Fee check.
"""

# pylint: disable=unused-import
from tealer.detectors.can_delete import CanDelete
from tealer.detectors.can_update import CanUpdate
from tealer.detectors.groupsize import MissingGroupSize
from tealer.detectors.rekeyto import MissingRekeyTo
from tealer.detectors.can_close_account import CanCloseAccount
from tealer.detectors.can_close_asset import CanCloseAsset
from tealer.detectors.fee_check import MissingFeeCheck
