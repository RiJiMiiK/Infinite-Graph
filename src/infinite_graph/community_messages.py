"""User-facing community-analysis message helpers."""

from __future__ import annotations

import networkx as nx


def format_mono_community_algorithm_failure(
    algorithm_name: str,
    error: Exception,
    graph: nx.DiGraph | None = None,
) -> str:
    """Return a user-facing failure description for a mono-community run."""
    details = str(error)
    if algorithm_name == "eigenvector" and (
        "ARPACK error" in details or "No eigenvalues to sufficient accuracy" in details
    ):
        node_count = None
        if graph is not None and hasattr(graph, "number_of_nodes"):
            node_count = graph.number_of_nodes()
        graph_line = (
            f"Graph size: {node_count} nodes.\n"
            if isinstance(node_count, int)
            else ""
        )
        return (
            "Unable to compute communities with the selected algorithm.\n\n"
            "Algorithm: eigenvector\n"
            f"{graph_line}"
            "Details: ARPACK could not compute eigenvalues with sufficient accuracy "
            "on this graph.\n"
            "Recommendation: try a smaller subgraph or switch to another algorithm for large saves."
        )
    return (
        "Unable to compute communities with the selected algorithm.\n\n"
        f"Algorithm: {algorithm_name}\n"
        f"Details: {details}"
    )
