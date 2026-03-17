from __future__ import annotations

from types import SimpleNamespace

import networkx as nx
import pytest

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
)


def test_build_cdlib_graph_preserves_direction_and_edge_weights() -> None:
    graph = community_analysis.build_cdlib_graph(
        [
            {"id": "Water", "label": "Water"},
            {"id": "Steam", "label": "Steam", "weight": 99},
        ],
        [
            {
                "source": "Water",
                "target": "Steam",
                "weight": 3,
                "elements": ["Fire", "Heat"],
            }
        ],
    )

    assert isinstance(graph, nx.DiGraph)
    assert sorted(graph.nodes) == ["Steam", "Water"]
    assert graph.nodes["Water"]["label"] == "Water"
    assert "weight" not in graph.nodes["Steam"]
    assert graph["Water"]["Steam"]["weight"] == 3.0
    assert graph["Water"]["Steam"]["elements"] == ["Fire", "Heat"]


def test_build_cdlib_graph_requires_directed_mode(monkeypatch) -> None:
    monkeypatch.setattr(community_analysis, "uses_directed_community_graph", lambda: False)

    with pytest.raises(ValueError, match="must keep the graph directed"):
        community_analysis.build_cdlib_graph([], [])


def test_build_cdlib_graph_requires_ignoring_node_weights(monkeypatch) -> None:
    monkeypatch.setattr(community_analysis, "ignores_node_weights", lambda: False)

    with pytest.raises(ValueError, match="must ignore node weights"):
        community_analysis.build_cdlib_graph([], [])


def test_algorithm_evaluation_lists_all_algorithms_with_compatibility_notes() -> None:
    evaluation = community_analysis.get_mono_community_algorithm_evaluation()
    assert [item["key"] for item in evaluation] == [
        "agdl",
        "async_fluid",
        "bayan",
        "belief",
        "cpm",
        "der",
        "eigenvector",
        "em",
        "ga",
        "gdmp2",
        "girvan_newman",
        "greedy_modularity",
        "head_tail",
        "infomap",
        "kcut",
        "label_propagation_raghavan",
        "label_propagation_cordasco_gargano",
        "leiden",
        "louvain",
        "lswl",
        "lswl_plus",
        "markov_clustering",
        "mcode",
        "mod_m",
        "mod_r",
        "paris",
        "pycombo",
        "rber_pots",
        "rb_pots",
        "ricci_community",
        "r_spectral_clustering",
        "scan",
        "significance_communities",
        "spinglass",
        "surprise_communities",
        "sbm_dl",
        "sbm_dl_nested",
        "spectral",
        "threshold_clustering",
        "walktrap",
    ]
    assert "directed weighted graph as-is" in next(
        item["compatibility_note"] for item in evaluation if item["key"] == "infomap"
    )
    assert "undirected unweighted view" in next(
        item["compatibility_note"] for item in evaluation if item["key"] == "rber_pots"
    )
    assert "undirected weighted view" in next(
        item["compatibility_note"] for item in evaluation if item["key"] == "der"
    )

    algorithms = community_analysis.get_mono_community_algorithms()
    visible_keys = [item["key"] for item in algorithms]
    assert "label_propagation_raghavan" not in visible_keys
    assert "sbm_dl" not in visible_keys
    assert "sbm_dl_nested" not in visible_keys
    assert "ricci_community" not in visible_keys
    assert (
        next(item for item in algorithms if item["key"] == "infomap")["requires_graph_adaptation"]
        is False
    )
    assert (
        next(item for item in algorithms if item["key"] == "leiden")["requires_graph_adaptation"]
        is True
    )
    assert (
        next(item for item in algorithms if item["key"] == "rber_pots")["requires_graph_adaptation"]
        is True
    )
    assert community_analysis.get_default_mono_community_algorithm() == "infomap"
    assert community_analysis.uses_directed_community_graph() is True
    assert community_analysis.uses_edge_weights_only() is True
    assert community_analysis.ignores_node_weights() is True


def test_algorithm_visibility_rules() -> None:
    assert (
        community_analysis._is_mono_community_algorithm_visible("label_propagation_raghavan")
        is False
    )
    assert community_analysis._is_mono_community_algorithm_visible("sbm_dl") is False
    assert community_analysis._is_mono_community_algorithm_visible("sbm_dl_nested") is False
    assert community_analysis._is_mono_community_algorithm_visible("ricci_community") is False
    assert community_analysis._is_mono_community_algorithm_visible("infomap") is True


