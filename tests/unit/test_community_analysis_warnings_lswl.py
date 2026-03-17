from __future__ import annotations

import networkx as nx

from src.infinite_graph.community import (
    analysis as community_analysis,
    lswl as community_lswl,
)


def test_estimate_lswl_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_lswl.estimate_lswl_runtime_and_communities(
        graph,
        strength_type=2,
        timeout=1.0,
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) == 1
    assert estimate["confidence"] in {"high", "medium", "low"}
    assert estimate["timeout_risk"] in {"high", "medium", "low"}
    assert estimate["collapse_risk"] == "high"


def test_estimate_lswl_runtime_and_communities_high_timeout_risk() -> None:
    graph = nx.DiGraph()
    for index in range(10000):
        graph.add_node(str(index))
    for index in range(9999):
        graph.add_edge(str(index), str(index + 1), weight=1.0)
        if index + 2 < 10000:
            graph.add_edge(str(index), str(index + 2), weight=2.0)

    estimate = community_lswl.estimate_lswl_runtime_and_communities(
        graph,
        strength_type=2,
        timeout=5.0,
    )

    assert estimate["timeout_risk"] == "high"
    assert estimate["confidence"] == "low"
    assert float(estimate["estimated_runtime_seconds"]) == 5.0


def test_estimate_lswl_runtime_and_communities_medium_timeout_risk() -> None:
    graph = nx.DiGraph()
    for index in range(5000):
        graph.add_node(str(index))
    for index in range(4999):
        graph.add_edge(str(index), str(index + 1), weight=1.0)
        if index + 2 < 5000:
            graph.add_edge(str(index), str(index + 2), weight=2.0)

    estimate = community_lswl.estimate_lswl_runtime_and_communities(
        graph,
        strength_type=2,
        timeout=5.0,
    )

    assert estimate["timeout_risk"] == "medium"
    assert estimate["confidence"] == "low"
    assert float(estimate["estimated_runtime_seconds"]) > 0.0


def test_get_mono_community_algorithm_pre_run_warning_for_lswl() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "lswl",
        graph,
        {"strength_type": 2, "timeout": 1.0, "query_node": "A"},
    )

    assert warning is not None
    assert "LSWL benchmark-based estimate" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Estimated timeout risk:" in warning
    assert "Estimated single-community collapse risk:" in warning
