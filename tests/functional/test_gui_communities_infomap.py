from __future__ import annotations

from types import SimpleNamespace

from PySide6.QtWidgets import QDoubleSpinBox

from src.infinite_graph import gui


def test_window_shows_infomap_parameters(qapp) -> None:
    window = gui.InfiniteGraphWindow()
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("infomap")
    )

    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {
        "num_trials",
        "seed",
        "markov_time",
        "preferred_number_of_modules",
    }
    assert isinstance(window._community_parameter_inputs["markov_time"], QDoubleSpinBox)
    window.close()


def test_window_compute_communities_supports_infomap(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("infomap")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="Infomap",
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
            "method_name": "Infomap",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["num_trials"].setValue(3)
    window._community_parameter_inputs["seed"].setValue(999)
    window._community_parameter_inputs["markov_time"].setValue(2.5)
    window._community_parameter_inputs["preferred_number_of_modules"].setValue(7)
    window._compute_communities()

    assert calls == [
        (
            sample_result["community_graph"],
            "infomap",
            {
                "num_trials": 3,
                "seed": 999,
                "markov_time": 2.5,
                "preferred_number_of_modules": 7,
            },
        )
    ]
    assert "Algorithm: Infomap" in window.community_summary_label.text()
    assert "Method name: Infomap" in window.community_summary_label.text()
    assert "Detected communities: 2" in window.community_summary_label.text()
    assert "Parameters:" in window.community_summary_label.text()
    assert "num_trials=3" in window.community_summary_label.text()
    assert "seed=999" in window.community_summary_label.text()
    assert "markov_time=2.5" in window.community_summary_label.text()
    assert "preferred_number_of_modules=7" in window.community_summary_label.text()
    window.close()
