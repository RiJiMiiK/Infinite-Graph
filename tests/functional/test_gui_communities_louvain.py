from __future__ import annotations

from types import SimpleNamespace

from PySide6.QtWidgets import QDoubleSpinBox

from src.infinite_graph import gui


def test_window_louvain_parameters_are_visible(qapp) -> None:
    window = gui.InfiniteGraphWindow()

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("louvain")
    )

    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {"resolution", "randomize"}
    assert isinstance(window._community_parameter_inputs["resolution"], QDoubleSpinBox)
    window.close()


def test_window_compute_communities_supports_louvain(qapp, sample_result, monkeypatch) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("louvain")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="Louvain",
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
            "method_name": "Louvain",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["resolution"].setValue(1.5)
    window._community_parameter_inputs["randomize"].setValue(7)
    window._compute_communities()

    assert calls == [
        (
            sample_result["community_graph"],
            "louvain",
            {"resolution": 1.5, "randomize": 7},
        )
    ]
    assert "Algorithm: Louvain" in window.community_summary_label.text()
    assert "Detected communities: 2" in window.community_summary_label.text()
    assert "resolution=1.5" in window.community_summary_label.text()
    assert "randomize=7" in window.community_summary_label.text()
    window.close()
