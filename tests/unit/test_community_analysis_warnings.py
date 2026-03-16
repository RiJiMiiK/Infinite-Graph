from __future__ import annotations

from types import SimpleNamespace

import networkx as nx

from src.infinite_graph.community import (
    agdl as community_agdl,
    analysis as community_analysis,
    async_fluid as community_async_fluid,
    belief as community_belief,
    cpm as community_cpm,
    der as community_der,
    eigenvector as community_eigenvector,
    em as community_em,
    ga as community_ga,
    gdmp2 as community_gdmp2,
    girvan_newman as community_girvan_newman,
    greedy_modularity as community_greedy_modularity,
    head_tail as community_head_tail,
    infomap as community_infomap,
    kcut as community_kcut,
    label_propagation as community_label_propagation,
)


def test_get_mono_community_algorithm_warning() -> None:
    assert community_analysis.get_mono_community_algorithm_warning("infomap") is None
    agdl_warning = community_analysis.get_mono_community_algorithm_warning("agdl")
    assert agdl_warning is not None
    assert "experimental in this environment" in agdl_warning
    assert "karate_club_graph()" in agdl_warning
    belief_warning = community_analysis.get_mono_community_algorithm_warning("belief")
    assert belief_warning is not None
    assert "several minutes at 1000 nodes" in belief_warning
    leiden_warning = community_analysis.get_mono_community_algorithm_warning("leiden")
    assert leiden_warning is not None
    assert "does not support directed graphs directly" in leiden_warning
    rber_warning = community_analysis.get_mono_community_algorithm_warning("rber_pots")
    assert rber_warning is not None
    assert "does not support edge weights directly" in rber_warning
    eigenvector_warning = community_analysis.get_mono_community_algorithm_warning("eigenvector")
    assert eigenvector_warning is not None
    assert "ARPACK" in eigenvector_warning
    gdmp2_warning = community_analysis.get_mono_community_algorithm_warning("gdmp2")
    assert gdmp2_warning is not None
    assert "RecursionError around 1000 nodes" in gdmp2_warning
    girvan_newman_warning = community_analysis.get_mono_community_algorithm_warning(
        "girvan_newman"
    )
    assert girvan_newman_warning is not None
    assert "10000-node benchmark run did not finish" in girvan_newman_warning
    greedy_modularity_warning = community_analysis.get_mono_community_algorithm_warning(
        "greedy_modularity"
    )
    assert greedy_modularity_warning is not None
    assert "stayed fast in project benchmarks" in greedy_modularity_warning
    head_tail_warning = community_analysis.get_mono_community_algorithm_warning("head_tail")
    assert head_tail_warning is not None
    assert "singleton communities" in head_tail_warning
    assert community_analysis.get_mono_community_algorithm_warning("unknown") is None


def test_estimate_agdl_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "C", weight=2.0)
    graph.add_edge("C", "A", weight=3.0)

    estimate = community_agdl.estimate_agdl_runtime_and_communities(
        graph,
        number_communities=3,
        kc=2,
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) >= 1
    assert estimate["confidence"] == "low"


def test_get_mono_community_algorithm_pre_run_warning_for_agdl() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "agdl",
        graph,
        {"number_communities": 3, "kc": 2},
    )

    assert warning is not None
    assert "experimental in this environment" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning


def test_get_mono_community_algorithm_pre_run_warning_for_bayan(monkeypatch) -> None:
    monkeypatch.setattr(
        community_analysis,
        "get_bayan_gurobi_status",
        lambda: {
            "available": True,
            "restricted": True,
            "license_expiration": 20271129,
            "message": "Restricted license - for non-production use only - expires 2027-11-29",
        },
    )

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning("bayan")

    assert warning is not None
    assert "runtime can effectively feel indefinite" in warning
    assert "restricted Gurobi license" in warning
    assert "20271129" in warning
    assert "checked again around 07:00" in warning
    assert "no equivalent test was run with a full license" in warning
    assert "far less problematic" in warning


def test_estimate_belief_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_analysis.estimate_belief_runtime_and_communities(
        graph,
        max_it=100,
        eps=0.0001,
        reruns_if_not_conv=5,
        threshold=0.005,
        q_max=7,
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) >= 1
    assert estimate["confidence"] in {"high", "medium", "low"}


def test_estimate_async_fluid_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_async_fluid.estimate_async_fluid_runtime_and_communities(
        graph,
        k=3,
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) == 3
    assert estimate["confidence"] in {"high", "medium", "low"}


