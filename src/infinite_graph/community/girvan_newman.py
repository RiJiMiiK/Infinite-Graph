"""Girvan-Newman benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

from .estimation import (
    build_graph_structure_features,
    build_reference_points,
    finalize_estimate,
)


GIRVAN_NEWMAN_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = (
    build_reference_points(
        (
            (300.0, 1.0, 0.0, 0.0, 1.0, 0.4279, 2.0),
            (300.0, 1.0, 0.0, 0.0, 3.0, 0.7638, 4.0),
            (300.0, 1.0, 0.0, 0.0, 10.0, 1.3286, 11.0),
            (300.0, 2.0, 0.0, 1.0, 1.0, 0.8692, 2.0),
            (300.0, 2.0, 0.0, 1.0, 3.0, 1.6313, 4.0),
            (300.0, 2.0, 0.0, 1.0, 10.0, 2.3091, 11.0),
            (300.0, 3.0, 1.0, 1.0, 1.0, 0.8045, 2.0),
            (300.0, 3.0, 1.0, 1.0, 3.0, 1.4806, 4.0),
            (300.0, 3.0, 1.0, 1.0, 10.0, 1.8666, 11.0),
            (1000.0, 1.0, 0.0, 0.0, 1.0, 3.6071, 2.0),
            (1000.0, 1.0, 0.0, 0.0, 3.0, 7.2032, 4.0),
            (1000.0, 1.0, 0.0, 0.0, 10.0, 12.1562, 11.0),
            (1000.0, 2.0, 0.0, 1.0, 1.0, 7.5776, 2.0),
            (1000.0, 2.0, 0.0, 1.0, 3.0, 18.5216, 4.0),
            (1000.0, 2.0, 0.0, 1.0, 10.0, 20.1967, 11.0),
            (1000.0, 3.0, 1.0, 1.0, 1.0, 6.9701, 2.0),
            (1000.0, 3.0, 1.0, 1.0, 3.0, 11.7137, 4.0),
            (1000.0, 3.0, 1.0, 1.0, 10.0, 23.9271, 11.0),
        ),
        ("level",),
    )
)


def build_girvan_newman_estimation_features(
    graph: nx.DiGraph,
    parameters: Mapping[str, object],
) -> dict[str, float]:
    """Build normalized features for Girvan-Newman estimation."""
    return {
        **build_graph_structure_features(graph),
        "level": float(parameters.get("level", 3)),
    }


def girvan_newman_reference_distance(
    features: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    """Compute a weighted distance between current features and a benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 4.0
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 1.0
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 1.8
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.5
        + abs(
            math.log(
                max(features["level"] + 2.0, 1.0) / max(reference["level"] + 2.0, 1.0)
            )
        )
        * 1.3
    )


def estimate_girvan_newman_runtime_and_communities(
    graph: nx.DiGraph,
    **parameters: object,
) -> dict[str, object]:
    """Estimate Girvan-Newman runtime and community count from project benchmarks."""
    features = build_girvan_newman_estimation_features(graph, parameters)
    estimate = finalize_estimate(
        features,
        GIRVAN_NEWMAN_ESTIMATION_REFERENCE_POINTS,
        girvan_newman_reference_distance,
    )
    if int(round(features["level"])) >= 1:
        estimate["estimated_community_count"] = max(2, int(round(features["level"])) + 1)
    if int(round(features["level"])) <= -1:
        estimate["estimated_community_count"] = 0
        estimate["confidence"] = "low"
    return estimate
