from tealer.detectors.optimizations.constant_gtxn import ConstantGtxn

GTXN = """
#pragma version 3
int 1
gtxns CloseRemainderTo
int 1
"""

constant_gtxn = [(GTXN, ConstantGtxn, [[2, 3]])]
