"""Async Fluid benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

from .community_estimation import build_graph_structure_features, finalize_estimate


def _reference(
    nodes: float,
    edges_per_node: float,
    self_loop_ratio: float,
    reciprocal_ratio: float,
    k_value: float,
    elapsed: float,
    communities: float,
) -> dict[str, float]:
    return {
        "nodes": nodes,
        "edges_per_node": edges_per_node,
        "self_loop_ratio": self_loop_ratio,
        "reciprocal_ratio": reciprocal_ratio,
        "k": k_value,
        "elapsed": elapsed,
        "communities": communities,
    }


ASYNC_FLUID_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = (
    _reference(20.0, 0.95, 0.0, 0.0, 2.0, 0.0008, 2.0),
    _reference(20.0, 0.95, 0.0, 0.0, 3.0, 0.0006, 3.0),
    _reference(20.0, 0.95, 0.0, 0.0, 5.0, 0.0003, 5.0),
    _reference(20.0, 2.05, 0.0, 1.05, 2.0, 0.0006, 2.0),
    _reference(20.0, 2.05, 0.0, 1.05, 3.0, 0.0003, 3.0),
    _reference(20.0, 2.05, 0.0, 1.05, 5.0, 0.0002, 5.0),
    _reference(20.0, 3.05, 1.0, 1.05, 2.0, 0.0004, 2.0),
    _reference(20.0, 3.05, 1.0, 1.05, 3.0, 0.0003, 3.0),
    _reference(20.0, 3.05, 1.0, 1.05, 5.0, 0.0004, 5.0),
    _reference(100.0, 0.99, 0.0, 0.0, 2.0, 0.0133, 2.0),
    _reference(100.0, 0.99, 0.0, 0.0, 3.0, 0.0059, 3.0),
    _reference(100.0, 0.99, 0.0, 0.0, 5.0, 0.0084, 5.0),
    _reference(100.0, 2.01, 0.0, 1.01, 2.0, 0.0027, 2.0),
    _reference(100.0, 2.01, 0.0, 1.01, 3.0, 0.0024, 3.0),
    _reference(100.0, 2.01, 0.0, 1.01, 5.0, 0.0025, 5.0),
    _reference(100.0, 3.01, 1.0, 1.01, 2.0, 0.0026, 2.0),
    _reference(100.0, 3.01, 1.0, 1.01, 3.0, 0.0033, 3.0),
    _reference(100.0, 3.01, 1.0, 1.01, 5.0, 0.0040, 5.0),
    _reference(300.0, 0.9966666667, 0.0, 0.0, 2.0, 0.0648, 2.0),
    _reference(300.0, 0.9966666667, 0.0, 0.0, 3.0, 0.0452, 3.0),
    _reference(300.0, 0.9966666667, 0.0, 0.0, 5.0, 0.0351, 5.0),
    _reference(300.0, 2.0033333333, 0.0, 1.0033333333, 2.0, 0.0145, 2.0),
    _reference(300.0, 2.0033333333, 0.0, 1.0033333333, 3.0, 0.0296, 3.0),
    _reference(300.0, 2.0033333333, 0.0, 1.0033333333, 5.0, 0.0241, 5.0),
    _reference(300.0, 3.0033333333, 1.0, 1.0033333333, 2.0, 0.0199, 2.0),
    _reference(300.0, 3.0033333333, 1.0, 1.0033333333, 3.0, 0.0167, 3.0),
    _reference(300.0, 3.0033333333, 1.0, 1.0033333333, 5.0, 0.0163, 5.0),
    _reference(1000.0, 0.999, 0.0, 0.0, 2.0, 0.2049, 2.0),
    _reference(1000.0, 0.999, 0.0, 0.0, 3.0, 0.2934, 3.0),
    _reference(1000.0, 0.999, 0.0, 0.0, 5.0, 0.4329, 5.0),
    _reference(1000.0, 2.001, 0.0, 1.001, 2.0, 0.1797, 2.0),
    _reference(1000.0, 2.001, 0.0, 1.001, 3.0, 0.5014, 3.0),
    _reference(1000.0, 2.001, 0.0, 1.001, 5.0, 0.3042, 5.0),
    _reference(1000.0, 3.001, 1.0, 1.001, 2.0, 0.2746, 2.0),
    _reference(1000.0, 3.001, 1.0, 1.001, 3.0, 0.3410, 3.0),
    _reference(1000.0, 3.001, 1.0, 1.001, 5.0, 0.3361, 5.0),
)


def build_async_fluid_estimation_features(
    graph: nx.DiGraph,
    parameters: Mapping[str, object],
) -> dict[str, float]:
    """Build normalized features for Async Fluid estimation."""
    return {
        **build_graph_structure_features(graph),
        "k": float(parameters.get("k", 2)),
    }


def async_fluid_reference_distance(
    features: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    """Compute a weighted distance between current features and a benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 3.5
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 1.3
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 1.6
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.4
        + abs(features["k"] - reference["k"]) * 0.8
    )


def estimate_async_fluid_runtime_and_communities(
    graph: nx.DiGraph,
    **parameters: object,
) -> dict[str, object]:
    """Estimate Async Fluid runtime and community count from project benchmark data."""
    features = build_async_fluid_estimation_features(graph, parameters)
    estimate = finalize_estimate(
        features,
        ASYNC_FLUID_ESTIMATION_REFERENCE_POINTS,
        async_fluid_reference_distance,
    )
    estimate["estimated_community_count"] = max(2, int(round(features["k"])))
    return estimate