def test_algorithm_visibility_rules_for_unix_platform(monkeypatch) -> None:
    monkeypatch.setattr(community_analysis, "_is_unix_platform", lambda: True)

    assert community_analysis._is_mono_community_algorithm_visible("sbm_dl") is True
    assert community_analysis._is_mono_community_algorithm_visible("sbm_dl_nested") is True
    assert community_analysis._is_mono_community_algorithm_visible("ricci_community") is True


def test_get_mono_community_algorithm_parameters() -> None:
    async_fluid_parameters = community_analysis.get_mono_community_algorithm_parameters(
        "async_fluid"
    )
    assert async_fluid_parameters == [
        {
            "name": "k",
            "label": "K",
            "type": "int",
            "default": 2,
            "minimum": 2,
        }
    ]

    cpm_parameters = community_analysis.get_mono_community_algorithm_parameters("cpm")
    assert cpm_parameters == [
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
    ]

    belief_parameters = community_analysis.get_mono_community_algorithm_parameters("belief")
    assert belief_parameters == [
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
    ]

    der_parameters = community_analysis.get_mono_community_algorithm_parameters("der")
    assert der_parameters == [
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
    ]

    em_parameters = community_analysis.get_mono_community_algorithm_parameters("em")
    assert em_parameters == [
        {
            "name": "k",
            "label": "K",
            "type": "int",
            "default": 3,
            "minimum": 1,
        }
    ]

    ga_parameters = community_analysis.get_mono_community_algorithm_parameters("ga")
    assert ga_parameters == [
        {
            "name": "population",
            "label": "Population",
            "type": "int",
            "default": 300,
            "minimum": 1,
        },
        {
            "name": "generation",
            "label": "Generation",
            "type": "int",
            "default": 30,
            "minimum": 1,
        },
        {
            "name": "r",
            "label": "R",
            "type": "float",
            "default": 1.5,
            "minimum": 0.0,
            "maximum": 1000.0,
            "decimals": 2,
            "step": 0.1,
        },
    ]

    gdmp2_parameters = community_analysis.get_mono_community_algorithm_parameters("gdmp2")
    assert gdmp2_parameters == [
        {
            "name": "min_threshold",
            "label": "Min threshold",
            "type": "float",
            "default": 0.75,
            "minimum": 0.0,
            "maximum": 1.0,
            "decimals": 3,
            "step": 0.01,
        },
    ]

    girvan_newman_parameters = community_analysis.get_mono_community_algorithm_parameters(
        "girvan_newman"
    )
    assert girvan_newman_parameters == [
        {
            "name": "level",
            "label": "Level",
            "type": "int",
            "default": 3,
            "minimum": -1,
        },
    ]

    assert community_analysis.get_mono_community_algorithm_parameters("greedy_modularity") == []
    assert community_analysis.get_mono_community_algorithm_parameters("head_tail") == [
        {
            "name": "head_tail_ratio",
            "label": "Head/tail ratio",
            "type": "float",
            "default": 0.4,
            "minimum": 0.0,
            "maximum": 1.0,
            "decimals": 3,
            "step": 0.05,
        },
    ]
    assert community_analysis.get_mono_community_algorithm_parameters("infomap") == [
        {
            "name": "num_trials",
            "label": "Num trials",
            "type": "int",
            "default": 1,
            "minimum": 1,
        },
        {
            "name": "seed",
            "label": "Seed",
            "type": "int",
            "default": 123,
            "minimum": 0,
        },
        {
            "name": "markov_time",
            "label": "Markov time",
            "type": "float",
            "default": 1.0,
            "minimum": 0.0,
            "maximum": 1000.0,
            "decimals": 3,
            "step": 0.1,
        },
        {
            "name": "preferred_number_of_modules",
            "label": "Preferred modules",
            "type": "int",
            "default": 0,
            "minimum": 0,
        },
    ]
    assert community_analysis.get_mono_community_algorithm_parameters("kcut") == [
        {
            "name": "kmax",
            "label": "K max",
            "type": "int",
            "default": 4,
            "minimum": 1,
        },
    ]
    assert community_analysis.get_mono_community_algorithm_parameters("louvain") == [
        {
            "name": "resolution",
            "label": "Resolution",
            "type": "float",
            "default": 1.0,
            "minimum": 0.0,
            "step": 0.1,
        },
        {
            "name": "randomize",
            "label": "Randomize",
            "type": "int",
            "default": 0,
            "minimum": 0,
        },
    ]
    assert community_analysis.get_mono_community_algorithm_parameters("lswl") == [
        {
            "name": "strength_type",
            "label": "Strength type",
            "type": "int",
            "default": 2,
            "minimum": 1,
            "maximum": 2,
        },
        {
            "name": "timeout",
            "label": "Timeout",
            "type": "float",
            "default": 1.0,
            "minimum": 0.0,
            "step": 0.1,
        },
    ]

    agdl_parameters = community_analysis.get_mono_community_algorithm_parameters("agdl")
    assert agdl_parameters == [
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
    ]
    assert community_analysis.get_mono_community_algorithm_parameters("unknown") == []


