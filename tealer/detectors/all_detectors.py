"""Collects and exports detectors defined in tealer.

Exported detectors are:

* ``isDeletable``: IsDeletable detects paths missing DeleteApplication check.
* ``isUpdatable``: IsUpdatable detects paths missing UpdateApplication check.
* ``groupSize``: MissingGroupSize detects paths missing GroupSize check.
* ``rekeyTo``: MissingRekeyTo detects paths missing RekeyTo check.
* ``canCloseAccount``: CanCloseAccount detects paths missing CloseRemainderTo check.
* ``canCloseAsset``: CanCloseAsset detects paths missing AssetCloseTo check.
* ``feeCheck``: MissingFeeCheck detects paths missing Fee check.
* ``anyoneCanUpdate``: Detect paths missing validations on sender field AND allows to delete the application.
* ``anyoneCanDelete``: Detect paths missing validations on sender field AND allows to update the application.
"""

# pylint: disable=unused-import
from tealer.detectors.is_deletable import IsDeletable
from tealer.detectors.is_updatable import IsUpdatable
from tealer.detectors.groupsize import MissingGroupSize
from tealer.detectors.rekeyto import MissingRekeyTo
from tealer.detectors.can_close_account import CanCloseAccount
from tealer.detectors.can_close_asset import CanCloseAsset
from tealer.detectors.fee_check import MissingFeeCheck
from tealer.detectors.anyone_can_update import AnyoneCanUpdate
from tealer.detectors.anyone_can_delete import AnyoneCanDelete
from tealer.detectors.optimizations.constant_gtxn import ConstantGtxn
from tealer.detectors.optimizations.sender_access import SenderAccess
from tealer.detectors.optimizations.self_access import SelfAccess
