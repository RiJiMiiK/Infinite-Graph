"""Greedy Modularity benchmark-based estimation helpers."""

from __future__ import annotations

import math

import networkx as nx

from .estimation import (
    build_graph_structure_features,
    build_reference_points,
    finalize_estimate,
)


GREEDY_MODULARITY_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = (
    build_reference_points(
        (
            (20.0, 1.0, 0.0, 0.0, 0.0037, 5.0),
            (20.0, 2.0, 0.0, 1.0, 0.0029, 4.0),
            (20.0, 3.0, 1.0, 1.0, 0.0027, 6.0),
            (100.0, 1.0, 0.0, 0.0, 0.0087, 17.0),
            (100.0, 2.0, 0.0, 1.0, 0.0102, 16.0),
            (100.0, 3.0, 1.0, 1.0, 0.0096, 17.0),
            (300.0, 1.0, 0.0, 0.0, 0.0494, 25.0),
            (300.0, 2.0, 0.0, 1.0, 0.0561, 25.0),
            (300.0, 3.0, 1.0, 1.0, 0.0535, 25.0),
            (1000.0, 1.0, 0.0, 0.0, 0.1777, 41.0),
            (1000.0, 2.0, 0.0, 1.0, 0.1601, 41.0),
            (1000.0, 3.0, 1.0, 1.0, 0.1901, 45.0),
            (3000.0, 1.0, 0.0, 0.0, 0.5798, 64.0),
            (3000.0, 2.0, 0.0, 1.0, 0.6175, 65.0),
            (3000.0, 3.0, 1.0, 1.0, 0.5745, 65.0),
            (10000.0, 1.0, 0.0, 0.0, 2.0790, 105.0),
            (10000.0, 2.0, 0.0, 1.0, 2.1120, 105.0),
            (10000.0, 3.0, 1.0, 1.0, 2.1691, 208.0),
        )
    )
)


def greedy_modularity_reference_distance(
    features: dict[str, float],
    reference: dict[str, float],
) -> float:
    """Compute a weighted distance to a Greedy Modularity benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 3.8
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 1.0
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 1.8
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.4
    )


def estimate_greedy_modularity_runtime_and_communities(
    graph: nx.DiGraph,
) -> dict[str, object]:
    """Estimate Greedy Modularity runtime and community count from project benchmarks."""
    features = build_graph_structure_features(graph)
    return finalize_estimate(
        features,
        GREEDY_MODULARITY_ESTIMATION_REFERENCE_POINTS,
        greedy_modularity_reference_distance,
    )
