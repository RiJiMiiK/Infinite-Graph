from __future__ import annotations

import pytest

from src.infinite_graph import gui
from src.infinite_graph import gui_window_combinations


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


def test_window_live_element_validation(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    assert "aucune save chargee" in window.candidate_count_label.text()
    assert "QGroupBox" in window.styleSheet()
    assert window.generate_button.objectName() == "primaryButton"
    assert window.discard_button.objectName() == "dangerButton"

    window.element1_edit.setText("water")
    window._validate_combination_inputs()
    assert window.element1_edit.styleSheet() == ""
    assert window.element1_edit.toolTip() == ""
    assert "charge une save" in window.candidate_status_label.text()
    assert "water + ?" in window.current_candidate_details.toPlainText()

    window._current_result = sample_result
    window.element1_edit.setText("water")
    window.element2_edit.setText("unknown")
    window._validate_combination_inputs()

    assert "#16a34a" in window.element1_edit.styleSheet()
    assert "Water" in window.element1_edit.toolTip()
    assert "#dc2626" in window.element2_edit.styleSheet()
    assert "introuvable" in window.element2_edit.toolTip()
    assert "introuvable" in window.candidate_status_label.text()
    assert "Origine : manuelle" in window.current_candidate_details.toPlainText()

    window.element1_edit.clear()
    window._validate_combination_inputs()
    assert window.element1_edit.styleSheet() == ""
    assert window.element1_edit.toolTip() == ""
    assert "saisis ou genere" in window.candidate_status_label.text()
    window.close()


def test_window_summary_panel_toggle_and_generation_state(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    errors = []
    monkeypatch.setattr(gui.QMessageBox, "critical", lambda *args: errors.append(args))
    assert window.summary_panel.isHidden() is True
    assert window.current_candidate_details.isHidden() is True
    assert window.history_panel.isHidden() is True
    assert window.summary_toggle_button.text() == "Afficher details"
    assert window.current_candidate_toggle_button.text() == "Afficher details candidat"
    assert window.history_toggle_button.text() == "Afficher historique"

    window._toggle_candidate_details()
    assert window.current_candidate_details.isHidden() is False
    assert window.current_candidate_toggle_button.text() == "Masquer details candidat"

    window._toggle_history_panel()
    assert window.history_panel.isHidden() is False
    assert window.history_toggle_button.text() == "Masquer historique"

    window._toggle_summary_panel()
    assert window.summary_panel.isHidden() is False
    assert window.summary_toggle_button.text() == "Masquer details"

    window._toggle_summary_panel()
    assert window.summary_panel.isHidden() is True
    assert window.summary_toggle_button.text() == "Afficher details"

    window.input_edit.setText("save.json")
    window._on_generation_finished(
        sample_result,
        {"positions": [], "adj": [], "sizes": [], "brushes": [], "labels": []},
        1.0,
    )
    assert window.candidate_count_label.text().endswith("0")
    assert window.summary_panel.isHidden() is False
    assert window.summary_toggle_button.text() == "Masquer details"

    window._on_generation_failed("boom")
    assert "aucune save chargee" in window.candidate_count_label.text()
    assert window.summary_panel.isHidden() is False
    assert window.summary_toggle_button.text() == "Masquer details"
    assert errors
    window.close()


def test_window_refresh_discarded_table_without_result(qapp) -> None:
    window = gui.InfiniteGraphWindow()
    window.discarded_model.update_rows([["Earth", "Wind"]])
    window._refresh_discarded_table()
    assert window.discarded_model.rowCount() == 0
    window.close()


def test_window_indexed_candidate_helpers(qapp, sample_result, monkeypatch) -> None:
    window = gui.InfiniteGraphWindow()

    assert window._indexed_candidate_allowed(("Earth", "Water"), include_skipped=False) is False
    assert window._pick_random_indexed_candidate(include_skipped=False) is None
    assert window._pick_cheapest_indexed_candidate(include_skipped=False) is None

    sample_result["candidate_pairs"] = [
        ("Earth", "Wind"),
        ("Earth", "Earth"),
        ("Earth", "Water"),
    ]
    sample_result["candidate_pairs_by_weight"] = [
        ("Fire", "Water"),
        ("Earth", "Wind"),
        ("Earth", "Earth"),
        ("Earth", "Water"),
    ]
    sample_result["done_pairs"] = {("Earth", "Earth")}
    sample_result["skipped_pairs"] = {("Earth", "Water")}
    window._current_result = sample_result

    assert window._indexed_candidate_allowed(("Fire", "Water"), include_skipped=False) is False
    assert window._indexed_candidate_allowed(("Earth", "Wind"), include_skipped=False) is False
    assert window._indexed_candidate_allowed(("Earth", "Earth"), include_skipped=False) is False
    assert window._indexed_candidate_allowed(("Earth", "Water"), include_skipped=False) is False
    assert window._indexed_candidate_allowed(("Earth", "Water"), include_skipped=True) is True

    monkeypatch.setattr(gui_window_combinations.random, "choice", lambda seq: seq[-1])
    assert window._pick_random_indexed_candidate(include_skipped=False) is None
    assert window._pick_random_indexed_candidate(include_skipped=True) == ("Earth", "Water")
    assert window._pick_cheapest_indexed_candidate(include_skipped=False) is None
    assert window._pick_cheapest_indexed_candidate(include_skipped=True) == ("Earth", "Water")
    window.close()


def test_window_combination_status_messages(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    sample_result["done_pairs"] = {("Earth", "Earth")}
    sample_result["skipped_pairs"] = {("Earth", "Water")}

    assert "recette deja connue" in window._combination_status_message("Water", "Fire")
    assert "discardee globalement" in window._combination_status_message("Earth", "Wind")
    assert "marquee done" in window._combination_status_message("Earth", "Earth")
    assert "repoussee plus tard" in window._combination_status_message("Earth", "Water")
    assert "candidate encore proposable" in window._combination_status_message("Water", "Wind")
    window.close()


def test_window_current_candidate_panel(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    assert "Aucune combinaison courante." in window.current_candidate_details.toPlainText()

    window._current_result = sample_result
    window._set_current_pair(("Water", "Wind"), "suggestion random", suggestion_mode="random")
    panel_text = window.current_candidate_details.toPlainText()
    assert "Paire courante : Water + Wind" in panel_text
    assert "Origine : suggestion random" in panel_text
    assert "Poids resultat estime : 1" in panel_text
    assert "Encore dans l'index candidats : non" in panel_text

    sample_result["candidate_pairs"] = [("Water", "Wind")]
    window._validate_combination_inputs()
    assert "Encore dans l'index candidats : oui" in window.current_candidate_details.toPlainText()

    window._record_suggestion(("Earth", "Earth"), "cheapest")
    history_item = window.suggestion_history_list.item(0)
    window._restore_history_suggestion(history_item)
    assert "Origine : historique" in window.current_candidate_details.toPlainText()

    window.element1_edit.setText("Earth")
    window.element2_edit.setText("Fire")
    assert "Origine : manuelle" in window.current_candidate_details.toPlainText()
    sample_result["missing"] = [("Water", "Wind"), ("Earth", "Earth")]
    window._refresh_summary()
    assert window.candidate_count_label.text().endswith("2")
    window.close()


def test_window_build_selected_node_details_without_result(qapp) -> None:
    window = gui.InfiniteGraphWindow()
    assert window._build_selected_node_details("Ghost") == "Nom : Ghost"
    window.close()
