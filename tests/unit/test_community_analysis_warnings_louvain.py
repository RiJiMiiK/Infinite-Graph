from __future__ import annotations

import networkx as nx

from src.infinite_graph.community import (
    analysis as community_analysis,
    louvain as community_louvain,
)


def test_estimate_louvain_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_louvain.estimate_louvain_runtime_and_communities(
        graph,
        resolution=2.0,
        randomize=7,
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) >= 1
    assert estimate["confidence"] in {"high", "medium", "low"}


def test_get_mono_community_algorithm_pre_run_warning_for_louvain() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "louvain",
        graph,
        {"resolution": 2.0, "randomize": 7},
    )

    assert warning is not None
    assert "Louvain benchmark-based estimate" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning
    assert "resolution is the main community-granularity control" in warning
