from tealer.detectors.optimizations.constant_gtxn import ConstantGtxn

GTXN = """
#pragma version 3
int 1
gtxns CloseRemainderTo
"""

constant_gtxn = [(GTXN, ConstantGtxn, [[2, 3]])]
