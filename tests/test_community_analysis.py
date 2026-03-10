from __future__ import annotations

from types import SimpleNamespace

import networkx as nx
import pytest

from src.infinite_graph import community_analysis


def test_build_cdlib_graph_preserves_direction_and_edge_weights() -> None:
    graph = community_analysis.build_cdlib_graph(
        [
            {"id": "Water", "label": "Water"},
            {"id": "Steam", "label": "Steam"},
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
    assert "weight" not in graph.nodes["Water"]
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


def test_get_mono_community_algorithms_and_default() -> None:
    algorithms = community_analysis.get_mono_community_algorithms()
    assert [item["key"] for item in algorithms] == [
        "infomap",
        "rb_pots",
        "rber_pots",
        "threshold_clustering",
    ]
    assert algorithms[0]["label"] == "Infomap"
    assert community_analysis.get_default_mono_community_algorithm() == "infomap"
    assert community_analysis.uses_directed_community_graph() is True
    assert community_analysis.uses_edge_weights_only() is True
    assert community_analysis.ignores_node_weights() is True


def test_run_mono_community_algorithm_rejects_unknown_name() -> None:
    with pytest.raises(ValueError, match="Unsupported mono-community algorithm"):
        community_analysis.run_mono_community_algorithm(nx.DiGraph(), "unknown")


def test_run_mono_community_algorithm_adds_expected_weight_parameters(monkeypatch) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    def fake_infomap(graph, **kwargs):
        calls.append(("infomap", kwargs))
        return "infomap-result"

    def fake_rb_pots(graph, **kwargs):
        calls.append(("rb_pots", kwargs))
        return "rb-result"

    def fake_threshold(graph, **kwargs):
        calls.append(("threshold_clustering", kwargs))
        return "threshold-result"

    monkeypatch.setattr(community_analysis.algorithms, "infomap", fake_infomap)
    monkeypatch.setattr(community_analysis.algorithms, "rb_pots", fake_rb_pots)
    monkeypatch.setattr(
        community_analysis.algorithms,
        "threshold_clustering",
        fake_threshold,
    )

    graph = nx.DiGraph()
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
    community_analysis.run_mono_community_algorithm(graph, "rb_pots", weights="custom")

    assert calls[0] == ("infomap", {"flags": "--directed --silent -w"})
    assert calls[1] == ("rb_pots", {"weights": "weight"})
    assert "threshold_function" in calls[2][1]
    assert "weights" not in calls[2][1]
    assert calls[3] == ("rb_pots", {"weights": "custom"})


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
