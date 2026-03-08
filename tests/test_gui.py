from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QMessageBox

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
        "graph_nodes": [
            {"id": "Water", "label": "Water", "weight": 0, "is_starter": True},
            {"id": "Fire", "label": "Fire", "weight": 0, "is_starter": True},
        ],
        "graph_edges": [
            {"source": "Water", "target": "Fire", "weight": 1, "elements": ["Steam"]}
        ],
        "node_weights": {"Water": 0, "Fire": 0, "Wind": 0, "Earth": 0, "Steam": 1},
        "known_pairs": {("Fire", "Water")},
        "discarded_pairs": {("Earth", "Wind")},
        "done_pairs": set(),
        "statistics": {
            "recipe_counts_by_result_weight": [(1, 1)],
            "node_counts_by_weight": [(0, 2)],
            "missing_counts_by_result_weight": [(1, 4)],
        },
        "missing": [("Earth", "Water"), ("Earth", "Earth")],
        "missing_limit": 1000,
        "focus_element": None,
    }


def test_list_table_model_basic() -> None:
    model = gui.ListTableModel(["A", "B"], [[1, 2]])
    assert model.rowCount() == 1
    assert model.columnCount() == 2
    assert model.data(model.index(0, 0)) == "1"
    assert model.data(model.index(0, 0), role=Qt.ToolTipRole) is None
    assert model.headerData(0, Qt.Horizontal) == "A"
    assert model.headerData(0, Qt.Vertical) == "1"
    model.update_rows([[3, 4]])
    assert model.data(model.index(0, 1)) == "4"


def test_copy_line_edit_copies_to_clipboard(qapp) -> None:
    widget = gui.CopyLineEdit()
    widget.setText("hello")
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(1, 1),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    widget.mousePressEvent(event)
    assert qapp.clipboard().text() == "hello"


def test_stats_canvas_updates_series(qapp) -> None:
    canvas = gui.StatsCanvas()
    canvas.update_series([(1, 2)], [(0, 4)])
    assert len(canvas.axis.lines) == 2
    canvas.update_series([], [])
    assert len(canvas.axis.lines) == 0


def test_build_graph_render_data_with_progress(monkeypatch) -> None:
    def fake_spring_layout(graph, seed, k, iterations, pos=None):
        del graph, seed, k, iterations, pos
        return {"A": np.array([0.0, 0.0]), "B": np.array([1.0, 1.0])}

    monkeypatch.setattr(gui.nx, "spring_layout", fake_spring_layout)
    steps: list[str] = []
    render = gui.build_graph_render_data(
        [
            {"id": "A", "label": "A", "weight": 0, "is_starter": True},
            {"id": "B", "label": "B", "weight": None, "is_starter": False},
        ],
        [{"source": "A", "target": "B", "weight": 1, "elements": ["C"]}],
        progress_callback=steps.append,
    )
    assert len(render["positions"]) == 2
    assert render["adj"] == [(0, 1)]
    assert render["labels"]
    assert steps[-1].startswith("Computing spring layout: 80/80")


def test_graph_view_widget_update_graph(qapp) -> None:
    widget = gui.GraphViewWidget()
    widget.update_graph({"positions": [], "adj": [], "sizes": [], "brushes": [], "labels": []})
    widget.update_graph(
        {
            "positions": [(0.0, 0.0)],
            "adj": [],
            "sizes": [10],
            "brushes": [gui.pg.mkBrush("#ffffff")],
            "labels": [{"text": "A", "x": 0.0, "y": 0.0}],
        }
    )
    widget.update_graph(
        {
            "positions": [(1.0, 1.0)],
            "adj": [],
            "sizes": [10],
            "brushes": [gui.pg.mkBrush("#ffffff")],
            "labels": [],
        }
    )
    assert len(widget._labels) == 0


def test_graph_view_widget_node_selection(qapp) -> None:
    widget = gui.GraphViewWidget()
    selected = []
    widget.nodeSelected.connect(selected.append)
    widget.update_graph(
        {
            "positions": [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)],
            "adj": [(0, 1), (2, 0)],
            "sizes": [10, 10, 10],
            "brushes": [
                gui.pg.mkBrush("#ffffff"),
                gui.pg.mkBrush("#000000"),
                gui.pg.mkBrush("#333333"),
            ],
            "labels": [],
            "node_ids": ["Water", "Fire", "Steam"],
        }
    )
    assert widget.select_node_at((5.0, 0.0)) == "Water"
    assert selected[-1] == "Water"
    assert widget._neighbor_node_ids() == {"Fire", "Steam"}
    widget.select_node_by_id("Fire")
    assert selected[-1] == "Fire"
    assert widget._neighbor_node_ids() == {"Water"}
    assert widget.select_node_at((1000.0, 1000.0)) is None
    assert selected[-1] is None
    assert widget._neighbor_node_ids() == set()


def test_graph_view_widget_mouse_press_and_empty_selection(qapp, monkeypatch) -> None:
    widget = gui.GraphViewWidget()
    called = []
    monkeypatch.setattr(widget, "select_node_at", lambda position: called.append(position))
    widget.update_graph(
        {
            "positions": [(0.0, 0.0)],
            "adj": [],
            "sizes": [10],
            "brushes": [gui.pg.mkBrush("#ffffff")],
            "labels": [],
            "node_ids": ["Water"],
        }
    )
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(1, 1),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    widget.mousePressEvent(event)
    assert called

    empty_widget = gui.GraphViewWidget()
    assert empty_widget.select_node_at((0.0, 0.0)) is None


