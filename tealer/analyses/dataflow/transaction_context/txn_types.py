from typing import TYPE_CHECKING, List, Set, Tuple, Dict

from tealer.analyses.dataflow.transaction_context.generic import DataflowTransactionContext
from tealer.analyses.dataflow.transaction_context.utils.key_helpers import (
    get_gtxn_at_index_key,
    get_ind_base_for_gtxn_type_keys,
    is_value_matches_key,
    get_absolute_index_key,
    get_relative_index_key,
)
from tealer.teal.instructions.instructions import (
    Eq,
    Neq,
    Not,
)
from tealer.teal.instructions.transaction_field import (
    ApplicationID,
    TypeEnum,
    OnCompletion,
)
from tealer.utils.teal_enums import TealerTransactionType
from tealer.utils.teal_enums import (
    ALL_TRANSACTION_TYPES,
    APPLICATION_TRANSACTION_TYPES,
    TYPEENUM_TRANSACTION_TYPES,
)
from tealer.utils.teal_enums import oncompletion_to_tealer_type, transaction_type_to_tealer_type
from tealer.utils.analyses import is_int_push_ins
from tealer.analyses.utils.stack_ast_builder import KnownStackValue, UnknownStackValue
from tealer.utils.algorand_constants import MAX_GROUP_SIZE

if TYPE_CHECKING:
    from tealer.teal.instructions.instructions import Instruction
    from tealer.teal.instructions.transaction_field import TransactionField
    from tealer.teal.basic_blocks import BasicBlock

# TODO: change the value representation for TxnTyp to something similar to FeeValue.
# Same underlying type(TealerTransactionType) for three different things:
#   - CallConfig: (Creation(AppId == 0) or Call(AppId != 0) or Always)
#   - TypeEnum: (pay or keyreg or axfer or afrz or appl)
#   - OnCompletion: (NoOp, OptIn, CloseOut, ClearState, UpdateApplication or DeleteApplication)

transaction_type_key = "TransactionType"

base_keys = [transaction_type_key]
universal_sets: Dict[str, List] = {}
universal_sets[transaction_type_key] = list(ALL_TRANSACTION_TYPES)


