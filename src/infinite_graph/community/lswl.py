"""LSWL benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

from .estimation import (
    build_graph_structure_features,
    build_reference_points,
    finalize_estimate,
)


LSWL_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = build_reference_points(
    (
        (20.0, 1.85, 0.0, 0.0, 2.0, 1.0, 0.0019, 1.0),
        (20.0, 2.0, 0.0, 1.0, 2.0, 1.0, 0.0014, 1.0),
        (20.0, 3.0, 1.0, 1.0, 2.0, 1.0, 0.0017, 1.0),
        (100.0, 1.97, 0.0, 0.0, 2.0, 1.0, 0.0053, 1.0),
        (100.0, 2.0, 0.0, 1.0, 2.0, 1.0, 0.0053, 1.0),
        (100.0, 3.0, 1.0, 1.0, 2.0, 1.0, 0.0043, 1.0),
        (300.0, 1.99, 0.0, 0.0, 2.0, 1.0, 0.0169, 1.0),
        (300.0, 2.0, 0.0, 1.0, 2.0, 1.0, 0.0228, 1.0),
        (300.0, 3.0, 1.0, 1.0, 2.0, 1.0, 0.0278, 1.0),
        (1000.0, 1.997, 0.0, 0.0, 2.0, 1.0, 0.1104, 1.0),
        (1000.0, 2.0, 0.0, 1.0, 2.0, 1.0, 0.1292, 1.0),
        (1000.0, 3.0, 1.0, 1.0, 2.0, 1.0, 0.1351, 1.0),
        (10000.0, 1.9997, 0.0, 0.0, 1.0, 10.0, 6.518, 1.0),
        (10000.0, 1.9997, 0.0, 0.0, 2.0, 10.0, 6.406, 1.0),
        (10000.0, 2.0, 0.0, 1.0, 1.0, 10.0, 5.456, 1.0),
        (10000.0, 2.0, 0.0, 1.0, 2.0, 10.0, 5.369, 1.0),
        (10000.0, 3.0, 1.0, 1.0, 1.0, 10.0, 5.596, 1.0),
        (10000.0, 3.0, 1.0, 1.0, 2.0, 10.0, 5.935, 1.0),
    ),
    ("strength_type", "timeout"),
)


def build_lswl_estimation_features(
    graph: nx.DiGraph,
    parameters: Mapping[str, object],
) -> dict[str, float]:
    """Build normalized features for LSWL estimation."""
    return {
        **build_graph_structure_features(graph),
        "strength_type": float(parameters.get("strength_type", 2)),
        "timeout": float(parameters.get("timeout", 1.0)),
    }


def lswl_reference_distance(
    features: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    """Compute a weighted distance between current features and an LSWL benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 4.0
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 1.0
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 1.8
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.4
        + abs(features["strength_type"] - reference["strength_type"]) * 0.2
        + abs(math.log(max(features["timeout"], 1e-9) / max(reference["timeout"], 1e-9))) * 1.6
    )


def estimate_lswl_runtime_and_communities(
    graph: nx.DiGraph,
    **parameters: object,
) -> dict[str, object]:
    """Estimate LSWL runtime and local-community size from project benchmark data."""
    features = build_lswl_estimation_features(graph, parameters)
    estimate = finalize_estimate(
        features,
        LSWL_ESTIMATION_REFERENCE_POINTS,
        lswl_reference_distance,
    )
    estimate["estimated_community_count"] = 1
    node_count = features["nodes"]
    timeout_value = features["timeout"]
    if node_count >= 10000 and timeout_value < 10.0:
        estimate["estimated_runtime_seconds"] = timeout_value
        estimate["confidence"] = "low"
        estimate["timeout_risk"] = "high"
    elif node_count >= 5000 and timeout_value < 10.0:
        estimate["confidence"] = "low"
        estimate["timeout_risk"] = "medium"
    else:
        estimate["timeout_risk"] = "low"
    estimate["collapse_risk"] = "high"
    return estimate
