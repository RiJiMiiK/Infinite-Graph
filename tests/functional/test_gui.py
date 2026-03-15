from __future__ import annotations

from pathlib import Path

import pytest

from src.infinite_graph import gui

class _FakeSignal:
    def __init__(self) -> None:
        self.callbacks = []

    def connect(self, callback) -> None:
        self.callbacks.append(callback)

    def emit(self, *args) -> None:
        for callback in list(self.callbacks):
            callback(*args)


class _FakeThread:
    def __init__(self, parent=None) -> None:
        del parent
        self.started = _FakeSignal()
        self.quit_called = False
        self.wait_called = False

    def start(self) -> None:
        return None

    def quit(self) -> None:
        self.quit_called = True

    def wait(self) -> None:
        self.wait_called = True


class _FakeWorker:
    def __init__(
        self,
        input_path: str,
        focus_element: str | None,
        layout_iterations: int,
        spring_scale: float,
    ) -> None:
        self.input_path = input_path
        self.focus_element = focus_element
        self.layout_iterations = layout_iterations
        self.spring_scale = spring_scale
        self.progress = _FakeSignal()
        self.finished = _FakeSignal()
        self.failed = _FakeSignal()
        self.moved = None

    def moveToThread(self, thread) -> None:
        self.moved = thread

    def run(self) -> None:
        return None


