from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QBoxLayout

from src.infinite_graph import gui, gui_window_combinations


def test_window_live_element_validation(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    assert "no save loaded" in window.candidate_count_label.text()
    assert "QGroupBox" in window.styleSheet()
    assert window.generate_button.objectName() == "primaryButton"
    assert window.discard_button.objectName() == "dangerButton"

    window.element1_edit.setText("water")
    window._validate_combination_inputs()
    assert window.element1_edit.styleSheet() == ""
    assert window.element1_edit.toolTip() == ""
    assert "load a save" in window.candidate_status_label.text()
    assert "water + ?" in window.current_candidate_details.toPlainText()

    window._current_result = sample_result
    window.element1_edit.setText("water")
    window.element2_edit.setText("unknown")
    window._validate_combination_inputs()

    assert "#16a34a" in window.element1_edit.styleSheet()
    assert "Water" in window.element1_edit.toolTip()
    assert "#dc2626" in window.element2_edit.styleSheet()
    assert "not found" in window.element2_edit.toolTip()
    assert "not found" in window.candidate_status_label.text()
    assert "Origin: manual" in window.current_candidate_details.toPlainText()

    window.element1_edit.clear()
    window._validate_combination_inputs()
    assert window.element1_edit.styleSheet() == ""
    assert window.element1_edit.toolTip() == ""
    assert "enter or generate" in window.candidate_status_label.text()
    window.close()


def test_window_summary_panel_toggle_and_generation_state(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    errors = []
    monkeypatch.setattr(gui.QMessageBox, "critical", lambda *args: errors.append(args))
    summary_result = dict(sample_result)
    summary_result["statistics"] = {
        "recipe_counts_by_result_weight": [],
        "node_counts_by_weight": [],
        "missing_counts_by_result_weight": [],
    }
    summary_result["missing"] = []
    assert window.summary_panel.isHidden() is True
    assert window.current_candidate_details.isHidden() is True
    assert window.history_panel.isHidden() is True
    assert window.summary_toggle_button.text() == "Show details"
    assert window.current_candidate_toggle_button.text() == "Show candidate details"
    assert window.history_toggle_button.text() == "Show history"

    window._toggle_candidate_details()
    assert window.current_candidate_details.isHidden() is False
    assert window.current_candidate_toggle_button.text() == "Hide candidate details"

    window._toggle_history_panel()
    assert window.history_panel.isHidden() is False
    assert window.history_toggle_button.text() == "Hide history"

    window._toggle_summary_panel()
    assert window.summary_panel.isHidden() is False
    assert window.summary_toggle_button.text() == "Hide details"

    window._toggle_summary_panel()
    assert window.summary_panel.isHidden() is True
    assert window.summary_toggle_button.text() == "Show details"

    window.input_edit.setText("save.json")
    window._on_generation_finished(
        summary_result,
        {"positions": [], "adj": [], "sizes": [], "brushes": [], "labels": []},
        1.0,
    )
    assert window.candidate_count_label.text().endswith("0")
    assert "0 weight bucket(s)" in window.recipe_weight_summary_label.text()
    assert "0 total element(s)" in window.node_weight_summary_label.text()
    assert "0 candidate(s)" in window.missing_recipe_summary_label.text()
    assert window.missing_weight_group.title() == "Missing recipes by result weight"
    assert window.missing_weight_list.count() == 0
    assert window.summary_panel.isHidden() is False
    assert window.summary_toggle_button.text() == "Hide details"

    window._on_generation_failed("boom")
    assert "no save loaded" in window.candidate_count_label.text()
    assert window.recipe_weight_summary_label.text() == "Recipe series: no data"
    assert window.node_weight_summary_label.text() == "Element series: no data"
    assert window.missing_recipe_summary_label.text() == "Missing recipes: no data"
    assert window.summary_panel.isHidden() is False
    assert window.summary_toggle_button.text() == "Hide details"
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

    assert "already known" in window._combination_status_message("Water", "Fire")
    assert "globally discarded" in window._combination_status_message("Earth", "Wind")
    assert "marked done" in window._combination_status_message("Earth", "Earth")
    assert "postponed" in window._combination_status_message("Earth", "Water")
    assert "still available" in window._combination_status_message("Water", "Wind")
    window.close()


def test_window_current_candidate_panel(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    assert "No current combination." in window.current_candidate_details.toPlainText()

    window._current_result = sample_result
    window._set_current_pair(("Water", "Wind"), "random suggestion", suggestion_mode="random")
    panel_text = window.current_candidate_details.toPlainText()
    assert "Current pair: Water + Wind" in panel_text
    assert "Origin: random suggestion" in panel_text
    assert "Estimated result weight: 1" in panel_text
    assert "Still present in candidate index: no" in panel_text

    sample_result["candidate_pairs"] = [("Water", "Wind")]
    window._validate_combination_inputs()
    assert "Still present in candidate index: yes" in window.current_candidate_details.toPlainText()

    window._record_suggestion(("Earth", "Earth"), "cheapest")
    history_item = window.suggestion_history_list.item(0)
    window._restore_history_suggestion(history_item)
    assert "Origin: history" in window.current_candidate_details.toPlainText()

    window.element1_edit.setText("Earth")
    window.element2_edit.setText("Fire")
    assert "Origin: manual" in window.current_candidate_details.toPlainText()
    sample_result["missing"] = [("Water", "Wind"), ("Earth", "Earth")]
    window._refresh_summary()
    assert window.candidate_count_label.text().endswith("2")
    window.close()


def test_window_build_selected_node_details_without_result(qapp) -> None:
    window = gui.InfiniteGraphWindow()
    assert window._build_selected_node_details("Ghost") == "Name: Ghost"
    window.close()


def test_window_responsive_layout_directions(qapp) -> None:
    window = gui.InfiniteGraphWindow()

    window._update_responsive_layout(window.WIDE_LAYOUT_BREAKPOINT)
    assert window._controls_layout.direction() == QBoxLayout.LeftToRight
    assert window._candidate_row_layout.direction() == QBoxLayout.LeftToRight

    window._update_responsive_layout(window.STACKED_LAYOUT_BREAKPOINT - 1)
    assert window._controls_layout.direction() == QBoxLayout.TopToBottom
    assert window._candidate_row_layout.direction() == QBoxLayout.TopToBottom
    assert window._suggestion_row_layout.direction() == QBoxLayout.TopToBottom
    assert window._decision_row_layout.direction() == QBoxLayout.TopToBottom
    window.close()


def test_window_resize_event_updates_responsive_layout(qapp, monkeypatch) -> None:
    window = gui.InfiniteGraphWindow()
    widths = []
    monkeypatch.setattr(window, "_update_responsive_layout", lambda width: widths.append(width))
    event = QResizeEvent(QSize(900, 700), QSize(1480, 940))
    window.resizeEvent(event)
    assert widths == [900]
    window.close()


def test_window_ui_preferences_roundtrip(qapp, monkeypatch) -> None:
    stored_preferences = {}

    monkeypatch.setattr(
        gui,
        "load_ui_preferences",
        lambda: {
            "window_width": 1200,
            "window_height": 820,
            "summary_panel_visible": True,
            "candidate_details_visible": True,
            "history_panel_visible": True,
            "layout_iterations": 55,
            "layout_scale": 1.7,
            "graph_main_splitter_sizes": [500, 300],
            "graph_bottom_splitter_sizes": [250, 350],
            "info_top_splitter_sizes": [200, 600],
            "info_splitter_sizes": [450, 180],
        },
    )
    monkeypatch.setattr(
        gui, "save_ui_preferences", lambda preferences: stored_preferences.update(preferences)
    )

    window = gui.InfiniteGraphWindow()
    assert window.summary_panel.isHidden() is False
    assert window.current_candidate_details.isHidden() is False
    assert window.history_panel.isHidden() is False
    assert window.layout_iterations_edit.text() == "55"
    assert window.layout_scale_edit.text() == "1.7"

    window.summary_panel.setVisible(False)
    window.current_candidate_details.setVisible(False)
    window.history_panel.setVisible(False)
    window.layout_iterations_edit.setText("99")
    window.layout_scale_edit.setText("2.5")
    window._save_ui_preferences_state()
    assert stored_preferences["summary_panel_visible"] is False
    assert stored_preferences["candidate_details_visible"] is False
    assert stored_preferences["history_panel_visible"] is False
    assert stored_preferences["layout_iterations"] == "99"
    assert stored_preferences["layout_scale"] == "2.5"
    assert "graph_main_splitter_sizes" in stored_preferences
    window.close()


def test_window_skips_saved_size_that_does_not_fit_screen(qapp, monkeypatch) -> None:
    monkeypatch.setattr(
        gui,
        "load_ui_preferences",
        lambda: {
            "window_width": 4000,
            "window_height": 3000,
        },
    )

    original_width = 1480
    original_height = 940
    window = gui.InfiniteGraphWindow()

    assert window.width() == original_width
    assert window.height() == original_height
    window.close()


def test_window_saved_size_fits_screen_without_screen(qapp, monkeypatch) -> None:
    window = gui.InfiniteGraphWindow()
    monkeypatch.setattr(window, "screen", lambda: None)

    assert window._saved_window_size_fits_screen(4000, 3000) is True
    window.close()
