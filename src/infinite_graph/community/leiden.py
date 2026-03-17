"""Leiden benchmark-based estimation helpers."""

from __future__ import annotations

import math

import networkx as nx

from .estimation import (
    build_graph_structure_features,
    build_reference_points,
    finalize_estimate,
)


LEIDEN_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = build_reference_points(
    (
        (20.0, 1.0, 0.0, 0.0, 0.0072, 4.0),
        (20.0, 2.0, 0.0, 1.0, 0.0026, 4.0),
        (20.0, 3.0, 1.0, 1.0, 0.0023, 5.0),
        (100.0, 1.0, 0.0, 0.0, 0.0042, 8.0),
        (100.0, 2.0, 0.0, 1.0, 0.0042, 8.0),
        (100.0, 3.0, 1.0, 1.0, 0.0052, 10.0),
        (300.0, 1.0, 0.0, 0.0, 0.0107, 14.0),
        (300.0, 2.0, 0.0, 1.0, 0.0138, 14.0),
        (300.0, 3.0, 1.0, 1.0, 0.0152, 17.0),
        (1000.0, 1.0, 0.0, 0.0, 0.0389, 26.0),
        (1000.0, 2.0, 0.0, 1.0, 0.0304, 26.0),
        (1000.0, 3.0, 1.0, 1.0, 0.0394, 32.0),
        (3000.0, 1.0, 0.0, 0.0, 0.0987, 46.0),
        (3000.0, 2.0, 0.0, 1.0, 0.0959, 44.0),
        (3000.0, 3.0, 1.0, 1.0, 0.1176, 54.0),
        (10000.0, 1.0, 0.0, 0.0, 0.5385, 83.0),
        (10000.0, 2.0, 0.0, 1.0, 0.4362, 83.0),
        (10000.0, 3.0, 1.0, 1.0, 0.4783, 103.0),
        (30000.0, 1.0, 0.0, 0.0, 1.6128, 140.0),
        (30000.0, 2.0, 0.0, 1.0, 1.6174, 149.0),
        (30000.0, 3.0, 1.0, 1.0, 1.7384, 180.0),
        (100000.0, 1.0, 0.0, 0.0, 5.4589, 266.0),
        (100000.0, 2.0, 0.0, 1.0, 5.4714, 268.0),
        (100000.0, 3.0, 1.0, 1.0, 6.3304, 320.0),
    )
)


def leiden_reference_distance(
    features: dict[str, float],
    reference: dict[str, float],
) -> float:
    """Compute a weighted distance to a Leiden benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 3.4
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 0.9
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 1.4
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.2
    )


def estimate_leiden_runtime_and_communities(
    graph: nx.DiGraph,
) -> dict[str, object]:
    """Estimate Leiden runtime and community count from project benchmarks."""
    features = build_graph_structure_features(graph)
    return finalize_estimate(
        features,
        LEIDEN_ESTIMATION_REFERENCE_POINTS,
        leiden_reference_distance,
    )