def test_get_mono_community_algorithm_pre_run_warning_for_async_fluid() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "async_fluid",
        graph,
        {"k": 4},
    )

    assert warning is not None
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "follows k by design" in warning
    assert "Confidence:" in warning


def test_get_mono_community_algorithm_pre_run_warning_for_belief() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "belief",
        graph,
        {
            "max_it": 100,
            "eps": 0.0001,
            "reruns_if_not_conv": 5,
            "threshold": 0.005,
            "q_max": 7,
        },
    )

    assert warning is not None
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning


def test_estimate_cpm_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_cpm.estimate_cpm_runtime_and_communities(
        graph,
        resolution_parameter=0.1,
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) >= 1
    assert estimate["confidence"] in {"high", "medium", "low"}


def test_estimate_der_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_der.estimate_der_runtime_and_communities(
        graph,
        walk_len=5,
        threshold=0.001,
        iter_bound=100,
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) >= 1
    assert estimate["confidence"] in {"high", "medium", "low"}


def test_estimate_eigenvector_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_eigenvector.estimate_eigenvector_runtime_and_communities(graph)

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) >= 1
    assert estimate["confidence"] in {"high", "medium", "low"}
    assert estimate["arpack_risk"] in {"high", "medium", "low"}


def test_estimate_eigenvector_runtime_and_communities_large_graph_sets_low_confidence() -> None:
    graph = nx.DiGraph()
    for index in range(5001):
        graph.add_node(str(index))
    for index in range(5000):
        graph.add_edge(str(index), str(index + 1), weight=1.0)

    estimate = community_eigenvector.estimate_eigenvector_runtime_and_communities(graph)

    assert estimate["confidence"] == "low"
    assert estimate["arpack_risk"] == "medium"


def test_estimate_eigenvector_runtime_and_communities_self_loop_risk_high() -> None:
    graph = nx.DiGraph()
    for index in range(10):
        node = str(index)
        graph.add_edge(node, node, weight=1.0)

    estimate = community_eigenvector.estimate_eigenvector_runtime_and_communities(graph)

    assert estimate["arpack_risk"] == "high"


def test_estimate_em_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_em.estimate_em_runtime_and_communities(graph, k=4)

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) == 4
    assert estimate["confidence"] in {"high", "medium", "low"}


def test_estimate_ga_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_ga.estimate_ga_runtime_and_communities(
        graph,
        population=300,
        generation=30,
        r=1.5,
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) >= 1
    assert estimate["confidence"] in {"high", "medium", "low"}


def test_estimate_gdmp2_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_gdmp2.estimate_gdmp2_runtime_and_communities(
        graph,
        min_threshold=0.42,
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) >= 1
    assert estimate["confidence"] in {"high", "medium", "low"}
    assert estimate["recursion_risk"] in {"high", "medium", "low"}


def test_estimate_gdmp2_runtime_and_communities_medium_recursion_risk() -> None:
    graph = nx.DiGraph()
    for index in range(700):
        graph.add_edge(str(index), str((index + 1) % 700), weight=1.0)

    estimate = community_gdmp2.estimate_gdmp2_runtime_and_communities(
        graph,
        min_threshold=0.42,
    )

    assert estimate["confidence"] == "low"
    assert estimate["recursion_risk"] == "medium"


def test_estimate_gdmp2_runtime_and_communities_mid_size_recursion_risk() -> None:
    graph = nx.DiGraph()
    for index in range(500):
        graph.add_edge(str(index), str((index + 1) % 500), weight=1.0)

    estimate = community_gdmp2.estimate_gdmp2_runtime_and_communities(
        graph,
        min_threshold=0.42,
    )

    assert estimate["confidence"] in {"high", "medium", "low"}
    assert estimate["recursion_risk"] == "medium"


def test_estimate_gdmp2_runtime_and_communities_high_recursion_risk() -> None:
    graph = nx.DiGraph()
    for index in range(1000):
        graph.add_edge(str(index), str((index + 1) % 1000), weight=1.0)

    estimate = community_gdmp2.estimate_gdmp2_runtime_and_communities(
        graph,
        min_threshold=0.42,
    )

    assert estimate["confidence"] == "low"
    assert estimate["recursion_risk"] == "high"


def test_estimate_girvan_newman_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_girvan_newman.estimate_girvan_newman_runtime_and_communities(
        graph,
        level=3,
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) == 4
    assert estimate["confidence"] in {"high", "medium", "low"}


