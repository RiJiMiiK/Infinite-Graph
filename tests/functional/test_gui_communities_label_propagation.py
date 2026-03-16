from __future__ import annotations

from types import SimpleNamespace

from src.infinite_graph import gui


def test_window_compute_communities_supports_label_propagation_cordasco_gargano(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("label_propagation_cordasco_gargano")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="Label Propagation",
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
            "method_name": "Label Propagation",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._compute_communities()

    assert calls == [
        (sample_result["community_graph"], "label_propagation_cordasco_gargano", {})
    ]
    assert "Algorithm: Label Propagation Cordasco-Gargano" in window.community_summary_label.text()
    assert "Method name: Label Propagation" in window.community_summary_label.text()
    assert "Detected communities: 2" in window.community_summary_label.text()
    assert "Parameters:" not in window.community_summary_label.text()
    window.close()
