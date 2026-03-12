"""EM benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

from .community_estimation import (
    build_graph_structure_features,
    build_k_reference,
    finalize_estimate,
)


EM_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = (
    build_k_reference(100.0, 1.32, 0.0, 0.0, 2.0, 0.0045, 2.0),
    build_k_reference(100.0, 1.32, 0.0, 0.0, 3.0, 0.0065, 3.0),
    build_k_reference(100.0, 1.32, 0.0, 0.0, 5.0, 0.0104, 5.0),
    build_k_reference(100.0, 1.32, 0.0, 0.0, 10.0, 0.0200, 10.0),
    build_k_reference(100.0, 2.0, 0.0, 1.0, 2.0, 0.0041, 2.0),
    build_k_reference(100.0, 2.0, 0.0, 1.0, 3.0, 0.0046, 3.0),
    build_k_reference(100.0, 2.0, 0.0, 1.0, 5.0, 0.0117, 5.0),
    build_k_reference(100.0, 2.0, 0.0, 1.0, 10.0, 0.0368, 10.0),
    build_k_reference(100.0, 3.0, 1.0, 1.0, 2.0, 0.0055, 2.0),
    build_k_reference(100.0, 3.0, 1.0, 1.0, 3.0, 0.0276, 3.0),
    build_k_reference(100.0, 3.0, 1.0, 1.0, 5.0, 0.0291, 5.0),
    build_k_reference(100.0, 3.0, 1.0, 1.0, 10.0, 0.0505, 10.0),
    build_k_reference(1000.0, 1.333, 0.0, 0.0, 2.0, 0.0429, 2.0),
    build_k_reference(1000.0, 1.333, 0.0, 0.0, 3.0, 0.0877, 3.0),
    build_k_reference(1000.0, 1.333, 0.0, 0.0, 5.0, 0.1084, 5.0),
    build_k_reference(1000.0, 1.333, 0.0, 0.0, 10.0, 0.2529, 10.0),
    build_k_reference(1000.0, 2.0, 0.0, 1.0, 2.0, 0.0126, 2.0),
    build_k_reference(1000.0, 2.0, 0.0, 1.0, 3.0, 0.0118, 3.0),
    build_k_reference(1000.0, 2.0, 0.0, 1.0, 5.0, 0.0173, 5.0),
    build_k_reference(1000.0, 2.0, 0.0, 1.0, 10.0, 0.0353, 10.0),
    build_k_reference(1000.0, 3.0, 1.0, 1.0, 2.0, 0.0080, 2.0),
    build_k_reference(1000.0, 3.0, 1.0, 1.0, 3.0, 0.0127, 3.0),
    build_k_reference(1000.0, 3.0, 1.0, 1.0, 5.0, 0.0171, 5.0),
    build_k_reference(1000.0, 3.0, 1.0, 1.0, 10.0, 0.0318, 10.0),
    build_k_reference(10000.0, 1.3333, 0.0, 0.0, 10.0, 11.6020, 10.0),
    build_k_reference(10000.0, 1.3333, 0.0, 0.0, 15.0, 8.5078, 15.0),
    build_k_reference(10000.0, 1.3333, 0.0, 0.0, 20.0, 7.8280, 20.0),
    build_k_reference(10000.0, 1.3333, 0.0, 0.0, 30.0, 22.2000, 30.0),
    build_k_reference(10000.0, 2.0, 0.0, 1.0, 10.0, 0.4356, 10.0),
    build_k_reference(10000.0, 2.0, 0.0, 1.0, 15.0, 0.6060, 15.0),
    build_k_reference(10000.0, 2.0, 0.0, 1.0, 20.0, 0.8163, 20.0),
    build_k_reference(10000.0, 2.0, 0.0, 1.0, 30.0, 1.0561, 30.0),
    build_k_reference(10000.0, 3.0, 1.0, 1.0, 10.0, 0.3855, 10.0),
    build_k_reference(10000.0, 3.0, 1.0, 1.0, 15.0, 0.5771, 15.0),
    build_k_reference(10000.0, 3.0, 1.0, 1.0, 20.0, 0.7771, 20.0),
    build_k_reference(10000.0, 3.0, 1.0, 1.0, 30.0, 1.0221, 30.0),
)


def build_em_estimation_features(
    graph: nx.DiGraph,
    parameters: Mapping[str, object],
) -> dict[str, float]:
    """Build normalized features for EM estimation."""
    return {
        **build_graph_structure_features(graph),
        "k": float(parameters.get("k", 3)),
    }


def em_reference_distance(
    features: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    """Compute a weighted distance between current features and an EM benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 3.8
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 1.1
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 1.8
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.6
        + abs(features["k"] - reference["k"]) * 0.7
    )


def estimate_em_runtime_and_communities(
    graph: nx.DiGraph,
    **parameters: object,
) -> dict[str, object]:
    """Estimate EM runtime and community count from project benchmark data."""
    features = build_em_estimation_features(graph, parameters)
    estimate = finalize_estimate(
        features,
        EM_ESTIMATION_REFERENCE_POINTS,
        em_reference_distance,
    )
    estimate["estimated_community_count"] = max(1, int(round(features["k"])))
    return estimate
