"""Shared helpers for benchmark-based community estimations."""

from __future__ import annotations

import math
from collections.abc import Mapping

import networkx as nx


def count_reciprocal_pairs(graph: nx.DiGraph) -> int:
    """Count reciprocal edge pairs in a directed graph."""
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


def finalize_estimate(
    features: Mapping[str, float],
    references: tuple[dict[str, float], ...],
    distance_function,
) -> dict[str, object]:
    """Compute a weighted estimate from benchmark reference points."""
    weighted_runtime_logs = 0.0
    weighted_communities = 0.0
    weighted_nodes = 0.0
    total_weight = 0.0
    for reference in references:
        distance = distance_function(features, reference)
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
        "features": dict(features),
    }


def build_graph_structure_features(graph: nx.DiGraph) -> dict[str, float]:
    """Build the shared structural feature set used by community estimators."""
    node_count = max(1, graph.number_of_nodes())
    edge_count = graph.number_of_edges()
    self_loops = nx.number_of_selfloops(graph)
    reciprocal_pairs = count_reciprocal_pairs(graph)
    return {
        "nodes": float(node_count),
        "edges_per_node": float(edge_count) / float(node_count),
        "self_loop_ratio": float(self_loops) / float(node_count),
        "reciprocal_ratio": float(reciprocal_pairs) / float(node_count),
    }


def build_reference_points(
    rows: tuple[tuple[float, ...], ...],
    extra_keys: tuple[str, ...] = (),
) -> tuple[dict[str, float], ...]:
    """Build benchmark reference points with shared graph-structure keys."""
    keys = (
        "nodes",
        "edges_per_node",
        "self_loop_ratio",
        "reciprocal_ratio",
        *extra_keys,
        "elapsed",
        "communities",
    )
    return tuple(dict(zip(keys, row, strict=True)) for row in rows)
