"""
The main purpose of transaction-context analysis is to simplify detectors based on transaction field validations.

Transaction field based detectors:
    Detectors that report execution paths that do not validate the value of a problematic transaction field such as
    RekeyTo, CloseRemainderTo, OnCompletion, etc...

The transaction field of the transaction executing the target contract can be accessed in multiple ways:

- The target contract uses `txn {field}`.
- The target contract use its index in the group and access the transaction field using gtxn.. type instructions.
- A different contract uses the target contract's group index and access the target transaction field using gtxn.. type instructions.

Code patterns for accessing the field:

Index types:

    - Absolute index: The index of the target transaction is given by the user input or is fixed at compile time.
    - Relative index: The user input or the compiled code contains the offset. The index is calculated using `Txn.group_index() +/- offset`.

The code patterns for target contract validating its own transaction fields:

- The field is accessed using `txn {field}`
- The target contract validates its index and uses absolute index:
    - The absolute index is fixed at compile time and `gtxn {index} {field}` is used.
    - The absolute index is fixed at compile time but is passed from one location to other:
        - The absolute index is pushed to stack using an `int` instruction and `gtxns {field}` is used.
            - The int instruction is pushed in the same basic block.
            - The int instruction is pushed in different basic block but the basic block is of the
                same subroutine.
            - The int instruction value is passed as a subroutine's argument.
    - The index is computed using `Txn.group_index()` and `gtxns {field}` is used.
    - The index is an user input.
- The target contract uses the group size (`global GroupSize`) and iterates over all transactions in the group
    - accesses all indexes in the group sequentially, the index is fixed at compile time.
        - Above listed code patterns for compile time fixed indexes.
    - Iterates in a loop
    - index is supplied as a subroutine argument.

The code patterns for other contracts validating the target's transaction fields:

- The other contract uses the group size (`global GroupSize`) and iterates over all transactions in the group
    - Above listed code patterns
- The other contracts validates the target contract's index and uses absolute index.
    - The absolute index is fixed at compile time and `gtxn {index} {field}` is used.
    - The absolute index is fixed at compile time but is passed from one location to other:
        - Above listed patterns
- The other contract uses relative index and accesses target's contract fields.
    - The offset is fixed at compile time
        - The index is calculated immediately after `int` instruction pushes the offset: relative index = Txn.group_index +/- offset.
            - The calculated index is used by `gtxns {field}` instruction in the same block.
            - The calculated index is passed around to different blocks.
            - The calculated index is passed as argument to a subroutine.
        - The offset is passed around to different blocks, to a subroutine.
            - Above listed patterns.
    - The offset is user input
        - Above listed patterns.

Code patterns for comparing the field:

- The accessed field is directly compared against the target value.
- The accessed field is compared against a value which reduces the list of possible values.
- The value of the accessed field is passed around:
    - basic blocks of the same subroutine.
    - is passed to an subroutine which compares the field.
- The value is compared using transitive properties: e.g `Gtxn[0].fee + Gtxn[1].fee < 3000`, fees of both transactions are compared.

Code patterns for asserting the comparison:

- The result of the comparison is directly asserted using `assert`.
- The result of the comparison is used by conditional branching instructions `bz`, `bnz`.
- The results of multiple comparisons are combined using `&&`, `||` and `!`.
    - The combined result is asserted using `assert`
    - The combined result is used by `bz` or `bnz` instructions.


The contract analyzed by Tealer can use combination of any of the above patterns. The transaction field analysis tries to
cover as many combinations as possible.

The goal of the transaction field analysis:

- Given an contract, it gives the possible values for the target transaction field of the target contract and possible values
    for the target transaction field of other contracts in the group.

The current results of transaction field analysis:

- Given an contract, it gives the possible values for the target transaction field of the target contract.
    Only some of the patterns are supported.


How is it implemented:

DataflowTransactionContext (in generic.py)

The generic.py contains the utilities that are needed for any transaction field analysis.

The execution flow for an analysis is as follows:

- DataflowTransactionContext.run_analysis()
    - Compute possible values for the transaction field at basic block level (DataflowTransactionContext._block_level_constraints()).
        - i.e if the contract would contain just this basic block, then what would be the possible
            transaction fields.
    - Compute possible values for the transaction field at path level (DataflowTransactionContext._path_level_constraints())
        - This is used when comparison result is used by `bz`, `bnz` instructions.
    - Combine the transaction field information of all basic blocks and edges in the CFG.
        - This is done using iterative fixed-point algorithm.
    - The end result:
        - For each block, list of possible values for the transaction field such that
            if and only if the transaction field during execution is one of the possible values:
            - The execution might reach this basic block
            - The execution might reach end of the basic block
            - The execution might reach from this basic block to a leaf block.

DataflowTransactionContext._block_level_constraints() computes possible values at block level.
    - finds `assert`, `return` instructions in the block.
    - Uses DataflowTransactionContext._get_asserted() on the input argument of `assert` and `return` instructions
        to find possible values for the field.

DataflowTransactionContext._path_level_constraints() computes possible values at path level.
    - checks the basic block has conditional branch instruction: `bz` or `bnz`.
    - Uses DataflowTransactionContext._get_asserted() on the input argument of `bz` or `bnz` to find
        possible values for the field for each out-edge(next) of the block.

DataflowTransactionContext._get_asserted() computes possible values for the field given an comparison result.
    - The input expression might contain `&&`, `||` or `!` and the result of the expression depends on multiple
        small comparisons.
    - This function finds all individual comparison expressions and uses DataflowTransactionContext._get_asserted_single()
        on each individual comparisons.
    - Given the possible values for each individual comparison, this function combines them to find possible values
        for the input comparison.

DataflowTransactionContext._get_asserted_single() is specific for individual fields and is implemented by the corresponding classes.

What are possible valus returned by _get_asserted() and _get_asserted_single()?

The returned values is a Tuple containing `true_values` and `false_values`.

true_values: Given that the execution of input expression results in non-zero value on top of stack, What values
    can the transaction field have?
false_values: Given that the execution of input expression results in zero value on top of stack, What values
    can the transaction field have?

For example input expression is `Txn.group_index() == 2`, then
    - if the result is non-zero => group_index must be in [2] => true_values for group_index = [2]
    - if the result is zero => group_index must be in [0, 1, 3, ..., 15] => false_values for group_index = [0, 1, 3, ..., 15]

_get_asserted_single() returns true_values and false_values for a single direct comparison.
_get_asserted() combines true_values and false_values for all individual direct comparisons and returns true_values
    and false_values for the entire input_expression.

How are these true_values and false_values used by _block_level_constraints() and _path_level_constraints?

_block_level_constraints() finds following instructions:
    - `assert`: Finds the true_values for input expression of `assert` and sets them as possible values
        For the execution to pass => the result must be non-zero => the transaction field can only have one of true_values to not fail the execution.
    - `return`: Finds the true_values for input expression of `return` and sets them as possible values
        For the execution to succeed => the return value must be non-zero => the expression result must be non-zero => the transaction field can have
        only one of true_values.

_path_level_constraints()
    - finds conditional branch instructions (`bz` or `bnz`)
    - finds the edge taken when the result of input expression is non-zero and the edge taken when the result of expression is zero.
    - Assign true_values as possible values for edge taken when the result of input expression is non-zero
    - Assign false_values as possible values for edge taken when the result of input expression is zero

_block_level_constraints fills the possible values for each block.
_path_level_constraints fills the possible values for each edge.

DataflowTransactionContext.run_analysis uses iterative fixed point algorithm to combine information at each block and edge using the information
for predecessors and successors. This gives the above mentioned end_result.


DataflowTransactionContext.BASE_KEYS and DataflowTransactionContext.KEYS_WITH_GTXN

BASE_KEYS: A key represents a transaction field. The possible values for a transaction field are tracked using its corresponding base key.
    The main reason is: The calculation of true_values and false_values for multiple keys can be same. Using multiple keys
    allows us to not create multiple classes that does exactly the same. The _get_asserted_single() is given the "key" and it
    can compute the values for the transaction field corresponding to the key.

    For example, all address fields have similar implementation for computing the true_values and false_values. A single implementation can
    can be used for all fields.

KEYS_WITH_GTXN: KEYS_WITH_GTXN is a subset of BASE_KEYS.
    For a given field multiple types of possible values can be calculated.
    The possible values of the field of the transaction
        1. executing the contract/function irrespective of the transaction's group index.
        2. executing the contract when the transaction group index is a particular value.
        3. at a given absolute index irrespective of which contract is executed.
        4. at a given relative index irrespective of which contract is executed.

    KEYS_WITH_GTXN contains the BASE_KEYS for which the 2., 3. and 4. type of values should also be computed.
    For example, computing the 2., 3. and 4. type of information does not make sense for GroupSize and GroupIndex
    fields. These fields will not be included in KEYS_WITH_GTXN

ANALYSIS_KEYS: List of all keys used for the analysis.
ANALYSIS_KEYS contains BASE_KEYS and keys to represent type 2., 3. and 4. values for each key in KEYS_WITH_GTXN.

How are values for each type of key calculated?

For type (1), The comparisons made on the value accessed using `txn {field}` are used.

For type (2), ANALYSIS_KEYS contains a key for each KEYS_WITH_GTXN and all possible indices.
    - The analysis key with index `i` and `field` key of KEYS_WITH_GTXN will store information of type (2)
    - First, the information at block level and path level is computed using the comparisons made on the field
        accessed using an `gtxn` instruction with absolute index `i`.
    - The information will be of type (3) at this step. In order to make it of type (2), the type (1) information
        is combined with the information at block level and path level.
    - see DataflowTransactionContext._update_gtxn_constraints()


For every field type (1) is computed before type (2).
Computation of type (2) information requires the possible group indices, so possible group indices are computed before
any other field is analyzed.

Supported fields

addr_fields.AddrFields handles support of all address type transaction fields. Add the field name to BASE_KEYS to collect values
for a field.

fee_field.FeeField supports Fee field.

int_fields.GroupIndices supports GroupIndex and GroupSize fields.

txn_types.TxnType supports Transaction type.
"""