def test_estimate_girvan_newman_runtime_and_communities_level_minus_one() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)

    estimate = community_girvan_newman.estimate_girvan_newman_runtime_and_communities(
        graph,
        level=-1,
    )

    assert estimate["estimated_community_count"] == 0
    assert estimate["confidence"] == "low"


def test_estimate_greedy_modularity_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_greedy_modularity.estimate_greedy_modularity_runtime_and_communities(
        graph
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) >= 1
    assert estimate["confidence"] in {"high", "medium", "low"}


def test_estimate_head_tail_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_head_tail.estimate_head_tail_runtime_and_communities(
        graph,
        head_tail_ratio=0.4,
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) >= 1
    assert estimate["confidence"] in {"high", "medium", "low"}
    assert estimate["singleton_risk"] in {"high", "medium", "low"}


def test_estimate_head_tail_runtime_and_communities_low_singleton_risk() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "C", weight=1.0)

    estimate = community_head_tail.estimate_head_tail_runtime_and_communities(
        graph,
        head_tail_ratio=0.4,
    )

    assert estimate["singleton_risk"] == "low"


def test_estimate_head_tail_runtime_and_communities_high_singleton_risk() -> None:
    graph = nx.DiGraph()
    for index in range(4):
        node = str(index)
        graph.add_edge(node, node, weight=1.0)

    estimate = community_head_tail.estimate_head_tail_runtime_and_communities(
        graph,
        head_tail_ratio=0.4,
    )

    assert estimate["singleton_risk"] == "high"


def test_estimate_head_tail_runtime_and_communities_medium_singleton_risk() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "A", weight=1.0)
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "C", weight=1.0)
    graph.add_edge("C", "D", weight=1.0)

    estimate = community_head_tail.estimate_head_tail_runtime_and_communities(
        graph,
        head_tail_ratio=0.4,
    )

    assert estimate["singleton_risk"] == "medium"


def test_estimate_infomap_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_infomap.estimate_infomap_runtime_and_communities(
        graph,
        num_trials=3,
        seed=999,
        markov_time=2.0,
        preferred_number_of_modules=5,
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) >= 1
    assert estimate["confidence"] in {"high", "medium", "low"}


def test_estimate_kcut_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_kcut.estimate_kcut_runtime_and_communities(graph, kmax=4)

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) >= 1
    assert estimate["confidence"] in {"high", "medium", "low"}
    assert estimate["degenerate_partition_risk"] in {"high", "medium", "low"}


def test_estimate_kcut_runtime_and_communities_low_confidence() -> None:
    graph = nx.DiGraph()
    for index in range(1000):
        graph.add_edge(str(index), str((index + 1) % 1000), weight=1.0)

    estimate = community_kcut.estimate_kcut_runtime_and_communities(graph, kmax=4)

    assert estimate["confidence"] == "low"


def test_estimate_kcut_runtime_and_communities_medium_degenerate_risk(monkeypatch) -> None:
    graph = nx.DiGraph()
    for index in range(100):
        graph.add_edge(str(index), str(index + 1), weight=1.0)

    monkeypatch.setattr(
        community_kcut,
        "finalize_estimate",
        lambda *args, **kwargs: {
            "estimated_runtime_seconds": 1.0,
            "estimated_community_count": 6,
            "confidence": "high",
            "features": {"nodes": 100.0},
        },
    )

    estimate = community_kcut.estimate_kcut_runtime_and_communities(graph, kmax=2)

    assert estimate["degenerate_partition_risk"] == "medium"


def test_estimate_label_propagation_runtime_and_communities() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    estimate = community_label_propagation.estimate_label_propagation_runtime_and_communities(
        graph
    )

    assert float(estimate["estimated_runtime_seconds"]) > 0.0
    assert int(estimate["estimated_community_count"]) >= 1
    assert estimate["confidence"] in {"high", "medium", "low"}
    assert estimate["collapse_risk"] in {"single", "split_or_single", "mixed", "singleton"}


def test_estimate_label_propagation_runtime_and_communities_singleton_risk() -> None:
    graph = nx.DiGraph()
    for index in range(3):
        graph.add_edge(str(index), str(index), weight=1.0)

    estimate = community_label_propagation.estimate_label_propagation_runtime_and_communities(
        graph
    )

    assert estimate["collapse_risk"] == "singleton"


