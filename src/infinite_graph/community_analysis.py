"""Helpers for mono-community analysis based on CDlib."""

from __future__ import annotations

from collections.abc import Mapping

import networkx as nx
from cdlib import algorithms

MONO_COMMUNITY_ALGORITHM_EVALUATION: dict[str, dict[str, object]] = {
    "agdl": {
        "label": "AGDL",
        "supports_directed": True,
        "supports_weighted": True,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Uses the directed weighted graph as-is.",
    },
    "async_fluid": {
        "label": "Async Fluid",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "bayan": {
        "label": "Bayan",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "belief": {
        "label": "Belief",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "cpm": {
        "label": "CPM",
        "supports_directed": False,
        "supports_weighted": True,
        "weight_parameter": "weights",
        "weight_value": "weight",
        "compatibility_note": "Will run on an undirected weighted view of the graph.",
    },
    "der": {
        "label": "DER",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "eigenvector": {
        "label": "Eigenvector",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "em": {
        "label": "EM",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "ga": {
        "label": "GA",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "gdmp2": {
        "label": "GDMP2",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "girvan_newman": {
        "label": "Girvan-Newman",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "greedy_modularity": {
        "label": "Greedy Modularity",
        "supports_directed": False,
        "supports_weighted": True,
        "weight_parameter": "weight",
        "weight_value": "weight",
        "compatibility_note": "Will run on an undirected weighted view of the graph.",
    },
    "head_tail": {
        "label": "Head/Tail",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "infomap": {
        "label": "Infomap",
        "supports_directed": True,
        "supports_weighted": True,
        "weight_parameter": "flags",
        "weight_value": "--directed --silent -w",
        "compatibility_note": "Uses the directed weighted graph as-is.",
    },
    "kcut": {
        "label": "Kcut",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "label_propagation_raghavan": {
        "label": "Label Propagation Raghavan",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "label_propagation_cordasco_gargano": {
        "label": "Label Propagation Cordasco-Gargano",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "leiden": {
        "label": "Leiden",
        "supports_directed": False,
        "supports_weighted": True,
        "weight_parameter": "weights",
        "weight_value": "weight",
        "compatibility_note": "Will run on an undirected weighted view of the graph.",
    },
    "louvain": {
        "label": "Louvain",
        "supports_directed": False,
        "supports_weighted": True,
        "weight_parameter": "weight",
        "weight_value": "weight",
        "compatibility_note": "Will run on an undirected weighted view of the graph.",
    },
    "lswl": {
        "label": "LSWL",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "lswl_plus": {
        "label": "LSWL Plus",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "markov_clustering": {
        "label": "Markov Clustering",
        "supports_directed": False,
        "supports_weighted": True,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected weighted view of the graph.",
    },
    "mcode": {
        "label": "MCODE",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "mod_m": {
        "label": "Mod M",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "mod_r": {
        "label": "Mod R",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "paris": {
        "label": "Paris",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "pycombo": {
        "label": "PyCombo",
        "supports_directed": False,
        "supports_weighted": True,
        "weight_parameter": "weight",
        "weight_value": "weight",
        "compatibility_note": "Will run on an undirected weighted view of the graph.",
    },
    "rber_pots": {
        "label": "RBER Pots",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "rb_pots": {
        "label": "RB Pots",
        "supports_directed": True,
        "supports_weighted": True,
        "weight_parameter": "weights",
        "weight_value": "weight",
        "compatibility_note": "Uses the directed weighted graph as-is.",
    },
    "ricci_community": {
        "label": "Ricci Community",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "r_spectral_clustering": {
        "label": "R Spectral Clustering",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "scan": {
        "label": "SCAN",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "significance_communities": {
        "label": "Significance Communities",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "spinglass": {
        "label": "Spinglass",
        "supports_directed": False,
        "supports_weighted": True,
        "weight_parameter": "weights",
        "weight_value": "weight",
        "compatibility_note": "Will run on an undirected weighted view of the graph.",
    },
    "surprise_communities": {
        "label": "Surprise Communities",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "sbm_dl": {
        "label": "SBM DL",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "sbm_dl_nested": {
        "label": "SBM DL Nested",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "spectral": {
        "label": "Spectral",
        "supports_directed": False,
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "threshold_clustering": {
        "label": "Threshold Clustering",
        "supports_directed": True,
        "supports_weighted": True,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Uses the directed weighted graph as-is.",
    },
    "walktrap": {
        "label": "Walktrap",
        "supports_directed": False,
        "supports_weighted": True,
        "weight_parameter": "weights",
        "weight_value": "weight",
        "compatibility_note": "Will run on an undirected weighted view of the graph.",
    },
}


def uses_directed_community_graph() -> bool:
    return True


def uses_edge_weights_only() -> bool:
    return True


def ignores_node_weights() -> bool:
    return True


def build_cdlib_graph(
    graph_nodes: list[dict[str, object]],
    graph_edges: list[dict[str, object]],
) -> nx.DiGraph:
    if not uses_directed_community_graph():
        raise ValueError("Community analysis must keep the graph directed.")
    if not ignores_node_weights():
        raise ValueError("Community analysis must ignore node weights.")

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


def get_mono_community_algorithm_evaluation() -> list[dict[str, object]]:
    return [
        {
            "key": key,
            "label": str(metadata["label"]),
            "supports_directed": bool(metadata["supports_directed"]),
            "supports_weighted": bool(metadata["supports_weighted"]),
            "compatibility_note": str(metadata["compatibility_note"]),
        }
        for key, metadata in MONO_COMMUNITY_ALGORITHM_EVALUATION.items()
    ]


def get_mono_community_algorithms() -> list[dict[str, object]]:
    return [
        {
            "key": key,
            "label": metadata["label"],
            "supports_directed": metadata["supports_directed"],
            "supports_weighted": metadata["supports_weighted"],
            "compatibility_note": metadata["compatibility_note"],
            "requires_graph_adaptation": (
                (not metadata["supports_directed"]) or (not metadata["supports_weighted"])
            ),
        }
        for key, metadata in MONO_COMMUNITY_ALGORITHM_EVALUATION.items()
    ]


def get_default_mono_community_algorithm() -> str:
    return "infomap"


def get_mono_community_algorithm_warning(algorithm_name: str) -> str | None:
    metadata = MONO_COMMUNITY_ALGORITHM_EVALUATION.get(algorithm_name)
    if metadata is None:
        return None

    warnings: list[str] = []
    if not metadata["supports_directed"]:
        warnings.append(
            "This algorithm does not support directed graphs directly. "
            "Infinite Graph will convert the graph to an undirected view before running it."
        )
    if not metadata["supports_weighted"]:
        warnings.append(
            "This algorithm does not support edge weights directly. "
            "Infinite Graph will remove edge weights before running it."
        )
    return "\n\n".join(warnings) if warnings else None


def prepare_mono_community_algorithm_input(
    graph: nx.DiGraph,
    algorithm_name: str,
    **kwargs: object,
) -> tuple[nx.Graph | nx.DiGraph, dict[str, object], list[str]]:
    if algorithm_name not in MONO_COMMUNITY_ALGORITHM_EVALUATION:
        available = ", ".join(sorted(MONO_COMMUNITY_ALGORITHM_EVALUATION))
        raise ValueError(
            f"Unsupported mono-community algorithm: {algorithm_name}. "
            f"Available: {available}"
        )

    metadata = MONO_COMMUNITY_ALGORITHM_EVALUATION[algorithm_name]
    adapted_graph: nx.Graph | nx.DiGraph = graph
    warnings: list[str] = []

    if not metadata["supports_directed"]:
        adapted_graph = _to_weighted_undirected_graph(graph)
        warnings.append(
            "The selected algorithm does not support directed graphs directly. "
            "The graph was converted to an undirected view for this run."
        )

    if not metadata["supports_weighted"]:
        adapted_graph = _drop_edge_weights(adapted_graph)
        warnings.append(
            "The selected algorithm does not support weighted edges directly. "
            "Edge weights were removed for this run."
        )

    call_kwargs = dict(kwargs)
    weight_parameter = metadata["weight_parameter"]
    if (
        metadata["supports_weighted"]
        and weight_parameter is not None
        and weight_parameter not in call_kwargs
    ):
        call_kwargs[weight_parameter] = metadata["weight_value"]
    return adapted_graph, call_kwargs, warnings


def run_mono_community_algorithm(
    graph: nx.DiGraph,
    algorithm_name: str,
    **kwargs: object,
):
    adapted_graph, call_kwargs, _warnings = prepare_mono_community_algorithm_input(
        graph,
        algorithm_name,
        **kwargs,
    )
    algorithm = getattr(algorithms, algorithm_name)
    return algorithm(adapted_graph, **call_kwargs)


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


def _to_weighted_undirected_graph(graph: nx.DiGraph | nx.Graph) -> nx.Graph:
    undirected = nx.Graph()
    for node, data in graph.nodes(data=True):
        undirected.add_node(node, **data)

    for source, target, data in graph.edges(data=True):
        weight = float(data.get("weight", 1.0))
        elements = list(data.get("elements", []))
        if undirected.has_edge(source, target):
            undirected[source][target]["weight"] += weight
            undirected[source][target]["elements"] = sorted(
                set(undirected[source][target].get("elements", [])) | set(elements)
            )
        else:
            undirected.add_edge(source, target, weight=weight, elements=elements)
    return undirected


def _drop_edge_weights(graph: nx.DiGraph | nx.Graph) -> nx.DiGraph | nx.Graph:
    unweighted = graph.copy()
    for _source, _target, data in unweighted.edges(data=True):
        data.pop("weight", None)
    return unweighted


def _normalize_parameters(parameters: Mapping[str, object] | object) -> dict[str, object]:
    if isinstance(parameters, Mapping):
        return {str(key): value for key, value in parameters.items()}
    return {}
