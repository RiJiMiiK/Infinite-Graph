from __future__ import annotations

from pathlib import Path

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
            "recipe_counts_by_result_weight": [],
            "node_counts_by_weight": [],
            "missing_counts_by_result_weight": [],
        },
        "missing": [],
        "missing_limit": 1000,
        "focus_element": None,
    }


def test_window_remove_selected_discarded_combination(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    infos = []
    removed = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(gui, "remove_discarded_pair", lambda path, pair: removed.append((path, pair)))

    window._remove_selected_discarded_combination()
    window._restore_discarded_pair(("Earth", "Wind"))
    window._current_result = sample_result
    window._current_save_path = Path("save.json")
    window._refresh_discarded_table()

    window._remove_selected_discarded_combination()
    assert "Selectionne d'abord" in infos[-1][-1]

    sample_result["discarded_pairs"].clear()
    window.discarded_model.update_rows([["Earth", "Wind"]])
    window.discarded_table.selectRow(0)
    window._remove_selected_discarded_combination()
    assert "n'est pas discardee" in infos[-1][-1]

    sample_result["discarded_pairs"].add(("Earth", "Wind"))
    window._refresh_discarded_table()
    window.discarded_table.selectRow(0)
    window._remove_selected_discarded_combination()
    assert removed == [(Path("save.json"), ("Earth", "Wind"))]
    assert ("Earth", "Wind") not in sample_result["discarded_pairs"]
    assert ("Earth", "Wind") in sample_result["missing"]
    assert window.discarded_model.rowCount() == 0
    window.close()


def test_window_reset_discarded_combinations(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    infos = []
    cleared = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(
        gui.QMessageBox,
        "question",
        lambda *args: gui.QMessageBox.StandardButton.No,
    )
    monkeypatch.setattr(gui, "clear_discarded_pairs", lambda path: cleared.append(path))

    window._reset_discarded_combinations()
    window._current_result = sample_result
    window._current_save_path = Path("save.json")
    window._refresh_discarded_table()
    sample_result["statistics"]["missing_counts_by_result_weight"] = []

    window._reset_discarded_combinations()
    assert cleared == []
    assert ("Earth", "Wind") in sample_result["discarded_pairs"]

    monkeypatch.setattr(
        gui.QMessageBox,
        "question",
        lambda *args: gui.QMessageBox.StandardButton.Yes,
    )
    window._reset_discarded_combinations()
    assert cleared == [Path("save.json")]
    assert sample_result["discarded_pairs"] == set()
    assert ("Earth", "Wind") in sample_result["missing"]
    assert window.discarded_model.rowCount() == 0

    window._reset_discarded_combinations()
    assert "Aucune combinaison discardee" in infos[-1][-1]
    window.close()
