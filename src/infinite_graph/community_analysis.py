"""Helpers for mono-community analysis based on CDlib."""

from __future__ import annotations

import importlib
import io
import os
from collections.abc import Mapping
from contextlib import redirect_stderr, redirect_stdout
from functools import lru_cache

import networkx as nx
from cdlib import algorithms

from . import community_messages
from .community_belief import (
    estimate_belief_runtime_and_communities as _estimate_belief_runtime_and_communities,
)
from .community_preview import build_algorithm_preview_warning

format_mono_community_algorithm_failure = (
    community_messages.format_mono_community_algorithm_failure
)

MONO_COMMUNITY_ALGORITHM_EVALUATION: dict[str, dict[str, object]] = {
    "agdl": {
        "label": "AGDL",
        "supports_directed": True,
        "supports_weighted": True,
        "runtime_warning": (
            "AGDL is experimental in this environment. "
            "Cross-platform benchmarks showed repeatable crashes "
            "on several graph families, "
            "especially many weighted undirected graphs "
            "and some cyclic directed weighted graphs. "
            "The failure also reproduces on standard CDlib examples "
            "such as karate_club_graph(), "
            "so this is treated as an upstream CDlib stability issue "
            "rather than an Infinite Graph bug."
        ),
        "parameter_definitions": [
            {
                "name": "number_communities",
                "label": "Number of communities",
                "type": "int",
                "default": 3,
                "minimum": 1,
            },
            {
                "name": "kc",
                "label": "KC",
                "type": "int",
                "default": 2,
                "minimum": 1,
            },
        ],
        "default_parameters": {
            "number_communities": 3,
            "kc": 2,
        },
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Uses the directed weighted graph as-is.",
    },
    "async_fluid": {
        "label": "Async Fluid",
        "supports_directed": False,
        "supports_weighted": False,
        "runtime_warning": (
            "Async Fluid is usually fast in this project. The main practical control is k, "
            "which directly sets the expected number of communities."
        ),
        "parameter_definitions": [
            {
                "name": "k",
                "label": "K",
                "type": "int",
                "default": 2,
                "minimum": 2,
            },
        ],
        "default_parameters": {
            "k": 2,
        },
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "bayan": {
        "label": "Bayan",
        "supports_directed": False,
        "supports_weighted": False,
        "runtime_warning": (
            "Bayan depends on Gurobi. The main risk in this project comes from running it "
            "without a suitable full license. With only a restricted license, relatively small "
            "graphs can trigger extremely long runs before a size-limit failure, and the runtime "
            "can effectively feel indefinite. On a real Infinite Graph save, a Bayan run was "
            "started around 01:00 and was still running when checked again around 07:00. "
            "This observation was made with a restricted Gurobi license only; no equivalent test "
            "was run with a full license. With a proper license, Bayan is expected to be far less "
            "problematic."
        ),
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "belief": {
        "label": "Belief",
        "supports_directed": False,
        "supports_weighted": False,
        "runtime_warning": (
            "Belief can become expensive quickly as the graph grows. "
            "Project benchmarks showed runs moving from sub-second at 20 nodes "
            "to several minutes at 1000 nodes depending on graph structure and parameters. "
            "Use the pre-run estimate as a guide before launching it on a large save."
        ),
        "parameter_definitions": [
            {
                "name": "max_it",
                "label": "Max iterations",
                "type": "int",
                "default": 100,
                "minimum": 1,
            },
            {
                "name": "eps",
                "label": "Epsilon",
                "type": "float",
                "default": 0.0001,
                "minimum": 0.0,
                "maximum": 1.0,
                "decimals": 4,
                "step": 0.0001,
            },
            {
                "name": "reruns_if_not_conv",
                "label": "Reruns if not converged",
                "type": "int",
                "default": 5,
                "minimum": 0,
            },
            {
                "name": "threshold",
                "label": "Threshold",
                "type": "float",
                "default": 0.005,
                "minimum": 0.0,
                "maximum": 1.0,
                "decimals": 4,
                "step": 0.0001,
            },
            {
                "name": "q_max",
                "label": "Q max",
                "type": "int",
                "default": 7,
                "minimum": 1,
            },
        ],
        "default_parameters": {
            "max_it": 100,
            "eps": 0.0001,
            "reruns_if_not_conv": 5,
            "threshold": 0.005,
            "q_max": 7,
        },
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "cpm": {
        "label": "CPM",
        "supports_directed": False,
        "supports_weighted": True,
        "runtime_warning": (
            "CPM is usually fast in this project, but the resolution parameter strongly affects "
            "how fragmented the result becomes. Use the pre-run estimate to preview both runtime "
            "and the approximate number of communities before launching it on a large save."
        ),
        "parameter_definitions": [
            {
                "name": "resolution_parameter",
                "label": "Resolution parameter",
                "type": "float",
                "default": 1.0,
                "minimum": 0.0,
                "maximum": 1000.0,
                "decimals": 3,
                "step": 0.1,
            },
        ],
        "default_parameters": {
            "resolution_parameter": 1.0,
        },
        "weight_parameter": "weights",
        "weight_value": "weight",
        "compatibility_note": "Will run on an undirected weighted view of the graph.",
    },
    "der": {
        "label": "DER",
        "supports_directed": False,
        "supports_weighted": True,
        "runtime_warning": (
            "DER is generally fast in this project, but very large walk lengths and iteration "
            "bounds can still increase runtime noticeably on large graphs. Use the pre-run "
            "estimate if you push those parameters far above the defaults."
        ),
        "parameter_definitions": [
            {
                "name": "walk_len",
                "label": "Walk length",
                "type": "int",
                "default": 3,
                "minimum": 1,
            },
            {
                "name": "threshold",
                "label": "Threshold",
                "type": "float",
                "default": 0.00001,
                "minimum": 0.0,
                "maximum": 1.0,
                "decimals": 5,
                "step": 0.00001,
            },
            {
                "name": "iter_bound",
                "label": "Iteration bound",
                "type": "int",
                "default": 50,
                "minimum": 1,
            },
        ],
        "default_parameters": {
            "walk_len": 3,
            "threshold": 0.00001,
            "iter_bound": 50,
        },
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected weighted view of the graph.",
    },
    "eigenvector": {
        "label": "Eigenvector",
        "supports_directed": False,
        "supports_weighted": False,
        "runtime_warning": (
            "Eigenvector relies on ARPACK and can fail on large graphs with a numerical "
            "precision error instead of returning a partition. If that happens, try a smaller "
            "subgraph or switch to a more robust algorithm for large saves."
        ),
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
    "em": {
        "label": "EM",
        "supports_directed": False,
        "supports_weighted": False,
        "runtime_warning": (
            "EM is usually practical in this project. Runtime mainly grows with graph size and k, "
            "and large acyclic-like graphs are the costliest cases observed in benchmarks."
        ),
        "parameter_definitions": [
            {
                "name": "k",
                "label": "K",
                "type": "int",
                "default": 3,
                "minimum": 1,
            },
        ],
        "default_parameters": {"k": 3},
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
        "callable_name": "label_propagation",
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
        "supports_weighted": True,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected weighted view of the graph.",
    },
    "lswl_plus": {
        "label": "LSWL Plus",
        "supports_directed": False,
        "supports_weighted": True,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected weighted view of the graph.",
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
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
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
        "supports_weighted": False,
        "weight_parameter": None,
        "weight_value": None,
        "compatibility_note": "Will run on an undirected unweighted view of the graph.",
    },
}


def uses_directed_community_graph() -> bool:
    return True


def uses_edge_weights_only() -> bool:
    return True


def ignores_node_weights() -> bool:
    return True


def estimate_belief_runtime_and_communities(
    graph: nx.DiGraph,
    **parameters: object,
) -> dict[str, object]:
    """Expose the Belief estimator through the main community analysis module."""
    return _estimate_belief_runtime_and_communities(graph, **parameters)


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
        label = str(node.get("label", node_id))
        graph.add_node(node_id, label=label)

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


def _is_unix_platform() -> bool:
    return os.name == "posix"


def _is_mono_community_algorithm_visible(algorithm_name: str) -> bool:
    if algorithm_name == "label_propagation_raghavan":
        return False
    if algorithm_name in {"ricci_community", "sbm_dl", "sbm_dl_nested"} and not _is_unix_platform():
        return False
    return True


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
        if _is_mono_community_algorithm_visible(key)
    ]


def get_mono_community_algorithm_parameters(
    algorithm_name: str,
) -> list[dict[str, object]]:
    metadata = MONO_COMMUNITY_ALGORITHM_EVALUATION.get(algorithm_name)
    if metadata is None:
        return []
    parameter_definitions = metadata.get("parameter_definitions", [])
    if not isinstance(parameter_definitions, list):
        return []
    return [
        {str(key): value for key, value in parameter.items()}
        for parameter in parameter_definitions
        if isinstance(parameter, Mapping)
    ]


def get_default_mono_community_algorithm() -> str:
    return "infomap"


@lru_cache(maxsize=1)
def get_bayan_gurobi_status() -> dict[str, object]:
    """Return a best-effort snapshot of the local Gurobi runtime status."""
    try:
        gp = importlib.import_module("gurobipy")
    except ImportError:
        return {
            "available": False,
            "restricted": False,
            "license_expiration": None,
            "message": "gurobipy is not installed.",
        }

    output = io.StringIO()
    try:
        with redirect_stdout(output), redirect_stderr(output):
            model = gp.Model()
    except Exception as exc:  # noqa: BLE001
        return {
            "available": False,
            "restricted": False,
            "license_expiration": None,
            "message": f"Gurobi could not start: {exc}",
        }

    banner = output.getvalue().strip()
    restricted = "restricted license" in banner.lower()
    expiration = None
    try:
        expiration = model.getAttr("LicenseExpiration")
    except Exception:  # pragma: no cover - defensive only
        expiration = None
    dispose = getattr(model, "dispose", None)
    if callable(dispose):
        dispose()

    return {
        "available": True,
        "restricted": restricted,
        "license_expiration": expiration,
        "message": banner or "Gurobi runtime detected.",
    }


def get_mono_community_algorithm_pre_run_warning(
    algorithm_name: str,
    graph: nx.DiGraph | None = None,
    parameters: Mapping[str, object] | None = None,
) -> str | None:
    """Return a warning that should be shown before starting an algorithm run."""
    metadata = MONO_COMMUNITY_ALGORITHM_EVALUATION.get(algorithm_name)
    if metadata is None:
        return None

    warnings: list[str] = []
    runtime_warning = metadata.get("runtime_warning")
    if isinstance(runtime_warning, str) and runtime_warning:
        warnings.append(runtime_warning)

    if algorithm_name == "bayan":
        gurobi_status = get_bayan_gurobi_status()
        if not bool(gurobi_status["available"]):
            warnings.append(
                "Gurobi is not available in this environment, so Bayan is expected to fail.\n"
                f"Details: {gurobi_status['message']}"
            )
        elif bool(gurobi_status["restricted"]):
            warning_lines = [
                "A restricted Gurobi license was detected for Bayan.",
                "This setup can fail on relatively small graphs with a size-limit error "
                "after spending an unknown amount of time inside the solver.",
                "A real Infinite Graph save already reproduced this behavior with an overnight "
                "run that started around 01:00 and was still blocked when checked again "
                "around 07:00.",
                "This observation only comes from a restricted-license setup; no equivalent "
                "runtime test was completed with a full Gurobi license.",
                "With a proper full license, this specific risk is expected to be much lower.",
            ]
            license_expiration = gurobi_status.get("license_expiration")
            if license_expiration:
                warning_lines.append(f"License expiration: {license_expiration}")
            message = str(gurobi_status.get("message", "")).strip()
            if message:
                warning_lines.append(f"Gurobi banner: {message}")
                warnings.append("\n".join(warning_lines))

    if graph is not None:
        preview_warning = build_algorithm_preview_warning(
            algorithm_name,
            graph,
            parameters,
        )
        if preview_warning:
            warnings.append(preview_warning)

    return "\n\n".join(warnings) if warnings else None


def get_mono_community_algorithm_warning(algorithm_name: str) -> str | None:
    metadata = MONO_COMMUNITY_ALGORITHM_EVALUATION.get(algorithm_name)
    if metadata is None:
        return None

    warnings: list[str] = []
    runtime_warning = metadata.get("runtime_warning")
    if isinstance(runtime_warning, str) and runtime_warning:
        warnings.append(runtime_warning)
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
            f"Unsupported mono-community algorithm: {algorithm_name}. " f"Available: {available}"
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
    default_parameters = metadata.get("default_parameters", {})
    if isinstance(default_parameters, Mapping):
        for key, value in default_parameters.items():
            call_kwargs.setdefault(str(key), value)
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
    algorithm_callable_name = str(
        MONO_COMMUNITY_ALGORITHM_EVALUATION[algorithm_name].get("callable_name", algorithm_name)
    )
    algorithm = getattr(algorithms, algorithm_callable_name)
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
