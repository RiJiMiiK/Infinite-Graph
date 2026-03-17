from __future__ import annotations

from src.infinite_graph import gui


def test_window_compute_communities_louvain_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("louvain")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "Louvain estimate warning.",
    )
    monkeypatch.setattr(
        gui.QMessageBox,
        "warning",
        lambda *args: gui.QMessageBox.Cancel,
    )
    monkeypatch.setattr(
        gui,
        "run_mono_community_algorithm",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    window._compute_communities()

    assert calls == []
    assert window.community_summary_label.text() == "No community analysis has been run yet."
    window.close()