def test_estimate_label_propagation_runtime_and_communities_mixed_risk() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "A", weight=1.0)
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "C", weight=1.0)

    estimate = community_label_propagation.estimate_label_propagation_runtime_and_communities(
        graph
    )

    assert estimate["collapse_risk"] == "mixed"


def test_estimate_label_propagation_runtime_and_communities_split_or_single_risk() -> None:
    graph = nx.DiGraph()
    for source in range(4):
        for target in range(4):
            if source != target:
                graph.add_edge(str(source), str(target), weight=1.0)

    estimate = community_label_propagation.estimate_label_propagation_runtime_and_communities(
        graph
    )

    assert estimate["collapse_risk"] == "split_or_single"


def test_estimate_label_propagation_runtime_and_communities_single_risk_and_medium_confidence() -> None:
    graph = nx.DiGraph()
    for index in range(3000):
        graph.add_edge(str(index), str(index + 1), weight=1.0)

    estimate = community_label_propagation.estimate_label_propagation_runtime_and_communities(
        graph
    )

    assert estimate["collapse_risk"] == "single"
    assert estimate["confidence"] == "medium"


def test_get_mono_community_algorithm_pre_run_warning_for_cpm() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "cpm",
        graph,
        {"resolution_parameter": 0.5},
    )

    assert warning is not None
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning


def test_get_mono_community_algorithm_pre_run_warning_for_der() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "der",
        graph,
        {"walk_len": 20, "threshold": 0.1, "iter_bound": 500},
    )

    assert warning is not None
    assert "DER benchmark-based estimate" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning
    assert "walk_len and iter_bound" in warning


def test_get_mono_community_algorithm_pre_run_warning_for_em() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "em",
        graph,
        {"k": 6},
    )

    assert warning is not None
    assert "EM benchmark-based estimate" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning


def test_get_mono_community_algorithm_pre_run_warning_for_ga() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "ga",
        graph,
        {"population": 300, "generation": 30, "r": 1.5},
    )

    assert warning is not None
    assert "GA can become expensive quickly" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning


def test_get_mono_community_algorithm_pre_run_warning_for_gdmp2() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "gdmp2",
        graph,
        {"min_threshold": 0.42},
    )

    assert warning is not None
    assert "GDMP2 stayed fast on small and medium benchmark graphs" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning
    assert "Estimated recursion failure risk:" in warning
    assert "RecursionError" in warning


def test_get_mono_community_algorithm_pre_run_warning_for_girvan_newman() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "girvan_newman",
        graph,
        {"level": 4},
    )

    assert warning is not None
    assert "Girvan-Newman becomes expensive" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning
    assert "level + 1" in warning
    assert "level=-1 mode returned an empty partition" in warning


def test_get_mono_community_algorithm_pre_run_warning_for_greedy_modularity() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "greedy_modularity",
        graph,
        {},
    )

    assert warning is not None
    assert "Greedy Modularity stayed fast in project benchmarks" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning


def test_get_mono_community_algorithm_pre_run_warning_for_head_tail() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "head_tail",
        graph,
        {"head_tail_ratio": 0.8},
    )

    assert warning is not None
    assert "small-medium sized graphs" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning
    assert "Estimated singleton-fragmentation risk:" in warning


def test_get_mono_community_algorithm_pre_run_warning_for_infomap() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "infomap",
        graph,
        {
            "num_trials": 3,
            "seed": 999,
            "markov_time": 2.0,
            "preferred_number_of_modules": 5,
        },
    )

    assert warning is not None
    assert "Infomap benchmark-based estimate" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning
    assert "num_trials was the main runtime driver" in warning


def test_get_mono_community_algorithm_pre_run_warning_for_kcut() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "kcut",
        graph,
        {"kmax": 6},
    )

    assert warning is not None
    assert "Kcut benchmark-based estimate" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning
    assert "Estimated degenerate-partition risk:" in warning


def test_get_mono_community_algorithm_pre_run_warning_for_label_propagation() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "A", weight=1.0)
    graph.add_edge("A", "A", weight=0.25)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "label_propagation_cordasco_gargano",
        graph,
        {},
    )

    assert warning is not None
    assert "Label Propagation benchmark-based estimate" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Confidence:" in warning
    assert "Estimated collapse risk:" in warning


