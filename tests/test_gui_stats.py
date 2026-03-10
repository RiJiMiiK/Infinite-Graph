from __future__ import annotations

import pytest

from src.infinite_graph import gui


@pytest.fixture()
def sample_result() -> dict[str, object]:
    return {
        "elements": ["Water", "Fire", "Wind", "Earth", "Steam"],
        "recipes": [{"left": "Water", "right": "Fire", "result": "Steam"}],
        "load_warnings": [],
        "ignored_element_entries": 0,
        "ignored_item_entries": 0,
        "ignored_recipe_entries": 0,
        "graph_nodes": [],
        "graph_edges": [],
        "node_weights": {"Water": 0, "Fire": 0, "Wind": 0, "Earth": 0, "Steam": 1},
        "known_pairs": {("Fire", "Water")},
        "discarded_pairs": {("Earth", "Wind")},
        "done_pairs": set(),
        "skipped_pairs": set(),
        "statistics": {
            "recipe_counts_by_result_weight": [(1, 1)],
            "node_counts_by_weight": [(0, 2)],
            "missing_counts_by_result_weight": [(1, 4)],
        },
        "missing": [("Earth", "Water"), ("Earth", "Earth")],
        "missing_limit": 1000,
        "focus_element": None,
    }


def test_stats_canvas_updates_series(qapp) -> None:
    canvas = gui.StatsCanvas()
    canvas.update_series([(1, 2)], [(0, 4)])
    assert len(canvas.axis.lines) == 2
    assert canvas.axis.get_title() == "Craft progression overview"
    assert canvas.axis.get_xlabel() == "Weight"
    assert canvas.axis.get_ylabel() == "Count"
    assert canvas.axis.get_legend() is not None
    canvas.update_series([], [])
    assert len(canvas.axis.lines) == 0


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
