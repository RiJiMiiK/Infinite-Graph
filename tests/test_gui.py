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
    def fake_spring_layout(graph, seed, k, iterations, pos=None, **kwargs):
        del graph, seed, k, iterations, pos, kwargs
        return {"A": np.array([0.0, 0.0]), "B": np.array([1.0, 1.0])}

    monkeypatch.setattr(gui.nx, "spring_layout", fake_spring_layout)
    steps: list[tuple[int, str]] = []
    render = gui.build_graph_render_data(
        [
            {"id": "A", "label": "A", "weight": 0, "is_starter": True},
            {"id": "B", "label": "B", "weight": None, "is_starter": False},
        ],
        [{"source": "A", "target": "B", "weight": 1, "elements": ["C"]}],
        progress_callback=lambda percent, message: steps.append((percent, message)),
        layout_iterations=10,
        spring_scale=2.0,
    )
    assert len(render["positions"]) == 2
    assert render["adj"] == [(0, 1)]
    assert render["labels"]
    assert steps[0] == (
        gui.GENERATION_STAGE_PROGRESS["Preparing graph structure"],
        "Preparing graph structure",
    )
    assert steps[1] == (
        gui.GENERATION_STAGE_PROGRESS["Checking layout cache"],
        "Checking layout cache",
    )
    assert steps[2] == (
        gui.GENERATION_STAGE_PROGRESS["Initializing spring layout"],
        "Initializing spring layout",
    )
    assert steps[-2][0] == gui.LAYOUT_PROGRESS_END
    assert steps[-2][1].startswith("Computing spring layout: 10/10")
    assert steps[-1] == (
        gui.GENERATION_STAGE_PROGRESS["Finalizing graph geometry"],
        "Finalizing graph geometry",
    )


def test_build_graph_render_data_uses_local_cache(monkeypatch, tmp_path: Path) -> None:
    save_path = tmp_path / "save.json"
    save_path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(gui, "layout_cache_dir", lambda: tmp_path / "layout-cache")
    spring_calls = []

    def fake_spring_layout(graph, seed, k, iterations, pos=None, **kwargs):
        del graph, seed, k, iterations, pos, kwargs
        spring_calls.append("called")
        return {"A": np.array([0.0, 0.0]), "B": np.array([1.0, 1.0])}

    monkeypatch.setattr(gui.nx, "spring_layout", fake_spring_layout)
    first_render = gui.build_graph_render_data(
        [
            {"id": "A", "label": "A", "weight": 0, "is_starter": True},
            {"id": "B", "label": "B", "weight": 1, "is_starter": False},
        ],
        [{"source": "A", "target": "B", "weight": 1, "elements": ["C"]}],
        layout_iterations=10,
        spring_scale=2.0,
        cache_save_path=save_path,
    )
    assert spring_calls == ["called", "called"]

    monkeypatch.setattr(
        gui.nx,
        "spring_layout",
        lambda *args, **kwargs: pytest.fail("spring layout should not run when cache is available"),
    )
    steps: list[tuple[int, str]] = []
    second_render = gui.build_graph_render_data(
        [
            {"id": "A", "label": "A", "weight": 0, "is_starter": True},
            {"id": "B", "label": "B", "weight": 1, "is_starter": False},
        ],
        [{"source": "A", "target": "B", "weight": 1, "elements": ["C"]}],
        progress_callback=lambda percent, message: steps.append((percent, message)),
        layout_iterations=10,
        spring_scale=2.0,
        cache_save_path=save_path,
    )
    assert first_render["positions"] == second_render["positions"]
    assert (
        gui.GENERATION_STAGE_PROGRESS["Loading cached layout"],
        "Loading cached layout",
    ) in steps


