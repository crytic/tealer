from tealer.detectors.optimizations.send_access import SelfAccess

GTXN = """
#pragma version 3
txn group index
gtxns CloseRemainderTo
"""

self_access = [(GTXN, SelfAccess, [[2, 3]])]
