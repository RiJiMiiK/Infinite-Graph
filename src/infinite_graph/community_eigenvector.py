"""Eigenvector benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

from .community_estimation import (
    build_graph_structure_features,
    build_reference_points,
    finalize_estimate,
)

EIGENVECTOR_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = build_reference_points(
    (
        (20.0, 1.45, 0.0, 0.0, 0.0014, 4.0),
        (20.0, 2.0, 0.0, 1.0, 0.0006, 4.0),
        (20.0, 3.0, 1.0, 1.0, 0.0009, 4.0),
        (100.0, 1.32, 0.0, 0.0, 0.0027, 8.0),
        (100.0, 2.0, 0.0, 1.0, 0.0023, 8.0),
        (100.0, 3.0, 1.0, 1.0, 0.0026, 8.0),
        (300.0, 1.33, 0.0, 0.0, 0.0151, 20.0),
        (300.0, 2.0, 0.0, 1.0, 0.0161, 16.0),
        (300.0, 3.0, 1.0, 1.0, 0.0154, 16.0),
        (1000.0, 1.33, 0.0, 0.0, 0.1397, 33.0),
        (1000.0, 2.0, 0.0, 1.0, 0.1572, 32.0),
        (1000.0, 3.0, 1.0, 1.0, 0.1645, 32.0),
        (3000.0, 1.333, 0.0, 0.0, 3.9089, 54.0),
        (3000.0, 2.0, 0.0, 1.0, 5.7967, 32.0),
        (3000.0, 3.0, 1.0, 1.0, 4.8009, 64.0),
        (10195.0, 9.9873467386, 0.6038254046, 0.0094163806, 6.5531, 0.0),
    ),
)


def build_eigenvector_estimation_features(graph: nx.DiGraph) -> dict[str, float]:
    """Build normalized features for Eigenvector estimation."""
    return build_graph_structure_features(graph)


def eigenvector_reference_distance(
    features: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    """Compute a weighted distance between current features and an Eigenvector benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 4.5
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 0.8
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 3.0
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.4
    )


def estimate_eigenvector_runtime_and_communities(
    graph: nx.DiGraph,
) -> dict[str, object]:
    """Estimate Eigenvector runtime and community count from project benchmark data."""
    features = build_eigenvector_estimation_features(graph)
    estimate = finalize_estimate(
        features,
        EIGENVECTOR_ESTIMATION_REFERENCE_POINTS,
        eigenvector_reference_distance,
    )
    if features["nodes"] >= 5000:
        estimate["confidence"] = "low"
    if features["nodes"] >= 8000 or features["self_loop_ratio"] >= 0.2:
        estimate["arpack_risk"] = "high"
    elif features["nodes"] >= 3000:
        estimate["arpack_risk"] = "medium"
    else:
        estimate["arpack_risk"] = "low"
    return estimate