def test_build_subgraph_render_data() -> None:
    render_data = {
        "positions": [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)],
        "adj": [(0, 1), (1, 2)],
        "sizes": [10, 10, 10],
        "brushes": [gui.pg.mkBrush("#fff"), gui.pg.mkBrush("#000"), gui.pg.mkBrush("#333")],
        "labels": [
            {"text": "Water", "x": 0.0, "y": 0.0},
            {"text": "Fire", "x": 100.0, "y": 0.0},
            {"text": "Steam", "x": 200.0, "y": 0.0},
        ],
        "node_ids": ["Water", "Fire", "Steam"],
        "node_weights": [0, 0, 1],
    }
    filtered = gui.build_subgraph_render_data(render_data, "Fire", 1)
    assert filtered["node_ids"] == ["Water", "Fire", "Steam"]
    assert filtered["adj"] == [(0, 1), (1, 2)]

    filtered = gui.build_subgraph_render_data(render_data, "Water", 0)
    assert filtered["node_ids"] == ["Water"]
    assert filtered["adj"] == []
    isolated = dict(render_data)
    isolated["adj"] = []
    assert gui.build_subgraph_render_data(isolated, "Water", 5)["node_ids"] == ["Water"]
    assert gui.build_subgraph_render_data(render_data, "Ghost", 1) is None
    assert gui.build_subgraph_render_data(render_data, "Water", -1) is None


def test_build_weight_filtered_render_data() -> None:
    render_data = {
        "positions": [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)],
        "adj": [(0, 1), (1, 2)],
        "sizes": [10, 10, 10],
        "brushes": [gui.pg.mkBrush("#fff"), gui.pg.mkBrush("#000"), gui.pg.mkBrush("#333")],
        "labels": [
            {"text": "Water", "x": 0.0, "y": 0.0},
            {"text": "Steam", "x": 100.0, "y": 0.0},
            {"text": "Cloud", "x": 200.0, "y": 0.0},
        ],
        "node_ids": ["Water", "Steam", "Cloud"],
        "node_weights": [0, 1, None],
    }
    filtered = gui.build_weight_filtered_render_data(render_data, 0, 0)
    assert filtered["node_ids"] == ["Water"]
    assert filtered["adj"] == []

    filtered = gui.build_weight_filtered_render_data(render_data, 0, 1)
    assert filtered["node_ids"] == ["Water", "Steam"]
    assert filtered["adj"] == [(0, 1)]

    filtered = gui.build_weight_filtered_render_data(render_data, 1, None)
    assert filtered["node_ids"] == ["Steam"]


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
    ranges = []
    widget.nodeSelected.connect(selected.append)
    widget.getViewBox().setRange = lambda *args, **kwargs: ranges.append((args, kwargs))
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
    assert ranges
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


def test_graph_view_widget_center_on_selected_node_without_match(qapp) -> None:
    widget = gui.GraphViewWidget()
    widget._render_data = {"node_ids": ["Water"], "positions": [(10.0, 20.0)]}
    widget._selected_node_id = "Fire"
    widget._center_on_selected_node()


