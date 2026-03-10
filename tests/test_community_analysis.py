from __future__ import annotations

from types import SimpleNamespace

import networkx as nx
import pytest

from src.infinite_graph import community_analysis


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
        "infomap",
        "rb_pots",
        "threshold_clustering",
        "agdl",
        "rber_pots",
        "leiden",
        "louvain",
        "pycombo",
        "walktrap",
        "greedy_modularity",
        "label_propagation",
    ]
    assert "directed weighted graph as-is" in evaluation[0]["compatibility_note"]
    assert "undirected unweighted view" in evaluation[4]["compatibility_note"]

    algorithms = community_analysis.get_mono_community_algorithms()
    assert [item["key"] for item in algorithms] == [
        "infomap",
        "rb_pots",
        "threshold_clustering",
        "agdl",
        "rber_pots",
        "leiden",
        "louvain",
        "pycombo",
        "walktrap",
        "greedy_modularity",
        "label_propagation",
    ]
    assert algorithms[0]["requires_graph_adaptation"] is False
    assert algorithms[4]["requires_graph_adaptation"] is True
    assert community_analysis.get_default_mono_community_algorithm() == "infomap"
    assert community_analysis.uses_directed_community_graph() is True
    assert community_analysis.uses_edge_weights_only() is True
    assert community_analysis.ignores_node_weights() is True


def test_get_mono_community_algorithm_warning() -> None:
    assert community_analysis.get_mono_community_algorithm_warning("infomap") is None
    leiden_warning = community_analysis.get_mono_community_algorithm_warning("leiden")
    assert leiden_warning is not None
    assert "does not support directed graphs directly" in leiden_warning
    rber_warning = community_analysis.get_mono_community_algorithm_warning("rber_pots")
    assert rber_warning is not None
    assert "does not support edge weights directly" in rber_warning
    assert community_analysis.get_mono_community_algorithm_warning("unknown") is None


def test_prepare_mono_community_algorithm_input_adapts_graph_and_warnings() -> None:
    graph = nx.DiGraph()
    graph.add_edge("Water", "Steam", weight=2.0, elements=["Fire"])
    graph.add_edge("Steam", "Water", weight=5.0, elements=["Cloud"])

    adapted_graph, call_kwargs, warnings = community_analysis.prepare_mono_community_algorithm_input(
        graph,
        "leiden",
    )
    assert isinstance(adapted_graph, nx.Graph)
    assert adapted_graph["Water"]["Steam"]["weight"] == 7.0
    assert sorted(adapted_graph["Water"]["Steam"]["elements"]) == ["Cloud", "Fire"]
    assert call_kwargs == {"weights": "weight"}
    assert len(warnings) == 1

    adapted_graph, call_kwargs, warnings = community_analysis.prepare_mono_community_algorithm_input(
        graph,
        "rber_pots",
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

    def fake_leiden(graph, **kwargs):
        calls.append(("leiden", graph, kwargs))
        return "leiden-result"

    monkeypatch.setattr(community_analysis.algorithms, "infomap", fake_infomap)
    monkeypatch.setattr(community_analysis.algorithms, "rb_pots", fake_rb_pots)
    monkeypatch.setattr(community_analysis.algorithms, "threshold_clustering", fake_threshold)
    monkeypatch.setattr(community_analysis.algorithms, "agdl", fake_agdl)
    monkeypatch.setattr(community_analysis.algorithms, "leiden", fake_leiden)

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
    assert community_analysis.run_mono_community_algorithm(graph, "leiden") == "leiden-result"

    assert calls[0][0] == "infomap"
    assert isinstance(calls[0][1], nx.DiGraph)
    assert calls[0][2] == {"flags": "--directed --silent -w"}
    assert calls[1][2] == {"weights": "weight"}
    assert "threshold_function" in calls[2][2]
    assert calls[3][2] == {}
    assert isinstance(calls[4][1], nx.Graph)
    assert calls[4][2] == {"weights": "weight"}


def test_summarize_mono_community_result_and_parameter_normalization() -> None:
    result = SimpleNamespace(
        communities=[{"Steam", "Water"}, {"Earth"}],
        method_name="Infomap",
        method_parameters={"flags": "--directed --silent -w"},
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
    assert summary["parameters"] == {"flags": "--directed --silent -w"}

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
