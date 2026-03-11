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

    algorithms = community_analysis.get_mono_community_algorithms()
    visible_keys = [item["key"] for item in algorithms]
    assert "label_propagation_raghavan" not in visible_keys
    assert "sbm_dl" not in visible_keys
    assert "sbm_dl_nested" not in visible_keys
    assert "ricci_community" not in visible_keys
    assert next(item for item in algorithms if item["key"] == "infomap")[
        "requires_graph_adaptation"
    ] is False
    assert next(item for item in algorithms if item["key"] == "leiden")[
        "requires_graph_adaptation"
    ] is True
    assert next(item for item in algorithms if item["key"] == "rber_pots")[
        "requires_graph_adaptation"
    ] is True
    assert community_analysis.get_default_mono_community_algorithm() == "infomap"
    assert community_analysis.uses_directed_community_graph() is True
    assert community_analysis.uses_edge_weights_only() is True
    assert community_analysis.ignores_node_weights() is True


def test_algorithm_visibility_rules() -> None:
    assert community_analysis._is_mono_community_algorithm_visible("label_propagation_raghavan") is False
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
    assert community_analysis.get_mono_community_algorithm_parameters("infomap") == []
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


def test_get_mono_community_algorithm_warning() -> None:
    assert community_analysis.get_mono_community_algorithm_warning("infomap") is None
    agdl_warning = community_analysis.get_mono_community_algorithm_warning("agdl")
    assert agdl_warning is not None
    assert "experimental in this environment" in agdl_warning
    assert "karate_club_graph()" in agdl_warning
    leiden_warning = community_analysis.get_mono_community_algorithm_warning("leiden")
    assert leiden_warning is not None
    assert "does not support directed graphs directly" in leiden_warning
    rber_warning = community_analysis.get_mono_community_algorithm_warning("rber_pots")
    assert rber_warning is not None
    assert "does not support edge weights directly" in rber_warning
    assert community_analysis.get_mono_community_algorithm_warning("unknown") is None


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

    def fake_async_fluid(graph, **kwargs):
        calls.append(("async_fluid", graph, kwargs))
        return "async-fluid-result"

    def fake_bayan(graph, **kwargs):
        calls.append(("bayan", graph, kwargs))
        return "bayan-result"

    def fake_leiden(graph, **kwargs):
        calls.append(("leiden", graph, kwargs))
        return "leiden-result"

    def fake_label_propagation(graph, **kwargs):
        calls.append(("label_propagation", graph, kwargs))
        return "label-propagation-result"

    monkeypatch.setattr(community_analysis.algorithms, "infomap", fake_infomap)
    monkeypatch.setattr(community_analysis.algorithms, "rb_pots", fake_rb_pots)
    monkeypatch.setattr(community_analysis.algorithms, "threshold_clustering", fake_threshold)
    monkeypatch.setattr(community_analysis.algorithms, "agdl", fake_agdl)
    monkeypatch.setattr(community_analysis.algorithms, "async_fluid", fake_async_fluid)
    monkeypatch.setattr(community_analysis.algorithms, "bayan", fake_bayan)
    monkeypatch.setattr(community_analysis.algorithms, "leiden", fake_leiden)
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
    assert community_analysis.run_mono_community_algorithm(graph, "leiden") == "leiden-result"
    assert (
        community_analysis.run_mono_community_algorithm(
            graph,
            "label_propagation_cordasco_gargano",
        )
        == "label-propagation-result"
    )

    assert calls[0][0] == "infomap"
    assert isinstance(calls[0][1], nx.DiGraph)
    assert calls[0][2] == {"flags": "--directed --silent -w"}
    assert calls[1][2] == {"weights": "weight"}
    assert "threshold_function" in calls[2][2]
    assert calls[3][2] == {"number_communities": 3, "kc": 2}
    assert calls[4][0] == "async_fluid"
    assert isinstance(calls[4][1], nx.Graph)
    assert calls[4][2] == {"k": 2}
    assert calls[5][0] == "bayan"
    assert isinstance(calls[5][1], nx.Graph)
    assert calls[5][2] == {}
    assert isinstance(calls[6][1], nx.Graph)
    assert calls[6][2] == {"weights": "weight"}
    assert calls[7][0] == "label_propagation"
    assert isinstance(calls[7][1], nx.Graph)
    assert calls[7][2] == {}


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
