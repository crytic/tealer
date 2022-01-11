from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from tealer.teal.basic_blocks import BasicBlock


# Copy from https://github.com/crytic/slither/blob/master/slither/utils/code_complexity.py


def _compute_number_edges(cfg: List["BasicBlock"]) -> int:
    """compute number of edges in the control flow graph of the contract."""
    n = 0
    for bb in cfg:
        n += len(bb.next)
    return n


def _compute_strongly_connected_components(cfg: List["BasicBlock"]) -> List[List["BasicBlock"]]:
    """Compute strongly connected components
        Based on Kosaraju algo
        Implem follows wikipedia algo: https://en.wikipedia.org/wiki/Kosaraju%27s_algorithm#The_algorithm
    Args:
        cfg (List[BasicBlock]): cfg of the contract
    Returns:
        List[List[BasicBlock]]: List of strongly connected components

    """
    visited = {bb: False for bb in cfg}
    assigned = {bb: False for bb in cfg}
    components = []

    l = []

    def visit(bb: "BasicBlock") -> None:
        if not visited[bb]:
            visited[bb] = True
            for next_bb in bb.next:
                visit(next_bb)
            l.append(bb)

    for bb in cfg:
        visit(bb)

    def assign(bb: "BasicBlock", root: List["BasicBlock"]) -> None:
        if not assigned[bb]:
            assigned[bb] = True
            root.append(bb)
            for prev_bb in bb.prev:
                assign(prev_bb, root)

    for bb in l:
        component: List["BasicBlock"] = []
        assign(bb, component)
        if component:
            components.append(component)

    return components


def compute_cyclomatic_complexity(cfg: List["BasicBlock"]) -> int:
    """Compute the cyclomatic complexity of the program

    Args:
        cfg (List[BasicBlock]): cfg of the contract.
    Returns:
        (int): cyclomatic complexity of the contract.

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
