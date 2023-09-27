from tealer.detectors.optimizations.self_access import SelfAccess

GTXN = """
#pragma version 3
txn GroupIndex
gtxns CloseRemainderTo
"""

self_access = [(GTXN, SelfAccess, [[2, 3]])]