def test_get_mono_community_algorithm_parameters_ignores_invalid_metadata(
    monkeypatch,
) -> None:
    monkeypatch.setitem(
        community_analysis.MONO_COMMUNITY_ALGORITHM_EVALUATION,
        "agdl",
        {
            **community_analysis.MONO_COMMUNITY_ALGORITHM_EVALUATION["agdl"],
            "parameter_definitions": object(),
        },
    )
    assert community_analysis.get_mono_community_algorithm_parameters("agdl") == []


def test_prepare_mono_community_algorithm_input_adapts_graph_and_warnings() -> None:
    graph = nx.DiGraph()
    graph.add_edge("Water", "Steam", weight=2.0, elements=["Fire"])
    graph.add_edge("Steam", "Water", weight=5.0, elements=["Cloud"])

    adapted_graph, call_kwargs, warnings = (
        community_analysis.prepare_mono_community_algorithm_input(
            graph,
            "leiden",
        )
    )
    assert isinstance(adapted_graph, nx.Graph)
    assert adapted_graph["Water"]["Steam"]["weight"] == 7.0
    assert sorted(adapted_graph["Water"]["Steam"]["elements"]) == ["Cloud", "Fire"]
    assert call_kwargs == {"weights": "weight"}
    assert len(warnings) == 1

    adapted_graph, call_kwargs, warnings = (
        community_analysis.prepare_mono_community_algorithm_input(
            graph,
            "rber_pots",
        )
    )
    assert isinstance(adapted_graph, nx.Graph)
    assert "weight" not in adapted_graph["Water"]["Steam"]
    assert call_kwargs == {}
    assert len(warnings) == 2


def test_prepare_mono_community_algorithm_input_rejects_unknown_name() -> None:
    with pytest.raises(ValueError, match="Unsupported mono-community algorithm"):
        community_analysis.prepare_mono_community_algorithm_input(nx.DiGraph(), "unknown")