class TxnType(DataflowTransactionContext):  # pylint: disable=too-few-public-methods

    TRANSACTION_TYPE_KEY = transaction_type_key
    BASE_KEYS = base_keys
    KEYS_WITH_GTXN: List[str] = [transaction_type_key]
    UNIVERSAL_SETS: Dict[str, List] = universal_sets

    def _universal_set(self, key: str) -> Set:
        if key not in self.BASE_KEYS:
            _, base_key = get_ind_base_for_gtxn_type_keys(key)
            return set(self.UNIVERSAL_SETS[base_key])
        return set(self.UNIVERSAL_SETS[key])

    def _null_set(self, key: str) -> Set:
        return set()

    def _union(self, key: str, a: Set, b: Set) -> Set:
        return a | b

    def _intersection(self, key: str, a: Set, b: Set) -> Set:
        return a & b

    def _get_asserted_transaction_types(  # pylint: disable=too-many-branches, too-many-locals
        self, key: str, ins_stack_value: KnownStackValue
    ) -> Tuple[Set["TealerTransactionType"], Set["TealerTransactionType"]]:
        """return set of transaction type that make the comparison true and a set that makes it false.

        considered instruction patterns:
        [g]txn [idx] ApplicationID
        bz/bnz

        [g]txn [idx] ApplicationID
        !
        bz/bnz

        [g]txn [idx] ApplicationID
        int 0
        ( == | != )
        bz/bnz

        [g]txn [idx] TypeEnum
        int [pay | acfg | axfer | appl ..]
        ( == | != )
        bz/bnz

        [g]txn [idx] OnCompletion
        int [UpdateApplication | DeleteApplication | ...]
        ( == | != )
        bz/bnz

        Args:
            key: The analysis key.
            ins_stack_value: A stack value. The stack value represents the result of ins_stack_value.instruction.
                This function assumes that this value is being asserted/checked.

        Returns:
            Set of possible values for the :key: when the ins_stack_value is asserted to be True and when ins_stack_value is
            asserted to be False.
        """
        U = set(self.UNIVERSAL_SETS[self.TRANSACTION_TYPE_KEY])

        ins1 = ins_stack_value.instruction
        if is_value_matches_key(key, ins_stack_value, ApplicationID):
            # txn ApplicationID pushes 0 if this Application creation transaction elses pushes nonzero
            return set(APPLICATION_TRANSACTION_TYPES) - set(
                [TealerTransactionType.ApplCreation]
            ), set([TealerTransactionType.ApplCreation])

        if isinstance(ins1, Not):
            not_arg = ins_stack_value.args[0]
            if isinstance(not_arg, UnknownStackValue):
                return set(U), set(U)
            ins2 = not_arg.instruction
            if is_value_matches_key(key, not_arg, ApplicationID):
                # txn ApplicationID
                # !
                # return
                return set([TealerTransactionType.ApplCreation]), set(
                    APPLICATION_TRANSACTION_TYPES
                ) - set([TealerTransactionType.ApplCreation])
            return set(U), set(U)

        if isinstance(ins1, (Eq, Neq)):
            arg1 = ins_stack_value.args[0]
            arg2 = ins_stack_value.args[1]
            if isinstance(arg1, UnknownStackValue) or isinstance(arg2, UnknownStackValue):
                # if one of the args is unknown
                return set(U), set(U)
            ins2 = arg1.instruction
            ins3 = arg2.instruction

            is_int_ins2, value_2 = is_int_push_ins(ins2)
            is_int_ins3, value_3 = is_int_push_ins(ins3)

            if (is_int_ins2 and is_int_ins3) or ((not is_int_ins2) and (not is_int_ins3)):
                # if both are ints or both are not ints
                return set(U), set(U)

            true_values, false_values = None, None
            if is_value_matches_key(key, arg1, ApplicationID) and value_3 is not None:
                # TODO: ApplicationCreation transaction can be NoOp or OptIn
                if isinstance(value_3, int) and value_3 == 0:
                    true_values, false_values = set([TealerTransactionType.ApplCreation]), set(
                        APPLICATION_TRANSACTION_TYPES
                    ) - set([TealerTransactionType.ApplCreation])
            elif is_value_matches_key(key, arg2, ApplicationID) and value_2 is not None:
                # TODO: ApplicationCreation transaction can be NoOp or OptIn
                if isinstance(value_2, int) and value_2 == 0:
                    true_values, false_values = set([TealerTransactionType.ApplCreation]), set(
                        APPLICATION_TRANSACTION_TYPES
                    ) - set([TealerTransactionType.ApplCreation])

            if is_value_matches_key(key, arg1, TypeEnum) and value_3 is not None:
                compared_type = transaction_type_to_tealer_type(value_3)
                true_values, false_values = set([compared_type]), set(
                    TYPEENUM_TRANSACTION_TYPES
                ) - set([compared_type])
            elif is_value_matches_key(key, arg2, TypeEnum) and value_2 is not None:
                compared_type = transaction_type_to_tealer_type(value_2)
                true_values, false_values = set([compared_type]), set(
                    TYPEENUM_TRANSACTION_TYPES
                ) - set([compared_type])

            if is_value_matches_key(key, arg1, OnCompletion) and value_3 is not None:
                compared_on_completion = oncompletion_to_tealer_type(value_3)
                true_values, false_values = set([compared_on_completion]), set(
                    APPLICATION_TRANSACTION_TYPES
                ) - set([compared_on_completion])
            elif is_value_matches_key(key, arg2, OnCompletion) and value_2 is not None:
                compared_on_completion = oncompletion_to_tealer_type(value_2)
                true_values, false_values = set([compared_on_completion]), set(
                    APPLICATION_TRANSACTION_TYPES
                ) - set([compared_on_completion])

            if true_values is not None and false_values is not None:
                if isinstance(ins1, Eq):
                    return true_values, false_values
                return false_values, true_values

        return set(U), set(U)

    def _get_asserted_single(self, key: str, ins_stack_value: KnownStackValue) -> Tuple[Set, Set]:
        return self._get_asserted_transaction_types(key, ins_stack_value)

    def _store_results(self) -> None:
        transaction_type_context = self._block_contexts[self.TRANSACTION_TYPE_KEY]

        for block in self._function.blocks:
            self._function.transaction_context(block).transaction_types = list(
                transaction_type_context[block]
            )

            for idx in range(MAX_GROUP_SIZE):
                values = self._block_contexts[
                    get_gtxn_at_index_key(idx, self.TRANSACTION_TYPE_KEY)
                ][block]
                self._function.transaction_context(block).gtxn_context(
                    idx
                ).transaction_types = list(values)

                abs_values = self._block_contexts[
                    get_absolute_index_key(idx, self.TRANSACTION_TYPE_KEY)
                ][block]
                self._function.transaction_context(block).absolute_context(
                    idx
                ).transaction_types = list(abs_values)

            for offset in range(-(MAX_GROUP_SIZE - 1), MAX_GROUP_SIZE):
                if offset == 0:
                    continue
                rel_values = self._block_contexts[
                    get_relative_index_key(offset, self.TRANSACTION_TYPE_KEY)
                ][block]
                self._function.transaction_context(block).relative_context(
                    offset
                ).transaction_types = list(rel_values)
