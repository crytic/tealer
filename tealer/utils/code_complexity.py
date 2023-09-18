"""Util functions to compute code complexity of the contracts.

Module implements functions to calculate cyclomatic complexity of
the contract for now.

Functions:
    compute_cyclomatic_complexity(cfg: List["BasicBlock"]) -> int:
        Calculates the cyclomatic complexity of the contract given
        it's Control Flow Graph(CFG) :cfg:.

"""
# pylint: skip-file
# mypy: ignore-errors
# TODO: Functions in this module are not used anywhere. Have to decide on how to calculate the code complexity.

from typing import List, TYPE_CHECKING
from tealer.utils.analyses import next_blocks_global, prev_blocks_global

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock


# from slither: slither/utils/code_complexity.py
def _compute_number_edges(cfg: List["BasicBlock"]) -> int:
    """compute number of edges in the control flow graph of the contract.

    Args:
        cfg: Control Flow Graph(CFG) of the contract.

    Returns:
        number of edges in the CFG.
    """

    n = 0
    for bb in cfg:
        n += len(next_blocks_global(bb))
    return n


# from slither: slither/utils/code_complexity.py
def _compute_strongly_connected_components(cfg: List["BasicBlock"]) -> List[List["BasicBlock"]]:
    """Compute strongly connected components in the control flow graph.

    Implementation uses Kosaraju algorithm to find strongly connected
    components in the control flow graph of the contract. This follows
    the implementation described in the `Kosaraju algorithm wikipedia page`_.

    Args:
        cfg : Control Flow Graph(CFG) of the contract

    Returns:
        list of strongly connected components in CFG. each connected component
        is a list of basic blocks(nodes in CFG).

    .. _Kosaraju algorithm wikipedia page:
       https://en.wikipedia.org/wiki/Kosaraju%27s_algorithm#The_algorithm
    """

    visited = {bb: False for bb in cfg}
    assigned = {bb: False for bb in cfg}
    components = []

    l = []

    def visit(bb: "BasicBlock") -> None:
        if not visited[bb]:
            visited[bb] = True
            for next_bb in next_blocks_global(bb):
                visit(next_bb)
            l.append(bb)

    for bb in cfg:
        visit(bb)

    def assign(bb: "BasicBlock", root: List["BasicBlock"]) -> None:
        if not assigned[bb]:
            assigned[bb] = True
            root.append(bb)
            for prev_bb in prev_blocks_global(bb):
                assign(prev_bb, root)

    for bb in l:
        component: List["BasicBlock"] = []
        assign(bb, component)
        if component:
            components.append(component)

    return components


# from slither: slither/utils/code_complexity.py
def compute_cyclomatic_complexity(cfg: List["BasicBlock"]) -> int:
    """Compute cyclomatic complexity of the contract.

    Args:
        cfg: Control Flow Graph(CFG) of the contract.

    Returns:
        Cyclomatic complexity of the contract.
    """

    # from https://en.wikipedia.org/wiki/Cyclomatic_complexity
    # M = E - N + 2P
    # where M is the complexity
    # E number of edges
    # N number of nodes
    # P number of connected components

    E = _compute_number_edges(cfg)
    N = len(cfg)
    P = len(_compute_strongly_connected_components(cfg))
    return E - N + 2 * P