def test_run_mono_community_algorithm_adds_expected_weight_parameters(monkeypatch) -> None:
    calls: list[tuple[str, object, dict[str, object]]] = []

    def fake_infomap(graph, **kwargs):
        calls.append(("infomap", graph, kwargs))
        return "infomap-result"

    def fake_rb_pots(graph, **kwargs):
        calls.append(("rb_pots", graph, kwargs))
        return "rb-result"

    def fake_threshold(graph, **kwargs):
        calls.append(("threshold_clustering", graph, kwargs))
        return "threshold-result"

    def fake_agdl(graph, **kwargs):
        calls.append(("agdl", graph, kwargs))
        return "agdl-result"

    def fake_async_fluid(graph, **kwargs):
        calls.append(("async_fluid", graph, kwargs))
        return "async-fluid-result"

    def fake_bayan(graph, **kwargs):
        calls.append(("bayan", graph, kwargs))
        return "bayan-result"

    def fake_belief(graph, **kwargs):
        calls.append(("belief", graph, kwargs))
        return "belief-result"

    def fake_der(graph, **kwargs):
        calls.append(("der", graph, kwargs))
        return "der-result"

    def fake_eigenvector(graph, **kwargs):
        calls.append(("eigenvector", graph, kwargs))
        return "eigenvector-result"

    def fake_em(graph, **kwargs):
        calls.append(("em", graph, kwargs))
        return "em-result"

    def fake_ga(graph, **kwargs):
        calls.append(("ga", graph, kwargs))
        return "ga-result"

    def fake_gdmp2(graph, **kwargs):
        calls.append(("gdmp2", graph, kwargs))
        return "gdmp2-result"

    def fake_girvan_newman(graph, **kwargs):
        calls.append(("girvan_newman", graph, kwargs))
        return "girvan-newman-result"

    def fake_greedy_modularity(graph, **kwargs):
        calls.append(("greedy_modularity", graph, kwargs))
        return "greedy-modularity-result"

    def fake_head_tail(graph, **kwargs):
        calls.append(("head_tail", graph, kwargs))
        return "head-tail-result"

    def fake_cpm(graph, **kwargs):
        calls.append(("cpm", graph, kwargs))
        return "cpm-result"

    def fake_leiden(graph, **kwargs):
        calls.append(("leiden", graph, kwargs))
        return "leiden-result"

    def fake_lswl(graph, **kwargs):
        calls.append(("lswl", graph, kwargs))
        return "lswl-result"

    def fake_label_propagation(graph, **kwargs):
        calls.append(("label_propagation", graph, kwargs))
        return "label-propagation-result"

    def fake_kcut(graph, **kwargs):
        calls.append(("kcut", graph, kwargs))
        return "kcut-result"

    monkeypatch.setattr(community_analysis, "_run_direct_infomap", fake_infomap)
    monkeypatch.setattr(community_analysis.algorithms, "rb_pots", fake_rb_pots)
    monkeypatch.setattr(community_analysis.algorithms, "threshold_clustering", fake_threshold)
    monkeypatch.setattr(community_analysis.algorithms, "agdl", fake_agdl)
    monkeypatch.setattr(community_analysis.algorithms, "async_fluid", fake_async_fluid)
    monkeypatch.setattr(community_analysis.algorithms, "bayan", fake_bayan)
    monkeypatch.setattr(community_analysis.algorithms, "belief", fake_belief)
    monkeypatch.setattr(community_analysis.algorithms, "der", fake_der)
    monkeypatch.setattr(community_analysis.algorithms, "eigenvector", fake_eigenvector)
    monkeypatch.setattr(community_analysis.algorithms, "em", fake_em)
    monkeypatch.setattr(community_analysis.algorithms, "ga", fake_ga)
    monkeypatch.setattr(community_analysis.algorithms, "gdmp2", fake_gdmp2)
    monkeypatch.setattr(community_analysis.algorithms, "girvan_newman", fake_girvan_newman)
    monkeypatch.setattr(
        community_analysis.algorithms,
        "greedy_modularity",
        fake_greedy_modularity,
    )
    monkeypatch.setattr(community_analysis.algorithms, "head_tail", fake_head_tail)
    monkeypatch.setattr(community_analysis.algorithms, "kcut", fake_kcut)
    monkeypatch.setattr(community_analysis.algorithms, "cpm", fake_cpm)
    monkeypatch.setattr(community_analysis.algorithms, "leiden", fake_leiden)
    monkeypatch.setattr(community_analysis.algorithms, "lswl", fake_lswl)
    monkeypatch.setattr(
        community_analysis.algorithms,
        "label_propagation",
        fake_label_propagation,
    )

    graph = nx.DiGraph()
    graph.add_edge("Water", "Steam", weight=2.0, elements=["Fire"])

    assert community_analysis.run_mono_community_algorithm(graph, "infomap") == "infomap-result"
    assert community_analysis.run_mono_community_algorithm(graph, "rb_pots") == "rb-result"
    assert (
        community_analysis.run_mono_community_algorithm(
            graph,
            "threshold_clustering",
            threshold_function=lambda edge: edge,
        )
        == "threshold-result"
    )
    assert community_analysis.run_mono_community_algorithm(graph, "agdl") == "agdl-result"
    assert (
        community_analysis.run_mono_community_algorithm(graph, "async_fluid")
        == "async-fluid-result"
    )
    assert community_analysis.run_mono_community_algorithm(graph, "bayan") == "bayan-result"
    assert community_analysis.run_mono_community_algorithm(graph, "belief") == "belief-result"
    assert community_analysis.run_mono_community_algorithm(graph, "der") == "der-result"
    assert (
        community_analysis.run_mono_community_algorithm(graph, "eigenvector")
        == "eigenvector-result"
    )
    assert community_analysis.run_mono_community_algorithm(graph, "em") == "em-result"
    assert community_analysis.run_mono_community_algorithm(graph, "ga") == "ga-result"
    assert community_analysis.run_mono_community_algorithm(graph, "gdmp2") == "gdmp2-result"
    assert (
        community_analysis.run_mono_community_algorithm(graph, "girvan_newman")
        == "girvan-newman-result"
    )
    assert (
        community_analysis.run_mono_community_algorithm(graph, "greedy_modularity")
        == "greedy-modularity-result"
    )
    assert community_analysis.run_mono_community_algorithm(graph, "head_tail") == "head-tail-result"
    assert community_analysis.run_mono_community_algorithm(graph, "kcut") == "kcut-result"
    assert community_analysis.run_mono_community_algorithm(graph, "cpm") == "cpm-result"
    assert community_analysis.run_mono_community_algorithm(graph, "leiden") == "leiden-result"
    assert (
        community_analysis.run_mono_community_algorithm(graph, "lswl", query_node="Water")
        == "lswl-result"
    )
    assert (
        community_analysis.run_mono_community_algorithm(
            graph,
            "label_propagation_cordasco_gargano",
        )
        == "label-propagation-result"
    )

    assert calls[0][0] == "infomap"
    assert isinstance(calls[0][1], nx.DiGraph)
    assert calls[0][2] == {
        "num_trials": 1,
        "seed": 123,
        "markov_time": 1.0,
        "preferred_number_of_modules": 0,
    }
    assert calls[1][2] == {"weights": "weight"}
    assert "threshold_function" in calls[2][2]
    assert calls[3][2] == {"number_communities": 3, "kc": 2}
    assert calls[4][0] == "async_fluid"
    assert isinstance(calls[4][1], nx.Graph)
    assert calls[4][2] == {"k": 2}
    assert calls[5][0] == "bayan"
    assert isinstance(calls[5][1], nx.Graph)
    assert calls[5][2] == {}
    assert calls[6][0] == "belief"
    assert isinstance(calls[6][1], nx.Graph)
    assert calls[6][2] == {
        "max_it": 100,
        "eps": 0.0001,
        "reruns_if_not_conv": 5,
        "threshold": 0.005,
        "q_max": 7,
    }
    assert calls[7][0] == "der"
    assert isinstance(calls[7][1], nx.Graph)
    assert calls[7][2] == {
        "walk_len": 3,
        "threshold": 0.00001,
        "iter_bound": 50,
    }
    assert calls[8][0] == "eigenvector"
    assert isinstance(calls[8][1], nx.Graph)
    assert calls[8][2] == {}
    assert calls[9][0] == "em"
    assert isinstance(calls[9][1], nx.Graph)
    assert calls[9][2] == {"k": 3}
    assert calls[10][0] == "ga"
    assert isinstance(calls[10][1], nx.Graph)
    assert calls[10][2] == {
        "population": 300,
        "generation": 30,
        "r": 1.5,
    }
    assert calls[11][0] == "gdmp2"
    assert isinstance(calls[11][1], nx.Graph)
    assert calls[11][2] == {
        "min_threshold": 0.75,
    }
    assert calls[12][0] == "girvan_newman"
    assert isinstance(calls[12][1], nx.Graph)
    assert calls[12][2] == {"level": 3}
    assert calls[13][0] == "greedy_modularity"
    assert isinstance(calls[13][1], nx.Graph)
    assert calls[13][2] == {"weight": "weight"}
    assert calls[14][0] == "head_tail"
    assert isinstance(calls[14][1], nx.Graph)
    assert calls[14][2] == {"head_tail_ratio": 0.4}
    assert calls[15][0] == "kcut"
    assert isinstance(calls[15][1], nx.Graph)
    assert calls[15][2] == {"kmax": 4}
    assert calls[16][0] == "cpm"
    assert isinstance(calls[16][1], nx.Graph)
    assert calls[16][2] == {
        "resolution_parameter": 1.0,
        "weights": "weight",
    }
    assert isinstance(calls[17][1], nx.Graph)
    assert calls[17][2] == {"weights": "weight"}
    assert calls[18][0] == "lswl"
    assert isinstance(calls[18][1], nx.Graph)
    assert calls[18][2] == {"query_node": "Water", "strength_type": 2, "timeout": 1.0, "online": True}
    assert calls[19][0] == "label_propagation"
    assert isinstance(calls[19][1], nx.Graph)
    assert calls[19][2] == {}


