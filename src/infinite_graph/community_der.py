"""DER benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

from .community_estimation import (
    build_graph_structure_features,
    build_reference_points,
    finalize_estimate,
)

DER_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = build_reference_points(
    (
        (1000.0, 1.099, 0.0, 0.0, 1.0, 1e-09, 1.0, 0.0112, 2.0),
        (1000.0, 1.099, 0.0, 0.0, 20.0, 0.001, 100.0, 0.0789, 2.0),
        (1000.0, 2.098, 0.0, 1.099, 1.0, 1e-07, 50.0, 0.0114, 2.0),
        (1000.0, 2.098, 0.0, 1.099, 20.0, 1e-07, 10.0, 0.0640, 2.0),
        (1000.0, 3.098, 1.0, 1.099, 1.0, 0.001, 250.0, 0.0123, 2.0),
        (1000.0, 3.098, 1.0, 1.099, 20.0, 0.001, 100.0, 0.1093, 2.0),
        (10000.0, 1.0999, 0.0, 0.0, 1.0, 1e-05, 1.0, 0.1021, 2.0),
        (10000.0, 1.0999, 0.0, 0.0, 100.0, 0.1, 100.0, 4.3012, 2.0),
        (10000.0, 2.0998, 0.0, 1.0999, 1.0, 1e-09, 1.0, 0.1202, 2.0),
        (10000.0, 2.0998, 0.0, 1.0999, 100.0, 1e-09, 1000.0, 4.7252, 2.0),
        (10000.0, 3.0998, 1.0, 1.0999, 1.0, 0.5, 1.0, 0.1400, 2.0),
        (10000.0, 3.0998, 1.0, 1.0999, 100.0, 0.5, 1000.0, 6.0624, 2.0),
    ),
    ("walk_len", "threshold", "iter_bound"),
)


def build_der_estimation_features(
    graph: nx.DiGraph,
    parameters: Mapping[str, object],
) -> dict[str, float]:
    """Build normalized features for DER estimation."""
    return {
        **build_graph_structure_features(graph),
        "walk_len": float(parameters.get("walk_len", 3)),
        "threshold": float(parameters.get("threshold", 0.00001)),
        "iter_bound": float(parameters.get("iter_bound", 50)),
    }


def der_reference_distance(
    features: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    """Compute a weighted distance between current features and a DER benchmark point."""
    eps_floor = 1e-12
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 3.5
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 1.0
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 1.6
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.2
        + abs(math.log(max(features["walk_len"], 1.0) / max(reference["walk_len"], 1.0))) * 1.4
        + abs(
            math.log(
                max(features["threshold"], eps_floor)
                / max(reference["threshold"], eps_floor)
            )
        )
        * 0.9
        + abs(
            math.log(
                max(features["iter_bound"], 1.0)
                / max(reference["iter_bound"], 1.0)
            )
        )
        * 1.1
    )


def estimate_der_runtime_and_communities(
    graph: nx.DiGraph,
    **parameters: object,
) -> dict[str, object]:
    """Estimate DER runtime and community count from project benchmark data."""
    features = build_der_estimation_features(graph, parameters)
    return finalize_estimate(
        features,
        DER_ESTIMATION_REFERENCE_POINTS,
        der_reference_distance,
    )