def test_get_mono_community_algorithm_pre_run_warning_for_eigenvector_large_graph() -> None:
    graph = nx.DiGraph()
    for index in range(1001):
        graph.add_node(str(index))
    for index in range(1000):
        graph.add_edge(str(index), str(index + 1), weight=1.0)

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning(
        "eigenvector",
        graph,
        {},
    )

    assert warning is not None
    assert "ARPACK precision failure" in warning
    assert "project example save" in warning
    assert "Estimated runtime:" in warning
    assert "Estimated communities:" in warning
    assert "Estimated ARPACK failure risk:" in warning


def test_format_mono_community_algorithm_failure_for_eigenvector_arpack() -> None:
    graph = nx.DiGraph()
    graph.add_nodes_from(["A", "B"])

    message = community_analysis.format_mono_community_algorithm_failure(
        "eigenvector",
        RuntimeError(
            "Error at src/community/leading_eigenvector.c:567: "
            "No eigenvalues to sufficient accuracy. -- ARPACK error"
        ),
        graph,
    )

    assert "Algorithm: eigenvector" in message
    assert "Graph size: 2 nodes." in message
    assert "ARPACK could not compute eigenvalues with sufficient accuracy" in message
    assert "try a smaller subgraph" in message


def test_format_mono_community_algorithm_failure_default() -> None:
    message = community_analysis.format_mono_community_algorithm_failure(
        "der",
        RuntimeError("boom"),
        None,
    )

    assert message == (
        "Unable to compute communities with the selected algorithm.\n\n"
        "Algorithm: der\n"
        "Details: boom"
    )


def test_format_duration_covers_all_ranges() -> None:
    assert community_belief.format_duration(12.5) == "12.5s"
    assert community_belief.format_duration(75.5) == "1m 15.5s"
    assert community_belief.format_duration(3671.2) == "1h 1m 11.2s"


def test_get_bayan_gurobi_status_when_gurobi_is_missing(monkeypatch) -> None:
    community_analysis.get_bayan_gurobi_status.cache_clear()

    def fake_import_module(name: str):
        raise ImportError("missing gurobi")

    monkeypatch.setattr(community_analysis.importlib, "import_module", fake_import_module)

    status = community_analysis.get_bayan_gurobi_status()

    assert status == {
        "available": False,
        "restricted": False,
        "license_expiration": None,
        "message": "gurobipy is not installed.",
    }
    community_analysis.get_bayan_gurobi_status.cache_clear()


def test_get_bayan_gurobi_status_with_restricted_license(monkeypatch) -> None:
    community_analysis.get_bayan_gurobi_status.cache_clear()

    class FakeModel:
        def __init__(self) -> None:
            print("Restricted license - for non-production use only - expires 2027-11-29")

        def getAttr(self, name: str) -> int:
            assert name == "LicenseExpiration"
            return 20271129

        def dispose(self) -> None:
            return None

    fake_gp = SimpleNamespace(Model=FakeModel)
    monkeypatch.setattr(
        community_analysis.importlib,
        "import_module",
        lambda name: fake_gp,
    )

    status = community_analysis.get_bayan_gurobi_status()

    assert status == {
        "available": True,
        "restricted": True,
        "license_expiration": 20271129,
        "message": "Restricted license - for non-production use only - expires 2027-11-29",
    }
    community_analysis.get_bayan_gurobi_status.cache_clear()


def test_get_bayan_gurobi_status_when_model_creation_fails(monkeypatch) -> None:
    community_analysis.get_bayan_gurobi_status.cache_clear()

    class FakeModel:
        def __init__(self) -> None:
            raise RuntimeError("license failure")

    fake_gp = SimpleNamespace(Model=FakeModel)
    monkeypatch.setattr(
        community_analysis.importlib,
        "import_module",
        lambda name: fake_gp,
    )

    status = community_analysis.get_bayan_gurobi_status()

    assert status == {
        "available": False,
        "restricted": False,
        "license_expiration": None,
        "message": "Gurobi could not start: license failure",
    }
    community_analysis.get_bayan_gurobi_status.cache_clear()


def test_get_mono_community_algorithm_pre_run_warning_for_missing_bayan_runtime(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        community_analysis,
        "get_bayan_gurobi_status",
        lambda: {
            "available": False,
            "restricted": False,
            "license_expiration": None,
            "message": "gurobipy is not installed.",
        },
    )

    warning = community_analysis.get_mono_community_algorithm_pre_run_warning("bayan")

    assert warning is not None
    assert "Gurobi is not available" in warning
    assert "gurobipy is not installed" in warning
    assert community_analysis.get_mono_community_algorithm_pre_run_warning("infomap") is None
    assert community_analysis.get_mono_community_algorithm_pre_run_warning("unknown") is None