def test_run_mono_community_algorithm_allows_overriding_default_parameters(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_agdl(graph, **kwargs):
        calls.append(kwargs)
        return "agdl-result"

    monkeypatch.setattr(community_analysis.algorithms, "agdl", fake_agdl)

    graph = nx.DiGraph()
    graph.add_edge("Water", "Steam", weight=2.0, elements=["Fire"])

    assert (
        community_analysis.run_mono_community_algorithm(
            graph,
            "agdl",
            number_communities=5,
        )
        == "agdl-result"
    )
    assert calls == [{"number_communities": 5, "kc": 2}]


def test_run_mono_community_algorithm_reframes_lswl_empty_community_crash(monkeypatch) -> None:
    def fake_lswl(graph, **kwargs):
        raise IndexError("list index out of range")

    monkeypatch.setattr(community_analysis.algorithms, "lswl", fake_lswl)

    graph = nx.DiGraph()
    graph.add_edge("Water", "Steam", weight=2.0, elements=["Fire"])

    with pytest.raises(RuntimeError) as excinfo:
        community_analysis.run_mono_community_algorithm(
            graph,
            "lswl",
            query_node="Water",
            timeout=5.0,
        )

    message = str(excinfo.value)
    assert "did not return a community" in message
    assert "query_node='Water'" in message
    assert "timeout=5.0" in message


def test_run_mono_community_algorithm_reraises_other_index_errors(monkeypatch) -> None:
    def fake_kcut(graph, **kwargs):
        raise IndexError("list index out of range")

    monkeypatch.setattr(community_analysis.algorithms, "kcut", fake_kcut)

    graph = nx.DiGraph()
    graph.add_edge("Water", "Steam", weight=2.0, elements=["Fire"])

    with pytest.raises(IndexError, match="list index out of range"):
        community_analysis.run_mono_community_algorithm(graph, "kcut")


def test_run_direct_infomap_uses_installed_package() -> None:
    graph = nx.DiGraph()
    graph.add_edge("Water", "Steam", weight=2.0)
    graph.add_edge("Steam", "Cloud", weight=1.0)

    result = community_analysis._run_direct_infomap(graph, flags="--silent")

    assert result.method_name == "Infomap"
    assert result.method_parameters == {
        "legacy_flags": "--silent",
        "num_trials": 1,
        "seed": 123,
        "markov_time": 1.0,
    }
    assert result.communities


def test_run_direct_infomap_supports_unweighted_edges() -> None:
    graph = nx.Graph()
    graph.add_edge("Water", "Steam")
    graph.add_edge("Steam", "Cloud")

    result = community_analysis._run_direct_infomap(graph)

    assert result.method_name == "Infomap"
    assert result.method_parameters == {
        "num_trials": 1,
        "seed": 123,
        "markov_time": 1.0,
    }
    assert result.communities


def test_run_direct_infomap_supports_api_parameters() -> None:
    graph = nx.DiGraph()
    graph.add_edge("Water", "Steam", weight=2.0)
    graph.add_edge("Steam", "Cloud", weight=1.0)

    result = community_analysis._run_direct_infomap(
        graph,
        num_trials=3,
        seed=999,
        markov_time=2.5,
        preferred_number_of_modules=7,
    )

    assert result.method_parameters == {
        "num_trials": 3,
        "seed": 999,
        "markov_time": 2.5,
        "preferred_number_of_modules": 7,
    }


def test_summarize_mono_community_result_and_parameter_normalization() -> None:
    result = SimpleNamespace(
        communities=[{"Steam", "Water"}, {"Earth"}],
        method_name="Infomap",
        method_parameters={"num_trials": 1, "seed": 123, "markov_time": 1.0},
    )

    summary = community_analysis.summarize_mono_community_result(result)

    assert summary["communities"] == [["Steam", "Water"], ["Earth"]]
    assert summary["community_count"] == 2
    assert summary["community_sizes"] == [2, 1]
    assert summary["min_size"] == 1
    assert summary["max_size"] == 2
    assert summary["average_size"] == 1.5
    assert summary["node_to_community"] == {"Steam": 0, "Water": 0, "Earth": 1}
    assert summary["method_name"] == "Infomap"
    assert summary["parameters"] == {"num_trials": 1, "seed": 123, "markov_time": 1.0}

    empty_summary = community_analysis.summarize_mono_community_result(
        SimpleNamespace(communities=[], method_name=None, method_parameters=object())
    )
    assert empty_summary["community_count"] == 0
    assert empty_summary["community_sizes"] == []
    assert empty_summary["min_size"] == 0
    assert empty_summary["max_size"] == 0
    assert empty_summary["average_size"] == 0.0
    assert empty_summary["node_to_community"] == {}
    assert empty_summary["method_name"] is None
    assert empty_summary["parameters"] == {}
