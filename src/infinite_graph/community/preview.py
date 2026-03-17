"""Community preview warning helpers."""

from __future__ import annotations

from collections.abc import Mapping

import networkx as nx

from .agdl import estimate_agdl_runtime_and_communities
from .async_fluid import estimate_async_fluid_runtime_and_communities
from .belief import estimate_belief_runtime_and_communities, format_duration
from .cpm import estimate_cpm_runtime_and_communities
from .der import estimate_der_runtime_and_communities
from .em import estimate_em_runtime_and_communities
from .eigenvector import estimate_eigenvector_runtime_and_communities
from .ga import estimate_ga_runtime_and_communities
from .gdmp2 import estimate_gdmp2_runtime_and_communities
from .girvan_newman import estimate_girvan_newman_runtime_and_communities
from .greedy_modularity import estimate_greedy_modularity_runtime_and_communities
from .head_tail import estimate_head_tail_runtime_and_communities
from .infomap import estimate_infomap_runtime_and_communities
from .kcut import estimate_kcut_runtime_and_communities
from .label_propagation import estimate_label_propagation_runtime_and_communities
from .leiden import estimate_leiden_runtime_and_communities


def build_algorithm_preview_warning(
    algorithm_name: str,
    graph: nx.DiGraph,
    parameters: Mapping[str, object] | None = None,
) -> str | None:
    """Build a benchmark-based preview warning for supported algorithms."""
    params = dict(parameters or {})
    warning = None

    if algorithm_name == "agdl":
        estimate = estimate_agdl_runtime_and_communities(graph, **params)
        warning = "\n".join(
            [
                "AGDL benchmark-based estimate for the current graph and parameters:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                (
                    "This estimate is heuristic and derived from the AGDL benchmark cases "
                    "that actually completed in this project."
                ),
            ]
        )
    elif algorithm_name == "belief":
        estimate = estimate_belief_runtime_and_communities(graph, **params)
        warning = "\n".join(
            [
                "Belief benchmark-based estimate for the current graph and parameters:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )
    elif algorithm_name == "async_fluid":
        estimate = estimate_async_fluid_runtime_and_communities(graph, **params)
        warning = "\n".join(
            [
                "Async Fluid benchmark-based estimate for the current graph and parameters:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                (
                    "- Estimated communities: "
                    f"{int(estimate['estimated_community_count'])} (this follows k by design)"
                ),
                f"- Confidence: {estimate['confidence']}",
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )
    elif algorithm_name == "cpm":
        estimate = estimate_cpm_runtime_and_communities(graph, **params)
        warning = "\n".join(
            [
                "CPM benchmark-based estimate for the current graph and parameters:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )
    elif algorithm_name == "der":
        estimate = estimate_der_runtime_and_communities(graph, **params)
        warning = "\n".join(
            [
                "DER benchmark-based estimate for the current graph and parameters:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                (
                    "DER stayed fast in the project benchmarks, but extreme walk_len and "
                    "iter_bound values were measurably slower on large graphs."
                ),
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )
    elif algorithm_name == "em":
        estimate = estimate_em_runtime_and_communities(graph, **params)
        warning = "\n".join(
            [
                "EM benchmark-based estimate for the current graph and parameters:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                (
                    "EM stayed practical in the project benchmarks, but large acyclic-like "
                    "graphs with high k were the slowest observed cases."
                ),
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )
    elif algorithm_name == "eigenvector" and graph.number_of_nodes() >= 1000:
        estimate = estimate_eigenvector_runtime_and_communities(graph)
        warning = "\n".join(
            [
                "Eigenvector warning for the current graph:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {estimate['estimated_community_count']}",
                f"- Confidence: {estimate['confidence']}.",
                "- Large graphs can trigger an ARPACK precision failure instead of a result.",
                "- This has already been reproduced on the project example save.",
                f"- Estimated ARPACK failure risk: {estimate['arpack_risk']}.",
                "- If it fails, try a smaller subgraph or another community algorithm.",
            ]
        )
    elif algorithm_name == "ga":
        estimate = estimate_ga_runtime_and_communities(graph, **params)
        warning = "\n".join(
            [
                "GA benchmark-based estimate for the current graph and parameters:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                (
                    "GA benchmarks showed that population is the main runtime driver, "
                    "generation is the secondary one, and r mostly changes fragmentation."
                ),
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )
    elif algorithm_name == "gdmp2":
        estimate = estimate_gdmp2_runtime_and_communities(graph, **params)
        warning = "\n".join(
            [
                "GDMP2 benchmark-based estimate for the current graph and parameters:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                (
                    "- Estimated recursion failure risk: "
                    f"{estimate['recursion_risk']}"
                ),
                (
                    "Project benchmarks showed repeatable RecursionError failures around "
                    "1000 nodes for every tested min_threshold value."
                ),
                (
                    "min_threshold changed fragmentation on smaller graphs, but it did not "
                    "remove the large-graph recursion issue."
                ),
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )
    elif algorithm_name == "girvan_newman":
        estimate = estimate_girvan_newman_runtime_and_communities(graph, **params)
        warning = "\n".join(
            [
                "Girvan-Newman benchmark-based estimate for the current graph and parameters:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                (
                    "Project benchmarks showed that runtime grows noticeably with both graph size "
                    "and level, while the observed community count on the tested graph families "
                    "tracked level + 1 for level >= 1."
                ),
                (
                    "The documented level=-1 mode returned an empty partition in this "
                    "environment during project benchmarks, so treat that option cautiously."
                ),
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )
    elif algorithm_name == "greedy_modularity":
        estimate = estimate_greedy_modularity_runtime_and_communities(graph)
        warning = "\n".join(
            [
                "Greedy Modularity benchmark-based estimate for the current graph:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                (
                    "Project benchmarks showed that Greedy Modularity stayed fast even on "
                    "large tested graphs, with community counts growing with graph size."
                ),
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )
    elif algorithm_name == "head_tail":
        estimate = estimate_head_tail_runtime_and_communities(graph, **params)
        warning = "\n".join(
            [
                "Head/Tail benchmark-based estimate for the current graph and parameters:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                f"- Estimated singleton-fragmentation risk: {estimate['singleton_risk']}",
                (
                    "Project benchmarks showed that Head/Tail can become slow on larger graphs, "
                    "and self-loop-heavy graph families collapsed into singleton communities."
                ),
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )
    elif algorithm_name == "infomap":
        estimate = estimate_infomap_runtime_and_communities(graph, **params)
        warning = "\n".join(
            [
                "Infomap benchmark-based estimate for the current graph and parameters:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                (
                    "Project benchmarks showed that Infomap stayed practical on large graphs, "
                    "while num_trials was the main runtime driver and "
                    "preferred_number_of_modules was the clearest community-count control."
                ),
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )
    elif algorithm_name == "kcut":
        estimate = estimate_kcut_runtime_and_communities(graph, **params)
        warning = "\n".join(
            [
                "Kcut benchmark-based estimate for the current graph and parameters:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                (
                    "- Estimated degenerate-partition risk: "
                    f"{estimate['degenerate_partition_risk']}"
                ),
                (
                    "Project benchmarks showed that runtime rises steeply with graph size and "
                    "kmax, while tested graph families often collapsed into one dominant "
                    "community plus many singleton communities."
                ),
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )
    elif algorithm_name == "label_propagation_cordasco_gargano":
        estimate = estimate_label_propagation_runtime_and_communities(graph)
        warning = "\n".join(
            [
                "Label Propagation benchmark-based estimate for the current graph:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                f"- Estimated collapse risk: {estimate['collapse_risk']}",
                (
                    "Project benchmarks showed very different failure modes by structure: "
                    "acyclic-like graphs often collapsed to a single community, cyclic-self "
                    "graphs collapsed into singletons, and large acyclic/cyclic graphs became slow."
                ),
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )
    elif algorithm_name == "leiden":
        estimate = estimate_leiden_runtime_and_communities(graph)
        warning = "\n".join(
            [
                "Leiden benchmark-based estimate for the current graph:",
                (
                    "- Estimated runtime: "
                    f"{format_duration(float(estimate['estimated_runtime_seconds']))}"
                ),
                f"- Estimated communities: {int(estimate['estimated_community_count'])}",
                f"- Confidence: {estimate['confidence']}",
                (
                    "Project benchmarks showed that Leiden stayed fast even on very large "
                    "tested graphs, while self-loop-heavy families produced somewhat more "
                    "communities than the other tested families."
                ),
                (
                    "This estimate is heuristic and derived from project benchmark data, "
                    "not a guarantee."
                ),
            ]
        )

    return warning
