"""Detect paths missing validations on sender field AND allows to delete the application."""

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


class AnyoneCanDelete(AbstractDetector):  # pylint: disable=too-few-public-methods
    """Detector to find execution paths missing validations on sender field AND allows to delete the application.

    Stateful smart contracts(application) can be deleted in Algorand. If the
    application transaction of type DeleteApplication is approved by the application,
    then the application will be deleted.

    This detector tries to find execution paths for which
        - OnCompletion can be DeleteApplication And
        - Transaction sender can be any address.
    """

    NAME = "anyoneCanDelete"
    DESCRIPTION = (
        "Detect paths missing validations on sender field AND allows to delete the application."
    )
    TYPE = DetectorType.STATEFULL

    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH

    WIKI_TITLE = "Anyone Can Delete Application"
    WIKI_DESCRIPTION = (
        "Detect paths missing validations on sender field AND allows to delete the application."
    )
    WIKI_EXPLOIT_SCENARIO = """
```py
@router.method(no_op=CallConfig.CALL, delete_application=CallConfig.CALL)
def remove_user():
    return Seq([
        App.localDel(Txn.sender(), "balance"),
        Return(Int(1))
    ])
```

Algorand supports multiple types of application transactions. All types of application transactions execute the application
and fail if the execution fails. Based on the application type, AVM performs additional operations on the application.

Additional operations for DeleteApplication type transaction is 
```
After executing the ApprovalProgram, delete the application parameters from the account data of the application's creator.
```

There should be proper access controls protecting the execution paths/methods approving DeleteApplication type transactions.

Exploitation:
    Attacker submits a DeleteApplication type transaction to "remove_user" method. Application parameters are deleted from the creator's
    account and application assets became inaccesible.
"""

    WIKI_RECOMMENDATION = """
Place proper access controls for privileged methods. One approach is to validate transaction sender is equal to a privileged address(admin) in the system.
"""

    def detect(self) -> "SupportedOutput":
        """Detect execution paths missing validations on sender field AND can delete the application .

        Returns:
            ExecutionPaths instance containing the list of vulnerable execution
            paths along with name, check, impact, confidence and other detector
            information.
        """

        def checks_field(block_ctx: "BlockTransactionContext") -> bool:
            # return False if Txn Type can be DeleteApplication AND sender can be any address.
            # return True otherwise
            return not (
                TealerTransactionType.ApplDeleteApplication in block_ctx.transaction_types
                and block_ctx.sender.any_addr
            )

        paths_without_check: List[List[BasicBlock]] = detect_missing_tx_field_validations(
            self.teal.bbs[0], checks_field
        )

        description = (
            "Lack of access controls on methods approving a DeleteApplication transaction."
        )
        filename = "anyone_can_delete"

        return self.generate_result(paths_without_check, description, filename)
