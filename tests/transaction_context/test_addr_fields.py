from typing import Tuple, List
import pytest

from tealer.utils.command_line.common import init_tealer_from_single_contract
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
rekeyto: List[List[str]] = [[] for _ in range(11)]
rekeyto_values = (rekeyto_any, rekeyto_none, rekeyto)

closeto_any = [False] * 11
closeto_none = [True] * 11
closeto: List[List[str]] = [[] for _ in range(11)]
closeto_values = (closeto_any, closeto_none, closeto)

assetcloseto_any = [False] * 11
assetcloseto_none = [True] * 11
assetcloseto: List[List[str]] = [[] for _ in range(11)]
assetcloseto_values = (assetcloseto_any, assetcloseto_none, assetcloseto)

BRANCHING_ADDR_VALUES = [
    rekeyto_values,
    closeto_values,
    assetcloseto_values,
]

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
def test_addr_fields(  # pylint: disable=too-many-locals
    test: Tuple[str, List[Tuple[List[bool], List[bool], List[List[str]]]], int]
) -> None:
    code, values, idx = test
    tealer = init_tealer_from_single_contract(code.strip(), "test")
    function = tealer.contracts["test"].functions["test"]
    ex_rekeyto_any, ex_rekeyto_none, ex_rekeyto = values[0]
    ex_closeto_any, ex_closeto_none, ex_closeto = values[1]
    ex_assetcloseto_any, ex_assetcloseto_none, ex_assetcloseto = values[2]

    bbs = order_basic_blocks(function.blocks)
    for b in bbs:
        if idx == -1:
            ctx = function.transaction_context(b)
        else:
            ctx = function.transaction_context(b).gtxn_context(idx)

        assert ctx.rekeyto.any_addr == ex_rekeyto_any[b.idx]
        assert ctx.rekeyto.no_addr == ex_rekeyto_none[b.idx]
        assert set(ctx.rekeyto.possible_addr) == set(ex_rekeyto[b.idx])

        assert ctx.closeto.any_addr == ex_closeto_any[b.idx]
        assert ctx.closeto.no_addr == ex_closeto_none[b.idx]
        assert set(ctx.closeto.possible_addr) == set(ex_closeto[b.idx])

        assert ctx.assetcloseto.any_addr == ex_assetcloseto_any[b.idx]
        assert ctx.assetcloseto.no_addr == ex_assetcloseto_none[b.idx]
        assert set(ctx.assetcloseto.possible_addr) == set(ex_assetcloseto[b.idx])
