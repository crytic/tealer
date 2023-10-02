from tealer.detectors.optimizations.sender_access import SenderAccess

SENDER_ACCESS = """
#pragma version 3
int 1
txna Accounts 0
int 2
"""

sender_access = [(SENDER_ACCESS, SenderAccess, [[3]])]
