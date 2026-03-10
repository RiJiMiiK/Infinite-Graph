"""Helpers for mono-community analysis based on CDlib."""

from __future__ import annotations

from collections.abc import Mapping

import networkx as nx
from cdlib import algorithms

MONO_COMMUNITY_ALGORITHMS: dict[str, dict[str, object]] = {
    "infomap": {
        "label": "Infomap",
        "weight_parameter": "flags",
        "weight_value": "--directed --silent -w",
        "supports_directed": True,
    },
    "rb_pots": {
        "label": "RB Pots",
        "weight_parameter": "weights",
        "weight_value": "weight",
        "supports_directed": True,
    },
    "rber_pots": {
        "label": "RBER Pots",
        "weight_parameter": "weights",
        "weight_value": "weight",
        "supports_directed": True,
    },
    "threshold_clustering": {
        "label": "Threshold Clustering",
        "weight_parameter": None,
        "weight_value": None,
        "supports_directed": True,
    },
}


def uses_directed_community_graph() -> bool:
    return True


def uses_edge_weights_only() -> bool:
    return True


def build_cdlib_graph(
    graph_nodes: list[dict[str, object]],
    graph_edges: list[dict[str, object]],
) -> nx.DiGraph:
    if not uses_directed_community_graph():
        raise ValueError("Community analysis must keep the graph directed.")
    graph = nx.DiGraph()
    for node in graph_nodes:
        node_id = str(node["id"])
        graph.add_node(
            node_id,
            label=str(node.get("label", node_id)),
        )

    for edge in graph_edges:
        source = str(edge["source"])
        target = str(edge["target"])
        graph.add_edge(
            source,
            target,
            weight=float(edge.get("weight", 1.0)),
            elements=list(edge.get("elements", [])),
        )

    return graph


def get_mono_community_algorithms() -> list[dict[str, object]]:
    return [
        {
            "key": key,
            "label": metadata["label"],
            "supports_directed": metadata["supports_directed"],
        }
        for key, metadata in MONO_COMMUNITY_ALGORITHMS.items()
    ]


def get_default_mono_community_algorithm() -> str:
    return "infomap"


def run_mono_community_algorithm(
    graph: nx.DiGraph,
    algorithm_name: str,
    **kwargs: object,
):
    if algorithm_name not in MONO_COMMUNITY_ALGORITHMS:
        available = ", ".join(sorted(MONO_COMMUNITY_ALGORITHMS))
        raise ValueError(
            f"Unsupported mono-community algorithm: {algorithm_name}. "
            f"Available: {available}"
        )

    metadata = MONO_COMMUNITY_ALGORITHMS[algorithm_name]
    algorithm = getattr(algorithms, algorithm_name)
    call_kwargs = dict(kwargs)
    weight_parameter = metadata["weight_parameter"]
    if weight_parameter is not None and weight_parameter not in call_kwargs:
        call_kwargs[weight_parameter] = metadata["weight_value"]
    return algorithm(graph, **call_kwargs)


def summarize_mono_community_result(result) -> dict[str, object]:
    communities = [sorted(str(node) for node in community) for community in result.communities]
    sizes = [len(community) for community in communities]
    node_to_community: dict[str, int] = {}
    for community_index, community in enumerate(communities):
        for node in community:
            node_to_community[node] = community_index

    return {
        "communities": communities,
        "community_count": len(communities),
        "community_sizes": sizes,
        "min_size": min(sizes) if sizes else 0,
        "max_size": max(sizes) if sizes else 0,
        "average_size": (sum(sizes) / len(sizes)) if sizes else 0.0,
        "node_to_community": node_to_community,
        "method_name": getattr(result, "method_name", "unknown"),
        "parameters": _normalize_parameters(getattr(result, "method_parameters", {})),
    }


def _normalize_parameters(parameters: Mapping[str, object] | object) -> dict[str, object]:
    if isinstance(parameters, Mapping):
        return {str(key): value for key, value in parameters.items()}
    return {}
