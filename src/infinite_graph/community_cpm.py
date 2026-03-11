"""CPM benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

from .community_estimation import build_graph_structure_features, finalize_estimate

CPM_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = (
    {
        "nodes": 100.0,
        "edges_per_node": 3.45,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 1.0,
        "resolution_parameter": 0.001,
        "elapsed": 0.006,
        "communities": 1.0,
    },
    {
        "nodes": 100.0,
        "edges_per_node": 3.45,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 1.0,
        "resolution_parameter": 0.01,
        "elapsed": 0.006,
        "communities": 1.0,
    },
    {
        "nodes": 100.0,
        "edges_per_node": 3.45,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 1.0,
        "resolution_parameter": 0.05,
        "elapsed": 0.007,
        "communities": 35.0,
    },
    {
        "nodes": 100.0,
        "edges_per_node": 3.45,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 1.0,
        "resolution_parameter": 0.1,
        "elapsed": 0.007,
        "communities": 44.0,
    },
    {
        "nodes": 100.0,
        "edges_per_node": 3.45,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 1.0,
        "resolution_parameter": 0.5,
        "elapsed": 0.012,
        "communities": 62.0,
    },
    {
        "nodes": 100.0,
        "edges_per_node": 3.45,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 1.0,
        "resolution_parameter": 1.0,
        "elapsed": 0.018,
        "communities": 73.0,
    },
    {
        "nodes": 100.0,
        "edges_per_node": 3.45,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 1.0,
        "resolution_parameter": 2.0,
        "elapsed": 0.019,
        "communities": 81.0,
    },
    {
        "nodes": 300.0,
        "edges_per_node": 8.2333333333,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 3.5166666667,
        "resolution_parameter": 0.001,
        "elapsed": 0.034,
        "communities": 1.0,
    },
    {
        "nodes": 300.0,
        "edges_per_node": 8.2333333333,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 3.5166666667,
        "resolution_parameter": 0.01,
        "elapsed": 0.035,
        "communities": 49.0,
    },
    {
        "nodes": 300.0,
        "edges_per_node": 8.2333333333,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 3.5166666667,
        "resolution_parameter": 0.05,
        "elapsed": 0.036,
        "communities": 118.0,
    },
    {
        "nodes": 300.0,
        "edges_per_node": 8.2333333333,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 3.5166666667,
        "resolution_parameter": 0.1,
        "elapsed": 0.037,
        "communities": 130.0,
    },
    {
        "nodes": 300.0,
        "edges_per_node": 8.2333333333,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 3.5166666667,
        "resolution_parameter": 0.5,
        "elapsed": 0.041,
        "communities": 170.0,
    },
    {
        "nodes": 300.0,
        "edges_per_node": 8.2333333333,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 3.5166666667,
        "resolution_parameter": 1.0,
        "elapsed": 0.042,
        "communities": 196.0,
    },
    {
        "nodes": 300.0,
        "edges_per_node": 8.2333333333,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 3.5166666667,
        "resolution_parameter": 2.0,
        "elapsed": 0.043,
        "communities": 224.0,
    },
    {
        "nodes": 1000.0,
        "edges_per_node": 19.636,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 9.302,
        "resolution_parameter": 0.001,
        "elapsed": 0.297,
        "communities": 1.0,
    },
    {
        "nodes": 1000.0,
        "edges_per_node": 19.636,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 9.302,
        "resolution_parameter": 0.01,
        "elapsed": 5.3,
        "communities": 263.0,
    },
    {
        "nodes": 1000.0,
        "edges_per_node": 19.636,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 9.302,
        "resolution_parameter": 0.05,
        "elapsed": 0.304,
        "communities": 337.0,
    },
    {
        "nodes": 1000.0,
        "edges_per_node": 19.636,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 9.302,
        "resolution_parameter": 0.1,
        "elapsed": 0.305,
        "communities": 341.0,
    },
    {
        "nodes": 1000.0,
        "edges_per_node": 19.636,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 9.302,
        "resolution_parameter": 0.5,
        "elapsed": 0.312,
        "communities": 465.0,
    },
    {
        "nodes": 1000.0,
        "edges_per_node": 19.636,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 9.302,
        "resolution_parameter": 1.0,
        "elapsed": 0.324,
        "communities": 546.0,
    },
    {
        "nodes": 1000.0,
        "edges_per_node": 19.636,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 9.302,
        "resolution_parameter": 2.0,
        "elapsed": 0.338,
        "communities": 636.0,
    },
    {
        "nodes": 10195.0,
        "edges_per_node": 9.9873467386,
        "self_loop_ratio": 0.6038254046,
        "reciprocal_ratio": 0.0094163806,
        "resolution_parameter": 0.001,
        "elapsed": 7.43,
        "communities": 1545.0,
    },
    {
        "nodes": 10195.0,
        "edges_per_node": 9.9873467386,
        "self_loop_ratio": 0.6038254046,
        "reciprocal_ratio": 0.0094163806,
        "resolution_parameter": 0.01,
        "elapsed": 7.6,
        "communities": 1142.0,
    },
    {
        "nodes": 10195.0,
        "edges_per_node": 9.9873467386,
        "self_loop_ratio": 0.6038254046,
        "reciprocal_ratio": 0.0094163806,
        "resolution_parameter": 0.05,
        "elapsed": 7.8,
        "communities": 1661.0,
    },
    {
        "nodes": 10195.0,
        "edges_per_node": 9.9873467386,
        "self_loop_ratio": 0.6038254046,
        "reciprocal_ratio": 0.0094163806,
        "resolution_parameter": 0.1,
        "elapsed": 8.0,
        "communities": 2194.0,
    },
    {
        "nodes": 10195.0,
        "edges_per_node": 9.9873467386,
        "self_loop_ratio": 0.6038254046,
        "reciprocal_ratio": 0.0094163806,
        "resolution_parameter": 0.5,
        "elapsed": 9.3,
        "communities": 5027.0,
    },
    {
        "nodes": 10195.0,
        "edges_per_node": 9.9873467386,
        "self_loop_ratio": 0.6038254046,
        "reciprocal_ratio": 0.0094163806,
        "resolution_parameter": 1.0,
        "elapsed": 12.1,
        "communities": 7630.0,
    },
    {
        "nodes": 10195.0,
        "edges_per_node": 9.9873467386,
        "self_loop_ratio": 0.6038254046,
        "reciprocal_ratio": 0.0094163806,
        "resolution_parameter": 2.0,
        "elapsed": 11.3,
        "communities": 8708.0,
    },
)


def build_cpm_estimation_features(
    graph: nx.DiGraph,
    parameters: Mapping[str, object],
) -> dict[str, float]:
    """Build normalized features for CPM estimation."""
    return {
        **build_graph_structure_features(graph),
        "resolution_parameter": float(parameters.get("resolution_parameter", 1.0)),
    }


def cpm_reference_distance(
    features: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    """Compute a weighted distance between current features and a benchmark point."""
    eps_floor = 1e-12
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 3.4
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 0.3
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 4.0
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 0.4
        + abs(
            math.log(
                max(features["resolution_parameter"], eps_floor)
                / max(reference["resolution_parameter"], eps_floor)
            )
        )
        * 3.2
    )


def estimate_cpm_runtime_and_communities(
    graph: nx.DiGraph,
    **parameters: object,
) -> dict[str, object]:
    """Estimate CPM runtime and community count from project benchmark data."""
    features = build_cpm_estimation_features(graph, parameters)
    return finalize_estimate(
        features,
        CPM_ESTIMATION_REFERENCE_POINTS,
        cpm_reference_distance,
    )
