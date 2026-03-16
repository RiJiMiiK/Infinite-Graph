"""Label Propagation benchmark-based estimation helpers."""

from __future__ import annotations

import math

import networkx as nx

from .estimation import build_graph_structure_features, build_reference_points, finalize_estimate


LABEL_PROPAGATION_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = (
    build_reference_points(
        (
            (20.0, 2.65, 0.0, 0.0, 0.0027, 1.0),
            (20.0, 3.0, 0.0, 1.5, 0.0012, 2.0),
            (20.0, 4.0, 1.0, 1.5, 0.0009, 20.0),
            (100.0, 2.92, 0.0, 0.0, 0.0220, 1.0),
            (100.0, 3.0, 0.0, 1.5, 0.0161, 2.0),
            (100.0, 4.0, 1.0, 1.5, 0.0061, 100.0),
            (300.0, 2.9766666667, 0.0, 0.0, 0.1757, 1.0),
            (300.0, 3.0, 0.0, 1.5, 0.0752, 1.0),
            (300.0, 4.0, 1.0, 1.5, 0.0219, 300.0),
            (1000.0, 2.992, 0.0, 0.0, 1.7476, 1.0),
            (1000.0, 3.0, 0.0, 1.5, 0.8709, 2.0),
            (1000.0, 4.0, 1.0, 1.5, 0.0501, 1000.0),
            (3000.0, 2.9973333333, 0.0, 0.0, 15.9048, 1.0),
            (3000.0, 3.0, 0.0, 1.5, 8.0270, 1.0),
            (3000.0, 4.0, 1.0, 1.5, 0.1859, 3000.0),
            (10000.0, 2.9992, 0.0, 0.0, 151.2859, 1.0),
            (10000.0, 3.0, 0.0, 1.5, 82.0005, 2.0),
            (10000.0, 4.0, 1.0, 1.5, 0.5202, 10000.0),
        )
    )
)


def label_propagation_reference_distance(
    features: dict[str, float],
    reference: dict[str, float],
) -> float:
    """Compute a weighted distance to a Label Propagation benchmark point."""
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 4.2
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 1.0
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 2.4
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 1.6
    )


def estimate_label_propagation_runtime_and_communities(
    graph: nx.DiGraph,
) -> dict[str, object]:
    """Estimate Label Propagation runtime and community count from project benchmarks."""
    features = build_graph_structure_features(graph)
    estimate = finalize_estimate(
        features,
        LABEL_PROPAGATION_ESTIMATION_REFERENCE_POINTS,
        label_propagation_reference_distance,
    )
    if features["self_loop_ratio"] >= 0.5:
        estimate["collapse_risk"] = "singleton"
    elif features["self_loop_ratio"] > 0.0:
        estimate["collapse_risk"] = "mixed"
    elif features["reciprocal_ratio"] >= 1.0:
        estimate["collapse_risk"] = "split_or_single"
    else:
        estimate["collapse_risk"] = "single"
    if features["nodes"] >= 3000 and features["self_loop_ratio"] == 0.0:
        estimate["confidence"] = "medium"
    return estimate
