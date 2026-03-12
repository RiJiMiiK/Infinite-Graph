"""GA benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

from .community_estimation import (
    build_graph_structure_features,
    build_reference_points,
    finalize_estimate,
)


GA_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = build_reference_points(
    (
        (100.0, 1.97, 0.0, 0.0, 50.0, 30.0, 1.5, 4.7729, 23.0),
        (100.0, 1.97, 0.0, 0.0, 300.0, 30.0, 1.5, 23.0318, 22.0),
        (100.0, 1.97, 0.0, 0.0, 300.0, 60.0, 1.5, 35.7234, 20.0),
        (100.0, 1.97, 0.0, 0.0, 300.0, 30.0, 0.5, 35.5097, 16.0),
        (100.0, 2.0, 0.0, 1.0, 50.0, 30.0, 1.5, 3.3137, 20.0),
        (100.0, 2.0, 0.0, 1.0, 300.0, 30.0, 1.5, 24.5120, 21.0),
        (100.0, 2.0, 0.0, 1.0, 300.0, 60.0, 1.5, 32.0927, 20.0),
        (100.0, 2.0, 0.0, 1.0, 300.0, 30.0, 0.5, 24.1274, 15.0),
        (100.0, 3.0, 1.0, 1.0, 50.0, 30.0, 1.5, 3.2431, 39.0),
        (100.0, 3.0, 1.0, 1.0, 300.0, 30.0, 1.5, 24.0966, 34.0),
        (100.0, 3.0, 1.0, 1.0, 300.0, 60.0, 1.5, 27.4330, 28.0),
        (100.0, 3.0, 1.0, 1.0, 300.0, 30.0, 3.0, 19.7357, 42.0),
        (500.0, 1.994, 0.0, 0.0, 300.0, 30.0, 1.5, 816.0056, 94.0),
        (500.0, 2.0, 0.0, 1.0, 300.0, 30.0, 1.5, 812.8634, 89.0),
        (500.0, 3.0, 1.0, 1.0, 300.0, 30.0, 1.5, 691.7880, 142.0),
    ),
    ("population", "generation", "r_value"),
)


def build_ga_estimation_features(
    graph: nx.DiGraph,
    parameters: Mapping[str, object],
) -> dict[str, float]:
    """Build normalized features for GA estimation."""
    return {
        **build_graph_structure_features(graph),
        "population": float(parameters.get("population", 300)),
        "generation": float(parameters.get("generation", 30)),
        "r_value": float(parameters.get("r", 1.5)),
    }


def ga_reference_distance(
    features: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    """Compute a weighted distance between current features and a GA benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 4.2
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 1.2
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 1.7
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.4
        + abs(
            math.log(
                max(features["population"], 1.0) / max(reference["population"], 1.0)
            )
        )
        * 1.8
        + abs(
            math.log(
                max(features["generation"], 1.0) / max(reference["generation"], 1.0)
            )
        )
        * 1.4
        + abs(
            math.log(max(features["r_value"], 1e-9) / max(reference["r_value"], 1e-9))
        )
        * 0.8
    )


def estimate_ga_runtime_and_communities(
    graph: nx.DiGraph,
    **parameters: object,
) -> dict[str, object]:
    """Estimate GA runtime and community count from project benchmark data."""
    features = build_ga_estimation_features(graph, parameters)
    return finalize_estimate(
        features,
        GA_ESTIMATION_REFERENCE_POINTS,
        ga_reference_distance,
    )
