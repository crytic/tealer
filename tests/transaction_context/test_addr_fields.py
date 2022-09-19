from typing import Tuple, List
import pytest

from tealer.teal.context.block_transaction_context import BlockTransactionContext
from tealer.teal.parse_teal import parse_teal
from tests.utils import order_basic_blocks


BRANCHING_ADDR = """
#pragma version 2
txn Receiver
addr 6ZIOGDXGSQSL4YINHLKCHYRV64FSN4LTUIQ6A4VWYK36FXFF42VI2UV7SM
==
bz wrongreceiver
txn Fee
int 10000
<
bz highfee
txn CloseRemainderTo
global ZeroAddress
==
bz closing_account
txn AssetCloseTo
global ZeroAddress
==
bz closing_asset
global GroupSize
int 1
==
bz unexpected_group_size
int 1
return
wrongreceiver:
highfee:
closing_account:
closing_asset:
unexpected_group_size:
    err
"""

rekeyto_any = [True] * 6 + [False] * 5
rekeyto_none = [False] * 6 + [True] * 5
rekeyto = [list() for _ in range(11)]

closeto_any = [False] * 11
closeto_none = [True] * 11
closeto = [list() for _ in range(11)]

assetcloseto_any = [False] * 11
assetcloseto_none = [True] * 11
assetcloseto = [list() for _ in range(11)]

BRANCHING_ADDR_VALUES = [rekeyto_any, rekeyto_none, rekeyto, closeto_any, closeto_none, closeto, assetcloseto_any, assetcloseto_none, assetcloseto]

BRANCHING_ADDR_GTXN = """
#pragma version 2
txn Receiver
addr 6ZIOGDXGSQSL4YINHLKCHYRV64FSN4LTUIQ6A4VWYK36FXFF42VI2UV7SM
==
bz wrongreceiver
txn Fee
int 10000
<
bz highfee
gtxn 0 CloseRemainderTo
global ZeroAddress
==
bz closing_account
gtxn 0 AssetCloseTo
addr AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEVAL4QAJS7JHB4
==
bz closing_asset
global GroupSize
int 1
==
bz unexpected_group_size
int 1
return
wrongreceiver:
highfee:
closing_account:
closing_asset:
unexpected_group_size:
    err
"""

ALL_TESTS_TXN = [
    (BRANCHING_ADDR, BRANCHING_ADDR_VALUES, -1),
    (BRANCHING_ADDR_GTXN, BRANCHING_ADDR_VALUES, 0),
]


@pytest.mark.parametrize("test", ALL_TESTS_TXN)  # type: ignore
def test_cfg_construction(test: Tuple[str, List[List[int]]]) -> None:
    code, values, idx = test
    teal = parse_teal(code.strip())

    rekeyto_any, rekeyto_none, rekeyto = values[:3]
    closeto_any, assetcloseto_none, closeto = values[3: 6]
    assetcloseto_any, assetcloseto_none, assetcloseto = values[6: 9]

    bbs = order_basic_blocks(teal.bbs)
    for b in bbs:
        if idx == -1:
            ctx = b.transaction_context
        else:
            ctx = b.transaction_context.gtxn_context(idx)

        assert ctx.any_rekeyto == rekeyto_any[b.idx]
        assert ctx.none_rekeyto == rekeyto_none[b.idx]
        assert set(ctx.rekeyto) == set(rekeyto[b.idx])
        
        assert ctx.any_closeto == closeto_any[b.idx]
        assert ctx.none_closeto == closeto_none[b.idx]
        assert set(ctx.closeto) == set(closeto[b.idx])
        
        assert ctx.any_assetcloseto == assetcloseto_any[b.idx]
        assert ctx.none_assetcloseto == assetcloseto_none[b.idx]
        assert set(ctx.assetcloseto) == set(assetcloseto[b.idx])
