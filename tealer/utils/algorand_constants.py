MAX_GROUP_SIZE = 16
MIN_ALGORAND_FEE = 1000  # in micro algos
ZERO_ADDRESS = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEVAL4QAJS7JHB4"
MAX_UINT64 = (1 << 64) - 1  # 2**64 - 1
# Maximum number of inner transactions a group transaction can have.
MAX_NUM_INNER_TXN = 256

# Over estimation of maximum cost a transaction can consume.
# There can be a maximum of 256 inner transactions in a group.
# There can be maximum of 16 transactions in a group.
# Each inner txn and txn costs MIN_ALGORAND Fee
MAX_TRANSACTION_COST = (MAX_GROUP_SIZE + MAX_NUM_INNER_TXN) * MIN_ALGORAND_FEE