def test_generate_worker_success_and_failure(monkeypatch, sample_result) -> None:
    def fake_process_save(*args, **kwargs):
        kwargs["progress_callback"]("Loading save file")
        return sample_result

    monkeypatch.setattr(gui, "process_save", fake_process_save)
    monkeypatch.setattr(
        gui,
        "build_graph_render_data",
        lambda *args, **kwargs: {
            "positions": [],
            "adj": [],
            "sizes": [],
            "brushes": [],
            "labels": [],
            "node_ids": [],
            "node_weights": [],
        },
    )
    worker = gui.GenerateWorker("save.json", None, 80, 1.2)
    finished: list[dict[str, object]] = []
    elapsed_values: list[float] = []
    failures: list[str] = []
    progress: list[tuple[int, str]] = []
    worker.finished.connect(
        lambda result, render, elapsed: (finished.append(result), elapsed_values.append(elapsed))
    )
    worker.failed.connect(failures.append)
    worker.progress.connect(lambda percent, message: progress.append((percent, message)))
    worker.run()
    assert finished
    assert elapsed_values
    assert elapsed_values[-1] >= 0.0
    assert not failures
    assert progress[0] == (0, "Starting generation")
    assert (gui.GENERATION_STAGE_PROGRESS["Loading save file"], "Loading save file") in progress
    assert progress[-1] == (100, "Preparing interface update")

    monkeypatch.setattr(gui, "process_save", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
    worker = gui.GenerateWorker("save.json", None, 80, 1.2)
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
    window.focus_edit.setText("Water")
    window._generate()
    assert isinstance(window._worker_thread, _FakeThread)
    assert isinstance(window._worker, _FakeWorker)
    assert window._worker.input_path == "save.json"
    assert window._worker.focus_element == "Water"
    assert window._worker.layout_iterations == 80
    assert window._worker.spring_scale == 1.2
    assert not window.progress_bar.isHidden()
    window._worker_thread = object()
    window._generate()

    window._worker_thread = None
    window.layout_iterations_edit.setText("bad")
    window._generate()
    assert infos[-1][-1] == "Les iterations du layout doivent etre un entier positif."

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
    assert "Combinaisons discardees" in window.summary_label.text()
    assert "Temps total de generation : 12.34s" in window.summary_label.text()
    assert "Aucun noeud selectionne" in window.selected_node_details.toPlainText()
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
    assert "Genere d'abord" in infos[-1][-1]
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


def test_window_build_selected_node_details_without_result(qapp) -> None:
    window = gui.InfiniteGraphWindow()
    assert window._build_selected_node_details("Ghost") == "Nom : Ghost"
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
    assert infos[-1][-1] == "Saisis un element a rechercher."

    window.graph_search_edit.setText("fire")
    window._search_graph_node()
    assert selected[-1] == "Fire"
    assert window.graph_search_edit.text() == "Fire"

    window.graph_search_edit.setText("unknown")
    window._search_graph_node()
    assert "introuvable" in infos[-1][-1]
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
    assert "selectionne un noeud" in infos[-1][-1]

    window.graph_view._selected_node_id = "Fire"
    window._apply_subgraph_filter()
    assert window.subgraph_center_edit.text() == "Fire"
    assert updates[-1]["node_ids"] == ["Water", "Fire", "Steam"]
    assert selections[-1] == "Fire"

    window.subgraph_center_edit.setText("Water")
    window.subgraph_depth_edit.setText("bad")
    window._apply_subgraph_filter()
    assert "entier positif" in infos[-1][-1]

    window.subgraph_depth_edit.setText("1")
    window.subgraph_center_edit.setText("Ghost")
    window._apply_subgraph_filter()
    assert "Impossible de construire" in infos[-1][-1]

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
    assert "au moins un poids" in infos[-1][-1]

    window.min_weight_edit.setText("bad")
    window._apply_weight_filter()
    assert "entiers positifs" in infos[-1][-1]

    window.min_weight_edit.setText("2")
    window.max_weight_edit.setText("1")
    window._apply_weight_filter()
    assert "superieur" in infos[-1][-1]

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


def test_layout_cache_helpers(tmp_path: Path, monkeypatch) -> None:
    save_path = tmp_path / "save.json"
    save_path.write_text("{}", encoding="utf-8")
    assert gui.layout_cache_dir().name == "layouts"
    monkeypatch.setattr(gui, "layout_cache_dir", lambda: tmp_path / "layout-cache")

    assert gui.load_cached_layout(save_path, ["Water"], 80, 1.2) is None
    assert gui.layout_cache_dir() == tmp_path / "layout-cache"
    gui.save_cached_layout(save_path, ["Water"], [(1.5, 2.5)], 80, 1.2)
    assert gui.load_cached_layout(save_path, ["Water"], 80, 1.2) == [(1.5, 2.5)]
    assert gui.load_cached_layout(save_path, ["Fire"], 80, 1.2) is None
    cache_file = gui._layout_cache_file(save_path, 80, 1.2)
    cache_file.write_text(
        '{"version": 0, "node_ids": ["Water"], "positions": [[1.5, 2.5]]}',
        encoding="utf-8",
    )
    assert gui.load_cached_layout(save_path, ["Water"], 80, 1.2) is None
    cache_file.write_text("{", encoding="utf-8")
    assert gui.load_cached_layout(save_path, ["Water"], 80, 1.2) is None


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


def test_window_update_missing_statistics_adds_new_weight_bucket(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    sample_result["statistics"]["missing_counts_by_result_weight"] = []
    sample_result["node_weights"] = {"Water": 0, "Steam": 1}
    window._current_result = sample_result
    window._update_missing_statistics_for_pair(("Water", "Steam"), 1)
    assert sample_result["statistics"]["missing_counts_by_result_weight"] == [(2, 1)]
    assert window.missing_weight_list.count() == 1
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
