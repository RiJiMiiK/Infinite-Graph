"""Belief benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

from .community_estimation import build_graph_structure_features, finalize_estimate

BELIEF_ESTIMATION_REFERENCE_POINTS: tuple[dict[str, float], ...] = (
    {
        "nodes": 20.0,
        "edges_per_node": 2.15,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 0.0,
        "max_it": 100.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.005,
        "q_max": 7.0,
        "elapsed": 8.3624,
        "communities": 1.0,
    },
    {
        "nodes": 20.0,
        "edges_per_node": 3.5,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 1.0,
        "max_it": 100.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.005,
        "q_max": 7.0,
        "elapsed": 5.0440,
        "communities": 2.0,
    },
    {
        "nodes": 20.0,
        "edges_per_node": 4.5,
        "self_loop_ratio": 1.0,
        "reciprocal_ratio": 1.0,
        "max_it": 100.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.005,
        "q_max": 7.0,
        "elapsed": 4.8679,
        "communities": 1.0,
    },
    {
        "nodes": 50.0,
        "edges_per_node": 3.6,
        "self_loop_ratio": 1.0,
        "reciprocal_ratio": 1.0,
        "max_it": 100.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 1.0,
        "threshold": 0.01,
        "q_max": 12.0,
        "elapsed": 1.8566,
        "communities": 2.0,
    },
    {
        "nodes": 100.0,
        "edges_per_node": 2.03,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 0.0,
        "max_it": 100.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.005,
        "q_max": 7.0,
        "elapsed": 14.8712,
        "communities": 1.0,
    },
    {
        "nodes": 100.0,
        "edges_per_node": 2.3,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 1.0,
        "max_it": 100.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.005,
        "q_max": 7.0,
        "elapsed": 14.9517,
        "communities": 1.0,
    },
    {
        "nodes": 100.0,
        "edges_per_node": 3.3,
        "self_loop_ratio": 1.0,
        "reciprocal_ratio": 1.0,
        "max_it": 100.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.005,
        "q_max": 7.0,
        "elapsed": 8.9261,
        "communities": 1.0,
    },
    {
        "nodes": 100.0,
        "edges_per_node": 3.3,
        "self_loop_ratio": 1.0,
        "reciprocal_ratio": 1.0,
        "max_it": 25.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.001,
        "q_max": 12.0,
        "elapsed": 7.4055,
        "communities": 4.0,
    },
    {
        "nodes": 100.0,
        "edges_per_node": 3.3,
        "self_loop_ratio": 1.0,
        "reciprocal_ratio": 1.0,
        "max_it": 25.0,
        "eps": 0.001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.001,
        "q_max": 12.0,
        "elapsed": 5.1602,
        "communities": 2.0,
    },
    {
        "nodes": 100.0,
        "edges_per_node": 3.3,
        "self_loop_ratio": 1.0,
        "reciprocal_ratio": 1.0,
        "max_it": 100.0,
        "eps": 0.001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.01,
        "q_max": 12.0,
        "elapsed": 10.7695,
        "communities": 2.0,
    },
    {
        "nodes": 300.0,
        "edges_per_node": 2.01,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 0.0,
        "max_it": 100.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.005,
        "q_max": 7.0,
        "elapsed": 39.4924,
        "communities": 1.0,
    },
    {
        "nodes": 300.0,
        "edges_per_node": 2.1,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 1.0,
        "max_it": 100.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.005,
        "q_max": 7.0,
        "elapsed": 41.9252,
        "communities": 1.0,
    },
    {
        "nodes": 300.0,
        "edges_per_node": 3.1,
        "self_loop_ratio": 1.0,
        "reciprocal_ratio": 1.0,
        "max_it": 100.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.005,
        "q_max": 7.0,
        "elapsed": 24.9422,
        "communities": 1.0,
    },
    {
        "nodes": 300.0,
        "edges_per_node": 3.1,
        "self_loop_ratio": 1.0,
        "reciprocal_ratio": 1.0,
        "max_it": 25.0,
        "eps": 0.001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.001,
        "q_max": 12.0,
        "elapsed": 22.5480,
        "communities": 5.0,
    },
    {
        "nodes": 300.0,
        "edges_per_node": 3.1,
        "self_loop_ratio": 1.0,
        "reciprocal_ratio": 1.0,
        "max_it": 100.0,
        "eps": 0.001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.01,
        "q_max": 12.0,
        "elapsed": 45.4664,
        "communities": 2.0,
    },
    {
        "nodes": 1000.0,
        "edges_per_node": 2.003,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 0.0,
        "max_it": 100.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.005,
        "q_max": 7.0,
        "elapsed": 362.7779,
        "communities": 1.0,
    },
    {
        "nodes": 1000.0,
        "edges_per_node": 2.03,
        "self_loop_ratio": 0.0,
        "reciprocal_ratio": 1.0,
        "max_it": 100.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.005,
        "q_max": 7.0,
        "elapsed": 556.2323,
        "communities": 1.0,
    },
    {
        "nodes": 1000.0,
        "edges_per_node": 3.03,
        "self_loop_ratio": 1.0,
        "reciprocal_ratio": 1.0,
        "max_it": 100.0,
        "eps": 0.0001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.005,
        "q_max": 7.0,
        "elapsed": 283.8963,
        "communities": 1.0,
    },
    {
        "nodes": 1000.0,
        "edges_per_node": 3.03,
        "self_loop_ratio": 1.0,
        "reciprocal_ratio": 1.0,
        "max_it": 25.0,
        "eps": 0.001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.001,
        "q_max": 12.0,
        "elapsed": 132.0003,
        "communities": 1.0,
    },
    {
        "nodes": 1000.0,
        "edges_per_node": 3.03,
        "self_loop_ratio": 1.0,
        "reciprocal_ratio": 1.0,
        "max_it": 100.0,
        "eps": 0.001,
        "reruns_if_not_conv": 5.0,
        "threshold": 0.01,
        "q_max": 12.0,
        "elapsed": 372.8350,
        "communities": 1.0,
    },
)
def build_belief_estimation_features(
    graph: nx.DiGraph,
    parameters: Mapping[str, object],
) -> dict[str, float]:
    return {
        **build_graph_structure_features(graph),
        "max_it": float(parameters.get("max_it", 100)),
        "eps": float(parameters.get("eps", 0.0001)),
        "reruns_if_not_conv": float(parameters.get("reruns_if_not_conv", 5)),
        "threshold": float(parameters.get("threshold", 0.005)),
        "q_max": float(parameters.get("q_max", 7)),
    }


def belief_reference_distance(
    features: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    eps_floor = 1e-12
    return (
        abs(math.log((features["nodes"] + 1.0) / (reference["nodes"] + 1.0))) * 3.0
        + abs(features["edges_per_node"] - reference["edges_per_node"]) * 2.5
        + abs(features["self_loop_ratio"] - reference["self_loop_ratio"]) * 3.0
        + abs(features["reciprocal_ratio"] - reference["reciprocal_ratio"]) * 2.5
        + abs(math.log((features["max_it"] + 1.0) / (reference["max_it"] + 1.0))) * 1.3
        + abs(features["reruns_if_not_conv"] - reference["reruns_if_not_conv"]) * 0.9
        + abs(
            math.log(max(features["threshold"], eps_floor) / max(reference["threshold"], eps_floor))
        )
        * 1.2
        + abs(math.log(max(features["eps"], eps_floor) / max(reference["eps"], eps_floor))) * 0.8
        + abs(features["q_max"] - reference["q_max"]) / 12.0
    )


def estimate_belief_runtime_and_communities(
    graph: nx.DiGraph,
    **parameters: object,
) -> dict[str, object]:
    features = build_belief_estimation_features(graph, parameters)
    return finalize_estimate(
        features,
        BELIEF_ESTIMATION_REFERENCE_POINTS,
        belief_reference_distance,
    )


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, remainder = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {remainder:04.1f}s"
    hours, remainder_minutes = divmod(minutes, 60)
    return f"{int(hours)}h {int(remainder_minutes)}m {remainder:04.1f}s"
