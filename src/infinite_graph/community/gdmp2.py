"""GDMP2 benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

from .estimation import (
    build_graph_structure_features,
    build_reference_points,
    finalize_estimate,
)


GDMP2_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = build_reference_points(
    (
        (20.0, 1.45, 0.0, 0.0, 0.75, 0.0054, 1.0),
        (20.0, 2.0, 0.0, 1.0, 0.75, 0.0037, 1.0),
        (20.0, 3.0, 1.0, 1.0, 0.75, 0.0043, 1.0),
        (100.0, 1.32, 0.0, 0.0, 0.75, 0.0769, 1.0),
        (100.0, 2.0, 0.0, 1.0, 0.75, 0.0709, 1.0),
        (100.0, 3.0, 1.0, 1.0, 0.75, 0.0755, 1.0),
        (300.0, 1.33, 0.0, 0.0, 0.001, 1.0839, 1.0),
        (300.0, 1.33, 0.0, 0.0, 0.05, 1.3508, 2.0),
        (300.0, 1.33, 0.0, 0.0, 0.75, 1.2321, 1.0),
        (300.0, 2.0, 0.0, 1.0, 0.001, 1.2566, 1.0),
        (300.0, 2.0, 0.0, 1.0, 0.05, 1.1032, 1.0),
        (300.0, 2.0, 0.0, 1.0, 0.75, 0.7307, 1.0),
        (300.0, 3.0, 1.0, 1.0, 0.001, 1.1588, 1.0),
        (300.0, 3.0, 1.0, 1.0, 0.05, 1.0672, 1.0),
        (300.0, 3.0, 1.0, 1.0, 0.75, 0.6642, 1.0),
    ),
    ("min_threshold",),
)


def build_gdmp2_estimation_features(
    graph: nx.DiGraph,
    parameters: Mapping[str, object],
) -> dict[str, float]:
    """Build normalized features for GDMP2 estimation."""
    return {
        **build_graph_structure_features(graph),
        "min_threshold": float(parameters.get("min_threshold", 0.75)),
    }


def gdmp2_reference_distance(
    features: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    """Compute a weighted distance between current features and a GDMP2 benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 4.2
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 1.2
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 2.2
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.5
        + abs(
            math.log(
                max(features["min_threshold"], 1e-9)
                / max(reference["min_threshold"], 1e-9)
            )
        )
        * 1.2
    )


def estimate_gdmp2_runtime_and_communities(
    graph: nx.DiGraph,
    **parameters: object,
) -> dict[str, object]:
    """Estimate GDMP2 runtime and community count from project benchmark data."""
    features = build_gdmp2_estimation_features(graph, parameters)
    estimate = finalize_estimate(
        features,
        GDMP2_ESTIMATION_REFERENCE_POINTS,
        gdmp2_reference_distance,
    )
    if features["nodes"] >= 1000:
        estimate["confidence"] = "low"
        estimate["recursion_risk"] = "high"
    elif features["nodes"] >= 700:
        estimate["confidence"] = "low"
        estimate["recursion_risk"] = "medium"
    elif features["nodes"] >= 500:
        estimate["recursion_risk"] = "medium"
    else:
        estimate["recursion_risk"] = "low"
    return estimate
