from __future__ import annotations

from types import SimpleNamespace

from PySide6.QtWidgets import QDoubleSpinBox

from src.infinite_graph import gui


def test_window_lswl_parameters_are_visible(qapp) -> None:
    window = gui.InfiniteGraphWindow()

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("lswl")
    )

    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {"strength_type", "timeout"}
    assert isinstance(window._community_parameter_inputs["timeout"], QDoubleSpinBox)
    window.close()


def test_window_compute_communities_lswl_requires_selected_node(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("lswl")
    )

    messages = []
    monkeypatch.setattr(
        gui.QMessageBox,
        "warning",
        lambda *args: messages.append(args[2]) or gui.QMessageBox.Ok,
    )
    monkeypatch.setattr(
        gui,
        "run_mono_community_algorithm",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("should not run")),
    )

    window._compute_communities()

    assert messages == ["LSWL requires a selected graph node. Select a node in the graph view first."]
    window.close()


def test_window_compute_communities_supports_lswl(qapp, sample_result, monkeypatch) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.graph_view._selected_node_id = "Water"
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("lswl")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="LSWL",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "LSWL",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["strength_type"].setValue(1)
    window._community_parameter_inputs["timeout"].setValue(2.5)
    window._compute_communities()

    assert calls == [
        (
            sample_result["community_graph"],
            "lswl",
            {"strength_type": 1, "timeout": 2.5, "query_node": "Water"},
        )
    ]
    assert "Algorithm: LSWL" in window.community_summary_label.text()
    assert "strength_type=1" in window.community_summary_label.text()
    assert "timeout=2.5" in window.community_summary_label.text()
    assert "query_node=Water" in window.community_summary_label.text()
    window.close()
