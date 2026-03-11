"""Belief benchmark-based estimation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx

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


def count_reciprocal_pairs(graph: nx.DiGraph) -> int:
    reciprocal_pairs = 0
    seen: set[tuple[object, object]] = set()
    for source, target in graph.edges():
        if source == target:
            continue
        pair = tuple(sorted((source, target), key=str))
        if pair in seen:
            continue
        if graph.has_edge(target, source):
            reciprocal_pairs += 1
            seen.add(pair)
    return reciprocal_pairs


def build_belief_estimation_features(
    graph: nx.DiGraph,
    parameters: Mapping[str, object],
) -> dict[str, float]:
    node_count = max(1, graph.number_of_nodes())
    edge_count = graph.number_of_edges()
    self_loops = nx.number_of_selfloops(graph)
    reciprocal_pairs = count_reciprocal_pairs(graph)
    return {
        "nodes": float(node_count),
        "edges_per_node": float(edge_count) / float(node_count),
        "self_loop_ratio": float(self_loops) / float(node_count),
        "reciprocal_ratio": float(reciprocal_pairs) / float(node_count),
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
    weighted_runtime_logs = 0.0
    weighted_communities = 0.0
    weighted_nodes = 0.0
    total_weight = 0.0
    for reference in BELIEF_ESTIMATION_REFERENCE_POINTS:
        distance = belief_reference_distance(features, reference)
        weight = 1.0 / (0.05 + distance)
        total_weight += weight
        weighted_runtime_logs += math.log(reference["elapsed"]) * weight
        weighted_communities += reference["communities"] * weight
        weighted_nodes += reference["nodes"] * weight
    estimated_runtime = math.exp(weighted_runtime_logs / total_weight)
    estimated_communities = max(1, int(round(weighted_communities / total_weight)))
    effective_reference_nodes = weighted_nodes / total_weight
    confidence_ratio = min(features["nodes"], effective_reference_nodes) / max(
        features["nodes"], effective_reference_nodes
    )
    confidence = (
        "high" if confidence_ratio >= 0.75 else "medium" if confidence_ratio >= 0.4 else "low"
    )
    return {
        "estimated_runtime_seconds": estimated_runtime,
        "estimated_community_count": estimated_communities,
        "confidence": confidence,
        "features": features,
    }


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, remainder = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {remainder:04.1f}s"
    hours, remainder_minutes = divmod(minutes, 60)
    return f"{int(hours)}h {int(remainder_minutes)}m {remainder:04.1f}s"
