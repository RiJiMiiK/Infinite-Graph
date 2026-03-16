"""Kcut benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

from .estimation import build_graph_structure_features, build_reference_points, finalize_estimate


KCUT_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = build_reference_points(
    (
        (20.0, 2.65, 0.0, 0.0, 2.0, 5.1897, 4.0),
        (20.0, 2.65, 0.0, 0.0, 3.0, 0.1205, 6.0),
        (20.0, 2.65, 0.0, 0.0, 4.0, 0.1600, 8.0),
        (20.0, 2.65, 0.0, 0.0, 5.0, 0.2200, 9.0),
        (20.0, 2.65, 0.0, 0.0, 8.0, 0.4678, 9.0),
        (20.0, 2.65, 0.0, 0.0, 10.0, 0.6415, 9.0),
        (20.0, 3.0, 0.0, 1.5, 2.0, 0.0562, 4.0),
        (20.0, 3.0, 0.0, 1.5, 3.0, 0.1113, 6.0),
        (20.0, 3.0, 0.0, 1.5, 4.0, 0.1956, 8.0),
        (20.0, 3.0, 0.0, 1.5, 5.0, 0.2362, 9.0),
        (20.0, 3.0, 0.0, 1.5, 8.0, 0.4915, 9.0),
        (20.0, 3.0, 0.0, 1.5, 10.0, 0.8365, 10.0),
        (20.0, 4.0, 1.0, 1.5, 2.0, 0.0583, 4.0),
        (20.0, 4.0, 1.0, 1.5, 3.0, 0.1140, 6.0),
        (20.0, 4.0, 1.0, 1.5, 4.0, 0.1729, 8.0),
        (20.0, 4.0, 1.0, 1.5, 5.0, 0.2723, 9.0),
        (20.0, 4.0, 1.0, 1.5, 8.0, 0.5646, 14.0),
        (20.0, 4.0, 1.0, 1.5, 10.0, 0.8708, 12.0),
        (100.0, 2.92, 0.0, 0.0, 2.0, 0.3966, 4.0),
        (100.0, 2.92, 0.0, 0.0, 3.0, 0.6912, 6.0),
        (100.0, 2.92, 0.0, 0.0, 4.0, 1.0227, 8.0),
        (100.0, 2.92, 0.0, 0.0, 5.0, 1.3617, 10.0),
        (100.0, 2.92, 0.0, 0.0, 8.0, 2.8784, 16.0),
        (100.0, 2.92, 0.0, 0.0, 10.0, 4.0934, 19.0),
        (100.0, 3.0, 0.0, 1.5, 2.0, 0.3988, 4.0),
        (100.0, 3.0, 0.0, 1.5, 3.0, 0.6947, 6.0),
        (100.0, 3.0, 0.0, 1.5, 4.0, 1.0759, 8.0),
        (100.0, 3.0, 0.0, 1.5, 5.0, 1.4830, 10.0),
        (100.0, 3.0, 0.0, 1.5, 8.0, 2.8650, 16.0),
        (100.0, 3.0, 0.0, 1.5, 10.0, 3.9559, 20.0),
        (100.0, 4.0, 1.0, 1.5, 2.0, 0.4025, 4.0),
        (100.0, 4.0, 1.0, 1.5, 3.0, 0.7266, 6.0),
        (100.0, 4.0, 1.0, 1.5, 4.0, 1.1282, 8.0),
        (100.0, 4.0, 1.0, 1.5, 5.0, 1.5191, 10.0),
        (100.0, 4.0, 1.0, 1.5, 8.0, 2.9755, 16.0),
        (100.0, 4.0, 1.0, 1.5, 10.0, 4.2601, 20.0),
        (300.0, 2.9766666667, 0.0, 0.0, 2.0, 2.8846, 4.0),
        (300.0, 2.9766666667, 0.0, 0.0, 3.0, 4.8362, 6.0),
        (300.0, 2.9766666667, 0.0, 0.0, 4.0, 7.0049, 8.0),
        (300.0, 2.9766666667, 0.0, 0.0, 5.0, 9.7750, 10.0),
        (300.0, 2.9766666667, 0.0, 0.0, 8.0, 18.9163, 16.0),
        (300.0, 2.9766666667, 0.0, 0.0, 10.0, 31.0474, 20.0),
        (300.0, 3.0, 0.0, 1.5, 2.0, 3.3643, 4.0),
        (300.0, 3.0, 0.0, 1.5, 3.0, 5.5834, 6.0),
        (300.0, 3.0, 0.0, 1.5, 4.0, 8.6448, 8.0),
        (300.0, 3.0, 0.0, 1.5, 5.0, 11.2429, 10.0),
        (300.0, 3.0, 0.0, 1.5, 8.0, 18.4259, 16.0),
        (300.0, 3.0, 0.0, 1.5, 10.0, 26.6548, 20.0),
        (300.0, 4.0, 1.0, 1.5, 2.0, 3.0065, 4.0),
        (300.0, 4.0, 1.0, 1.5, 3.0, 5.1468, 6.0),
        (300.0, 4.0, 1.0, 1.5, 4.0, 7.5726, 8.0),
        (300.0, 4.0, 1.0, 1.5, 5.0, 9.8935, 10.0),
        (300.0, 4.0, 1.0, 1.5, 8.0, 23.5617, 16.0),
        (300.0, 4.0, 1.0, 1.5, 10.0, 32.8068, 20.0),
        (1000.0, 2.992, 0.0, 0.0, 4.0, 88.8809, 8.0),
        (1000.0, 3.0, 0.0, 1.5, 4.0, 112.1901, 8.0),
        (1000.0, 4.0, 1.0, 1.5, 4.0, 82.0082, 8.0),
    ),
    ("kmax",),
)


def build_kcut_estimation_features(
    graph: nx.DiGraph,
    parameters: Mapping[str, object],
) -> dict[str, float]:
    """Build normalized features for Kcut estimation."""
    return {
        **build_graph_structure_features(graph),
        "kmax": float(max(1, int(parameters.get("kmax", 4)))),
    }


def kcut_reference_distance(
    features: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    """Compute a weighted distance between current features and a Kcut benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 4.5
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 1.0
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 2.0
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.6
        + abs(features["kmax"] - reference["kmax"]) * 0.8
    )


def estimate_kcut_runtime_and_communities(
    graph: nx.DiGraph,
    **parameters: object,
) -> dict[str, object]:
    """Estimate Kcut runtime and community count from project benchmark data."""
    features = build_kcut_estimation_features(graph, parameters)
    estimate = finalize_estimate(
        features,
        KCUT_ESTIMATION_REFERENCE_POINTS,
        kcut_reference_distance,
    )
    estimated_communities = int(estimate["estimated_community_count"])
    singleton_ratio = max(0.0, float(estimated_communities - 1)) / max(
        1.0,
        features["nodes"],
    )
    if singleton_ratio >= 0.12:
        estimate["degenerate_partition_risk"] = "high"
    elif singleton_ratio >= 0.04:
        estimate["degenerate_partition_risk"] = "medium"
    else:
        estimate["degenerate_partition_risk"] = "low"
    if features["nodes"] >= 1000:
        estimate["confidence"] = "low"
    return estimate