def test_generate_worker_success_and_failure(monkeypatch, sample_result) -> None:
    monkeypatch.setattr(gui, "process_save", lambda *args, **kwargs: sample_result)
    monkeypatch.setattr(
        gui,
        "build_graph_render_data",
        lambda nodes, edges, progress_callback=None: {"positions": [], "adj": [], "sizes": [], "brushes": [], "labels": []},
    )
    worker = gui.GenerateWorker("save.json", None)
    finished: list[dict[str, object]] = []
    failures: list[str] = []
    progress: list[str] = []
    worker.finished.connect(lambda result, render: finished.append(result))
    worker.failed.connect(failures.append)
    worker.progress.connect(progress.append)
    worker.run()
    assert finished
    assert not failures
    assert "Loading save file" in progress

    monkeypatch.setattr(gui, "process_save", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
    worker = gui.GenerateWorker("save.json", None)
    worker.failed.connect(failures.append)
    worker.run()
    assert "boom" in failures[-1]


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
    def __init__(self, input_path: str, focus_element: str | None) -> None:
        self.input_path = input_path
        self.focus_element = focus_element
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
    monkeypatch.setattr(gui.QMessageBox, "critical", lambda *args: errors.append(args))
    window._generate()
    assert errors

    monkeypatch.setattr(gui, "QThread", _FakeThread)
    monkeypatch.setattr(gui, "GenerateWorker", _FakeWorker)
    window.input_edit.setText("save.json")
    window.focus_edit.setText("Water")
    window._generate()
    assert isinstance(window._worker_thread, _FakeThread)
    assert isinstance(window._worker, _FakeWorker)
    assert window._worker.input_path == "save.json"
    assert window._worker.focus_element == "Water"
    assert not window.progress_bar.isHidden()
    window._worker_thread = object()
    window._generate()

    monkeypatch.setattr(gui.QFileDialog, "getOpenFileName", lambda *args, **kwargs: ("picked.json", ""))
    window._pick_input()
    assert window.input_edit.text() == "picked.json"
    monkeypatch.setattr(gui.QFileDialog, "getOpenFileName", lambda *args, **kwargs: ("", ""))
    window._pick_input()
    window.close()


def test_window_generation_callbacks_and_cleanup(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    window.input_edit.setText("save.json")
    window._on_generation_progress("step")
    assert "step" in window.stage_label.text()
    window._on_generation_finished(
        sample_result,
        {"positions": [], "adj": [], "sizes": [], "brushes": [], "labels": []},
    )
    assert window._current_result is sample_result
    assert window.random_button.isEnabled()
    assert "Combinaisons discardees" in window.summary_label.text()
    assert "Aucun noeud selectionne" in window.selected_node_details.toPlainText()

    warned_result = dict(sample_result)
    warned_result["load_warnings"] = ["warn"]
    window._on_generation_finished(
        warned_result,
        {"positions": [], "adj": [], "sizes": [], "brushes": [], "labels": []},
    )
    assert "done with warnings" in window.stage_label.text()

    errors = []
    monkeypatch.setattr(gui.QMessageBox, "critical", lambda *args: errors.append(args))
    window._on_generation_failed("bad")
    assert errors

    fake_thread = _FakeThread()
    window._worker_thread = fake_thread
    window._worker = object()
    window._cleanup_worker()
    assert fake_thread.quit_called is True
    assert fake_thread.wait_called is True
    assert window._worker_thread is None
    window._cleanup_worker()
    window.close()


def test_window_candidate_buttons_and_selection(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    window._pick_random_combination()
    window._pick_cheapest_combination()
    window._current_result = sample_result
    infos = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(gui, "find_random_combination", lambda *args, **kwargs: None)
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

    window._set_candidate_buttons_enabled(False)
    assert not window.random_button.isEnabled()
    window._set_candidate_buttons_enabled(True)
    assert window.done_button.isEnabled()
    window._current_result = sample_result
    window.node_model.update_rows([["Fire", 0], ["Water", 0]])
    window._on_graph_node_selected("Fire")
    assert "Fire" in window.selected_node_label.text()
    assert window.node_table.selectionModel().hasSelection() is True
    details = window.selected_node_details.toPlainText()
    assert "Nom : Fire" in details
    assert "Poids : 0" in details
    assert "Starter : oui" in details
    window._on_graph_node_selected("Water")
    details = window.selected_node_details.toPlainText()
    assert "Voisins sortants : Fire" in details
    window._on_graph_node_selected(None)
    assert "aucun" in window.selected_node_label.text()
    assert "Aucun noeud selectionne" in window.selected_node_details.toPlainText()
    window.close()


def test_window_build_selected_node_details_without_result(qapp) -> None:
    window = gui.InfiniteGraphWindow()
    assert window._build_selected_node_details("Ghost") == "Nom : Ghost"
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


def test_gui_main(monkeypatch, qapp) -> None:
    created = {}

    class FakeWindow:
        def __init__(self) -> None:
            created["window"] = self
            self.shown = False

        def show(self) -> None:
            self.shown = True

    monkeypatch.setattr(gui, "InfiniteGraphWindow", FakeWindow)
    monkeypatch.setattr(gui.QApplication, "instance", staticmethod(lambda: qapp))
    monkeypatch.setattr(qapp, "exec", lambda: 0)
    gui.main()
    assert created["window"].shown is True
