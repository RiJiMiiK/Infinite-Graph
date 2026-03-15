"""AGDL benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

from .estimation import (
    build_graph_structure_features,
    build_reference_points,
    finalize_estimate,
)


AGDL_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = build_reference_points(
    (
        (20.0, 2.85, 0.0, 0.0, 3.0, 2.0, 0.0008, 1.0),
        (20.0, 4.0, 0.0, 2.0, 3.0, 2.0, 0.0003, 1.0),
        (100.0, 0.99, 0.0, 0.0, 5.0, 4.0, 0.0013, 1.0),
        (100.0, 1.98, 0.0, 0.99, 5.0, 4.0, 0.0011, 1.0),
        (300.0, 0.9966666667, 0.0, 0.0, 10.0, 8.0, 0.0048, 1.0),
        (1000.0, 0.999, 0.0, 0.0, 20.0, 16.0, 0.0207, 1.0),
    ),
    ("number_communities", "kc"),
)


def build_agdl_estimation_features(
    graph: nx.DiGraph,
    parameters: Mapping[str, object],
) -> dict[str, float]:
    """Build normalized features for AGDL estimation."""
    return {
        **build_graph_structure_features(graph),
        "number_communities": float(parameters.get("number_communities", 3)),
        "kc": float(parameters.get("kc", 2)),
    }


def agdl_reference_distance(
    features: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    """Compute a weighted distance between current features and an AGDL benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 3.0
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 0.8
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 3.0
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.2
        + abs(
            math.log(
                max(features["number_communities"], 1.0)
                / max(reference["number_communities"], 1.0)
            )
        )
        * 0.6
        + abs(math.log(max(features["kc"], 1.0) / max(reference["kc"], 1.0))) * 0.6
    )


def estimate_agdl_runtime_and_communities(
    graph: nx.DiGraph,
    **parameters: object,
) -> dict[str, object]:
    """Estimate AGDL runtime and community count from project benchmark data."""
    features = build_agdl_estimation_features(graph, parameters)
    estimate = finalize_estimate(
        features,
        AGDL_ESTIMATION_REFERENCE_POINTS,
        agdl_reference_distance,
    )
    estimate["confidence"] = "low"
    return estimate
