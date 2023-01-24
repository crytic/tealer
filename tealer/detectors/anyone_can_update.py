"""Detect paths missing validations on sender field AND allows to update the application."""

from typing import List, TYPE_CHECKING

from tealer.detectors.abstract_detector import (
    AbstractDetector,
    DetectorClassification,
    DetectorType,
)
from tealer.teal.basic_blocks import BasicBlock
from tealer.detectors.utils import detect_missing_tx_field_validations
from tealer.utils.teal_enums import TealerTransactionType

if TYPE_CHECKING:
    from tealer.utils.output import SupportedOutput
    from tealer.teal.context.block_transaction_context import BlockTransactionContext


# TODO: change original CanUpdate, CanDelete to isUpdatable and isDeletable.    (?)
# And use CanUpdate for AnyoneCanUpdate, CanDelete for AnyoneCanDelete.
class AnyoneCanUpdate(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find execution paths missing validations on sender field AND allows to update the application.

    Stateful smart contracts(application) can be updated in algorand. If the
    application transaction of type UpdateApplication is approved by the application,
    then the application's code will be updated with the new code.

    This detector tries to find execution paths for which
        - OnCompletion can be UpdateApplication And
        - Transaction sender can be any address.
    """

    NAME = "anyoneCanUpdate"
    DESCRIPTION = (
        "Detect paths missing validations on sender field AND allows to update the application."
    )
    TYPE = DetectorType.STATEFULL

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_TITLE = "Anyone Can Update Application"
    WIKI_DESCRIPTION = (
        "Detect paths missing validations on sender field AND allows to update the application."
    )
    WIKI_EXPLOIT_SCENARIO = """
```py
@router.method(no_op=CallConfig.CALL, update_application=CallConfig.CALL)
def update_balance():
    return Seq([
        App.localPut(Txn.sender(), "key", Int(1000)),
        Return(Int(1))
    ])
```

Algorand supports multiple types of application transactions. All types of application transactions execute the application
and fail if the execution fails. Based on the application type, AVM performs additional operations on the application.

Additional operations for UpdateApplication type transaction is 
```
After executing the ApprovalProgram, replace the ApprovalProgram and ClearStateProgram associated with this application ID with the programs specified in this transaction.
```

Ability to execute UpdateApplication transaction will give complete control of application code, which controls all the assets held by the application. There should be proper
access controls protecting the execution paths/methods approving UpdateApplication type transactions.

Exploitation:
    Attacker sends a UpdateApplication transaction with the new approval program which transfers all of the application's assets to attacker's address.
"""

    WIKI_RECOMMENDATION = """
Place proper access controls for privileged methods. One approach is to validate the transaction sender: Assert it is equal to a privileged address(admin) in the system.
"""

    def detect(self) -> "SupportedOutput":
        """Detect paths missing validations on sender field AND allows to update the application.

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        def checks_field(block_ctx: "BlockTransactionContext") -> bool:
            # return False if Txn Type can be UpdateApplication AND sender can be any address.
            # return True otherwise.
            return not (
                TealerTransactionType.ApplUpdateApplication in block_ctx.transaction_types
                and block_ctx.sender.any_addr
            )

        paths_without_check: List[List[BasicBlock]] = detect_missing_tx_field_validations(
            self.teal.bbs[0], checks_field
        )

        description = (
            "Lack of access controls on methods approving a UpdateApplication transaction."
        )

        filename = "anyone_can_update"
        return self.generate_result(paths_without_check, description, filename)
