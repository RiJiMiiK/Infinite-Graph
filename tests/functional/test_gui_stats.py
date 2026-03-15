from __future__ import annotations

from src.infinite_graph import gui

def test_window_update_missing_statistics_adds_new_weight_bucket(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    sample_result["statistics"]["missing_counts_by_result_weight"] = []
    sample_result["node_weights"] = {"Water": 0, "Steam": 1}
    window._current_result = sample_result
    window._update_missing_statistics_for_pair(("Water", "Steam"), 1)
    assert sample_result["statistics"]["missing_counts_by_result_weight"] == [(2, 1)]
    assert window.missing_weight_list.count() == 1
    window.close()


def test_window_update_missing_statistics_preserves_other_buckets(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    sample_result["statistics"]["missing_counts_by_result_weight"] = [(1, 2), (2, 3), (3, 4)]
    sample_result["node_weights"] = {"Water": 0, "Steam": 1}
    window._current_result = sample_result
    window._update_missing_statistics_for_pair(("Water", "Steam"), -1)
    assert sample_result["statistics"]["missing_counts_by_result_weight"] == [(1, 2), (2, 2), (3, 4)]
    window.close()