def test_window_generate_and_input_pick(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    errors = []
    infos = []
    monkeypatch.setattr(gui.QMessageBox, "critical", lambda *args: errors.append(args))
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    window._generate()
    assert errors

    monkeypatch.setattr(gui, "QThread", _FakeThread)
    monkeypatch.setattr(gui, "GenerateWorker", _FakeWorker)
    window.input_edit.setText("save.json")
    window._generate()
    assert isinstance(window._worker_thread, _FakeThread)
    assert isinstance(window._worker, _FakeWorker)
    assert window._worker.input_path == "save.json"
    assert window._worker.focus_element is None
    assert window._worker.layout_iterations == 80
    assert window._worker.spring_scale == 1.2
    assert not window.progress_bar.isHidden()
    window._worker_thread = object()
    window._generate()

    window._worker_thread = None
    window.layout_iterations_edit.setText("bad")
    window._generate()
    assert "The layout settings are not valid." in infos[-1][-1]
    assert "Layout iterations must be a positive integer." in infos[-1][-1]

    monkeypatch.setattr(gui.QFileDialog, "getOpenFileName", lambda *args, **kwargs: ("picked.json", ""))
    window._pick_input()
    assert window.input_edit.text() == "picked.json"
    monkeypatch.setattr(gui.QFileDialog, "getOpenFileName", lambda *args, **kwargs: ("", ""))
    window._pick_input()
    window.close()


def test_window_generation_callbacks_and_cleanup(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    window.input_edit.setText("save.json")
    window._on_generation_progress(42, "step")
    assert "step" in window.stage_label.text()
    assert window.progress_bar.value() == 42
    window.suggestion_history_list.addItem("Random: Water + Earth")
    window._on_generation_finished(
        sample_result,
        {"positions": [], "adj": [], "sizes": [], "brushes": [], "labels": []},
        12.34,
    )
    assert window._current_result is sample_result
    assert window.random_button.isEnabled()
    assert "Discarded combinations" in window.summary_label.text()
    assert "Total generation time: 12.34s" in window.summary_label.text()
    assert "No node selected" in window.selected_node_details.toPlainText()
    assert "Water" in window.element_completer_model.stringList()
    assert window.discarded_model.rowCount() == 1
    assert window.discarded_model.data(window.discarded_model.index(0, 0)) == "Earth"
    assert window.discarded_model.data(window.discarded_model.index(0, 1)) == "Wind"
    assert window.progress_bar.value() == 100
    assert window.suggestion_history_list.count() == 0
    assert "12.34s" in window.stage_label.text()

    warned_result = dict(sample_result)
    warned_result["load_warnings"] = ["warn"]
    window._on_generation_finished(
        warned_result,
        {"positions": [], "adj": [], "sizes": [], "brushes": [], "labels": []},
        1.5,
    )
    assert "done with warnings" in window.stage_label.text()
    assert window.progress_bar.value() == 100
    assert "1.50s" in window.stage_label.text()

    errors = []
    monkeypatch.setattr(gui.QMessageBox, "critical", lambda *args: errors.append(args))
    window._on_generation_failed("bad")
    assert errors
    assert window.element_completer_model.stringList() == []
    assert window.current_candidate_details.toPlainText() == "No current combination."

    fake_thread = _FakeThread()
    window._worker_thread = fake_thread
    window._worker = object()
    window._cleanup_worker()
    assert fake_thread.quit_called is True
    assert fake_thread.wait_called is True
    assert window._worker_thread is None
    window._cleanup_worker()
    window.close()


def test_window_element_completion_setup_and_update(qapp) -> None:
    window = gui.InfiniteGraphWindow()
    assert window.element1_edit.completer() is window.element1_completer
    assert window.element2_edit.completer() is window.element2_completer
    assert window.element1_completer.caseSensitivity() == gui.Qt.CaseInsensitive
    assert window.element1_completer.filterMode() == gui.Qt.MatchContains
    window._update_element_completion(["Steam", "water", "Fire"])
    assert window.element_completer_model.stringList() == ["Fire", "Steam", "water"]
    window.close()


def test_window_missing_attribute_raises(qapp) -> None:
    window = gui.InfiniteGraphWindow()
    with pytest.raises(AttributeError):
        _ = window.missing_widget_name
    window.close()


def test_window_refresh_helpers_without_result(qapp) -> None:
    window = gui.InfiniteGraphWindow()
    window._refresh_missing_weight_list()
    window._refresh_summary()
    window._update_missing_statistics_for_pair(("Water", "Fire"), 1)
    assert window.missing_weight_list.count() == 0
    window.close()


def test_window_candidate_buttons_and_selection(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    window._pick_random_combination()
    window._pick_cheapest_combination()
    window._pick_next_combination()
    window._current_result = sample_result
    infos = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(gui, "find_random_combination", lambda *args, **kwargs: None)
    window._pick_next_combination()
    assert "Generate a suggestion first" in infos[-1][-1]
    window._pick_random_combination()
    assert infos
    monkeypatch.setattr(gui, "find_random_combination", lambda *args, **kwargs: ("A", "B"))
    window._pick_random_combination()
    assert window.element1_edit.text() == "A"

    monkeypatch.setattr(gui, "find_cheapest_combination", lambda *args, **kwargs: None)
    window._pick_cheapest_combination()
    monkeypatch.setattr(gui, "find_cheapest_combination", lambda *args, **kwargs: ("C", "D"))
    window._pick_cheapest_combination()
    assert window.element2_edit.text() == "D"
    random_calls = []
    cheapest_calls = []

    def fake_random(*args, **kwargs):
        random_calls.append(set(kwargs["done_pairs"]))
        return None if len(random_calls) == 1 else ("R", "S")

    def fake_cheapest(*args, **kwargs):
        cheapest_calls.append(set(kwargs["done_pairs"]))
        return None if len(cheapest_calls) == 1 else ("T", "U")

    monkeypatch.setattr(gui, "find_random_combination", fake_random)
    monkeypatch.setattr(gui, "find_cheapest_combination", fake_cheapest)
    sample_result["skipped_pairs"] = {("Earth", "Water")}
    window._pick_random_combination()
    window._pick_cheapest_combination()
    assert ("Earth", "Water") in random_calls[0]
    assert ("Earth", "Water") not in random_calls[1]
    assert ("Earth", "Water") in cheapest_calls[0]
    assert ("Earth", "Water") not in cheapest_calls[1]
    monkeypatch.setattr(gui, "find_random_combination", lambda *args, **kwargs: ("E", "F"))
    window.element1_edit.setText("Earth")
    window.element2_edit.setText("Water")
    window._last_suggestion_mode = "random"
    window._pick_next_combination()
    assert ("Earth", "Water") in sample_result["skipped_pairs"]
    assert window.element1_edit.text() == "E"
    sample_result["done_pairs"].add(("A", "B"))
    sample_result["discarded_pairs"].add(("C", "D"))
    window.element1_edit.setText("A")
    window.element2_edit.setText("B")
    window._pick_next_combination()
    window.element1_edit.setText("C")
    window.element2_edit.setText("D")
    window._last_suggestion_mode = "cheapest"
    monkeypatch.setattr(gui, "find_cheapest_combination", lambda *args, **kwargs: ("G", "H"))
    window._pick_next_combination()
    assert window.element1_edit.text() == "G"

    window._set_candidate_buttons_enabled(False)
    assert not window.random_button.isEnabled()
    window._set_candidate_buttons_enabled(True)
    assert window.next_button.isEnabled()
    assert window.done_button.isEnabled()
    assert window.undo_done_button.isEnabled()
    assert window.undo_discard_button.isEnabled()
    window._current_result = sample_result
    window.node_model.update_rows([["Fire", 0], ["Water", 0]])
    window._on_graph_node_selected("Fire")
    assert "Fire" in window.selected_node_label.text()
    assert window.node_table.selectionModel().hasSelection() is True
    details = window.selected_node_details.toPlainText()
    assert "Name: Fire" in details
    assert "Weight: 0" in details
    assert "Starter: yes" in details
    window._on_graph_node_selected("Water")
    details = window.selected_node_details.toPlainText()
    assert "Outgoing neighbors: Fire" in details
    window._on_graph_node_selected(None)
    assert "none" in window.selected_node_label.text()
    assert "No node selected" in window.selected_node_details.toPlainText()
    window.close()


def test_window_suggestion_history(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result

    window._record_suggestion(("Water", "Earth"), "random")
    window._record_suggestion(("Earth", "Earth"), "cheapest")
    window._record_suggestion(("Water", "Earth"), "random")

    assert window.suggestion_history_list.count() == 2
    assert window.suggestion_history_list.item(0).text() == "Random: Water + Earth"
    assert window.suggestion_history_list.item(1).text() == "Cheapest: Earth + Earth"

    history_item = window.suggestion_history_list.item(1)
    window._restore_history_suggestion(history_item)
    assert window.element1_edit.text() == "Earth"
    assert window.element2_edit.text() == "Earth"
    window._restore_history_suggestion(gui.QListWidgetItem("Sans paire"))
    assert window.element1_edit.text() == "Earth"
    assert window.element2_edit.text() == "Earth"

    for index in range(12):
        window._record_suggestion((f"Element {index}", "Earth"), "random")
    assert window.suggestion_history_list.count() == 10
    window.close()


def test_window_search_graph_node(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    infos = []
    selected = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(window.graph_view, "select_node_by_id", lambda node_id: selected.append(node_id))

    window._search_graph_node()
    window._current_result = sample_result
    window._search_graph_node()
    assert "Enter an element to search." in infos[-1][-1]

    window.graph_search_edit.setText("fire")
    window._search_graph_node()
    assert selected[-1] == "Fire"
    assert window.graph_search_edit.text() == "Fire"

    window.graph_search_edit.setText("unknown")
    window._search_graph_node()
    assert "not found" in infos[-1][-1]
    window.close()


def test_window_subgraph_filter(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    infos = []
    updates = []
    selections = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(window.graph_view, "update_graph", lambda render_data: updates.append(render_data))
    monkeypatch.setattr(window.graph_view, "select_node_by_id", lambda node_id: selections.append(node_id))

    window._apply_subgraph_filter()
    window._reset_subgraph_filter()
    window._current_result = sample_result
    window._full_render_data = {
        "positions": [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)],
        "adj": [(0, 1), (1, 2)],
        "sizes": [10, 10, 10],
        "brushes": [gui.pg.mkBrush("#fff"), gui.pg.mkBrush("#000"), gui.pg.mkBrush("#333")],
        "labels": [],
        "node_ids": ["Water", "Fire", "Steam"],
        "node_weights": [0, 0, 1],
    }

    window._apply_subgraph_filter()
    assert "select a node" in infos[-1][-1]

    window.graph_view._selected_node_id = "Fire"
    window._apply_subgraph_filter()
    assert window.subgraph_center_edit.text() == "Fire"
    assert updates[-1]["node_ids"] == ["Water", "Fire", "Steam"]
    assert selections[-1] == "Fire"

    window.subgraph_center_edit.setText("Water")
    window.subgraph_depth_edit.setText("bad")
    window._apply_subgraph_filter()
    assert "non-negative integer" in infos[-1][-1]

    window.subgraph_depth_edit.setText("1")
    window.subgraph_center_edit.setText("Ghost")
    window._apply_subgraph_filter()
    assert "Unable to build" in infos[-1][-1]

    window._reset_subgraph_filter()
    assert updates[-1]["node_ids"] == ["Water", "Fire", "Steam"]
    window.close()


def test_window_weight_filter(monkeypatch, qapp) -> None:
    window = gui.InfiniteGraphWindow()
    infos = []
    updates = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(window.graph_view, "update_graph", lambda render_data: updates.append(render_data))
    window._apply_weight_filter()
    window.graph_view._render_data = {
        "positions": [(0.0, 0.0), (100.0, 0.0)],
        "adj": [(0, 1)],
        "sizes": [10, 10],
        "brushes": [gui.pg.mkBrush("#fff"), gui.pg.mkBrush("#000")],
        "labels": [],
        "node_ids": ["Water", "Steam"],
        "node_weights": [0, 1],
    }

    window._apply_weight_filter()
    assert "at least a minimum or maximum weight" in infos[-1][-1]

    window.min_weight_edit.setText("bad")
    window._apply_weight_filter()
    assert "non-negative integers" in infos[-1][-1]

    window.min_weight_edit.setText("2")
    window.max_weight_edit.setText("1")
    window._apply_weight_filter()
    assert "greater than maximum" in infos[-1][-1]

    window.min_weight_edit.setText("0")
    window.max_weight_edit.setText("0")
    window._apply_weight_filter()
    assert updates[-1]["node_ids"] == ["Water"]
    window.close()


def test_window_layout_settings_and_rebuild(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    infos = []
    updates = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(
        gui,
        "build_graph_render_data",
        lambda *args, **kwargs: {
            "positions": [(0.0, 0.0)],
            "adj": [],
            "sizes": [10],
            "brushes": [gui.pg.mkBrush("#fff")],
            "labels": [],
            "node_ids": ["Water"],
            "node_weights": [0],
        },
    )
    monkeypatch.setattr(window.graph_view, "update_graph", lambda render_data: updates.append(render_data))

    assert window._layout_settings() == (80, 1.2)
    window.layout_iterations_edit.setText("bad")
    with pytest.raises(ValueError, match="iterations"):
        window._layout_settings()

    window.layout_iterations_edit.setText("80")
    window.layout_scale_edit.setText("bad")
    with pytest.raises(ValueError, match="spring scale"):
        window._layout_settings()

    window.layout_scale_edit.setText("0")
    with pytest.raises(ValueError, match="spring scale"):
        window._layout_settings()

    window.layout_scale_edit.setText("1.2")
    window._rebuild_layout()
    window._current_result = sample_result
    window.layout_iterations_edit.setText("10")
    window.layout_scale_edit.setText("2.5")
    window._rebuild_layout()
    assert updates[-1]["node_ids"] == ["Water"]
    assert window.stage_label.text() == "Current step: done"

    window.layout_iterations_edit.setText("0")
    window._rebuild_layout()
    assert "iterations" in infos[-1][-1]
    window.close()

def test_window_mark_done_branches(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    infos = []
    warns = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(gui.QMessageBox, "warning", lambda *args: warns.append(args))

    window._mark_current_combination_done()
    window._current_result = sample_result
    window._mark_current_combination_done()
    window.element1_edit.setText("X")
    window.element2_edit.setText("Y")
    window._mark_current_combination_done()
    window.element1_edit.setText("Water")
    window.element2_edit.setText("Fire")
    window._mark_current_combination_done()
    window.element1_edit.setText("Earth")
    window.element2_edit.setText("Wind")
    window._mark_current_combination_done()
    sample_result["done_pairs"].add(("Earth", "Earth"))
    window.element1_edit.setText("Earth")
    window.element2_edit.setText("Earth")
    window._mark_current_combination_done()
    window.element1_edit.setText("Water")
    window.element2_edit.setText("Earth")
    window._mark_current_combination_done()
    assert ("Earth", "Water") in sample_result["done_pairs"]
    assert sample_result["statistics"]["missing_counts_by_result_weight"] == [(1, 3)]
    assert window.element1_edit.text() == ""
    assert infos and warns
    window.close()


def test_window_undo_done_branches(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    infos = []
    warns = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(gui.QMessageBox, "warning", lambda *args: warns.append(args))

    window._undo_current_combination_done()
    window._current_result = sample_result
    window._undo_current_combination_done()
    window.element1_edit.setText("X")
    window.element2_edit.setText("Y")
    window._undo_current_combination_done()
    window.element1_edit.setText("Earth")
    window.element2_edit.setText("Water")
    window._undo_current_combination_done()
    sample_result["done_pairs"].add(("Earth", "Water"))
    sample_result["missing"] = [("Earth", "Earth")]
    sample_result["statistics"]["missing_counts_by_result_weight"] = [(1, 1)]
    window.element1_edit.setText("Water")
    window.element2_edit.setText("Earth")
    window._undo_current_combination_done()
    assert ("Earth", "Water") not in sample_result["done_pairs"]
    assert ("Earth", "Water") in sample_result["missing"]
    assert sample_result["statistics"]["missing_counts_by_result_weight"] == [(1, 2)]
    assert window.element1_edit.text() == ""
    assert infos and warns
    window.close()


def test_window_discard_branches(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    window._discard_current_combination()
    window._current_result = sample_result
    window._current_save_path = Path("save.json")
    infos = []
    warns = []
    added = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(gui.QMessageBox, "warning", lambda *args: warns.append(args))
    monkeypatch.setattr(gui, "add_discarded_pair", lambda path, pair: added.append((path, pair)))

    window._discard_current_combination()
    window.element1_edit.setText("X")
    window.element2_edit.setText("Y")
    window._discard_current_combination()
    window.element1_edit.setText("Water")
    window.element2_edit.setText("Fire")
    window._discard_current_combination()
    window.element1_edit.setText("Earth")
    window.element2_edit.setText("Wind")
    window._discard_current_combination()
    window.element1_edit.setText("Earth")
    window.element2_edit.setText("Water")
    window._discard_current_combination()
    assert added
    assert ("Earth", "Water") in sample_result["discarded_pairs"]
    assert sample_result["statistics"]["missing_counts_by_result_weight"] == [(1, 3)]
    assert window.missing_weight_list.count() == 1
    assert window.discarded_model.rowCount() == 2
    assert window.element1_edit.text() == ""
    assert infos and warns

    no_weight_result = dict(sample_result)
    no_weight_result["node_weights"] = {"Earth": None, "Water": 0}
    no_weight_result["discarded_pairs"] = set()
    no_weight_result["missing"] = [("Earth", "Water")]
    no_weight_result["statistics"] = {"missing_counts_by_result_weight": [(1, 1)]}
    window._current_result = no_weight_result
    window.element1_edit.setText("Earth")
    window.element2_edit.setText("Water")
    window._discard_current_combination()

    not_found_result = dict(sample_result)
    not_found_result["discarded_pairs"] = set()
    not_found_result["missing"] = [("Earth", "Water")]
    not_found_result["statistics"] = {"missing_counts_by_result_weight": [(2, 1)]}
    window._current_result = not_found_result
    window.element1_edit.setText("Earth")
    window.element2_edit.setText("Water")
    window._discard_current_combination()
    assert not_found_result["statistics"]["missing_counts_by_result_weight"] == [(2, 1)]
    assert window.missing_weight_list.count() == 1
    window.close()


def test_window_undo_discard_branches(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    infos = []
    warns = []
    removed = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(gui.QMessageBox, "warning", lambda *args: warns.append(args))
    monkeypatch.setattr(gui, "remove_discarded_pair", lambda path, pair: removed.append((path, pair)))

    window._undo_current_combination_discard()
    window._current_result = sample_result
    window._current_save_path = Path("save.json")
    window._undo_current_combination_discard()
    window.element1_edit.setText("X")
    window.element2_edit.setText("Y")
    window._undo_current_combination_discard()
    window.element1_edit.setText("Earth")
    window.element2_edit.setText("Water")
    window._undo_current_combination_discard()
    sample_result["discarded_pairs"].add(("Earth", "Water"))
    sample_result["missing"] = [("Earth", "Earth")]
    sample_result["statistics"]["missing_counts_by_result_weight"] = [(1, 1)]
    window.element1_edit.setText("Water")
    window.element2_edit.setText("Earth")
    window._undo_current_combination_discard()
    assert removed == [(Path("save.json"), ("Earth", "Water"))]
    assert ("Earth", "Water") not in sample_result["discarded_pairs"]
    assert ("Earth", "Water") in sample_result["missing"]
    assert sample_result["statistics"]["missing_counts_by_result_weight"] == [(1, 2)]
    assert window.discarded_model.rowCount() == 1
    assert window.discarded_model.data(window.discarded_model.index(0, 0)) == "Earth"
    assert window.discarded_model.data(window.discarded_model.index(0, 1)) == "Wind"
    assert window.element1_edit.text() == ""
    assert infos and warns
    window.close()


