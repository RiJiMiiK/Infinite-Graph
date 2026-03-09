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
        "statistics": {"missing_counts_by_result_weight": []},
        "missing": [],
        "missing_limit": 1000,
        "focus_element": None,
    }


def test_window_live_element_validation(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()

    window.element1_edit.setText("water")
    window._validate_combination_inputs()
    assert window.element1_edit.styleSheet() == ""
    assert window.element1_edit.toolTip() == ""

    window._current_result = sample_result
    window.element1_edit.setText("water")
    window.element2_edit.setText("unknown")
    window._validate_combination_inputs()

    assert "#16a34a" in window.element1_edit.styleSheet()
    assert "Water" in window.element1_edit.toolTip()
    assert "#dc2626" in window.element2_edit.styleSheet()
    assert "introuvable" in window.element2_edit.toolTip()

    window.element1_edit.clear()
    window._validate_combination_inputs()
    assert window.element1_edit.styleSheet() == ""
    assert window.element1_edit.toolTip() == ""
    window.close()
