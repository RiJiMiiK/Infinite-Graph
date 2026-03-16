"""Head/Tail benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

from .estimation import (
    build_graph_structure_features,
    build_reference_points,
    finalize_estimate,
)


HEAD_TAIL_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = build_reference_points(
    (
        (100.0, 1.0, 0.0, 0.0, 0.4, 0.1387, 16.0),
        (100.0, 2.0, 0.0, 1.0, 0.4, 0.1375, 18.0),
        (100.0, 3.0, 1.0, 1.0, 0.4, 0.1416, 100.0),
        (300.0, 1.0, 0.0, 0.0, 0.4, 1.0891, 8.0),
        (300.0, 2.0, 0.0, 1.0, 0.4, 1.1060, 18.0),
        (300.0, 3.0, 1.0, 1.0, 0.4, 1.1941, 300.0),
        (1000.0, 1.0, 0.0, 0.0, 0.1, 8.5051, 16.0),
        (1000.0, 1.0, 0.0, 0.0, 0.4, 11.7094, 16.0),
        (1000.0, 2.0, 0.0, 1.0, 0.4, 8.6853, 34.0),
        (1000.0, 3.0, 1.0, 1.0, 0.1, 10.9762, 1000.0),
        (1000.0, 3.0, 1.0, 1.0, 0.4, 11.9419, 1000.0),
    ),
    ("head_tail_ratio",),
)


def build_head_tail_estimation_features(
    graph: nx.DiGraph,
    parameters: Mapping[str, object],
) -> dict[str, float]:
    """Build normalized features for Head/Tail estimation."""
    return {
        **build_graph_structure_features(graph),
        "head_tail_ratio": float(parameters.get("head_tail_ratio", 0.4)),
    }


def head_tail_reference_distance(
    features: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    """Compute a weighted distance between current features and a benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 4.0
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 1.2
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 2.0
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.4
        + abs(features["head_tail_ratio"] - reference["head_tail_ratio"]) * 0.5
    )


def estimate_head_tail_runtime_and_communities(
    graph: nx.DiGraph,
    **parameters: object,
) -> dict[str, object]:
    """Estimate Head/Tail runtime and community count from project benchmark data."""
    features = build_head_tail_estimation_features(graph, parameters)
    estimate = finalize_estimate(
        features,
        HEAD_TAIL_ESTIMATION_REFERENCE_POINTS,
        head_tail_reference_distance,
    )
    if features["self_loop_ratio"] >= 0.5:
        estimate["singleton_risk"] = "high"
    elif features["self_loop_ratio"] > 0.0:
        estimate["singleton_risk"] = "medium"
    else:
        estimate["singleton_risk"] = "low"
    return estimate
