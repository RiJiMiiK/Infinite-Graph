from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PySide6.QtCore import QEvent, QModelIndex, QPointF, Qt
from PySide6.QtGui import QMouseEvent

from src.infinite_graph import gui
from src.infinite_graph.ui.table import ContainsFilterProxyModel


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

    monkeypatch.setattr(
        gui,
        "process_save",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    worker = gui.GenerateWorker("save.json", None, 80, 1.2)
    worker.failed.connect(failures.append)
    worker.run()
    assert "boom" in failures[-1]


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


def test_contains_filter_proxy_model_basic() -> None:
    model = gui.ListTableModel(
        ["Element", "Weight"],
        [["Water", 0], ["Steam", 1]],
    )
    proxy = ContainsFilterProxyModel()
    proxy.set_filter_text("water")
    assert proxy.filterAcceptsRow(0, QModelIndex()) is True

    proxy.setSourceModel(model)
    assert proxy.rowCount() == 1
    proxy.set_filter_text("")
    assert proxy.rowCount() == 2

    proxy.set_filter_text("ste")
    assert proxy.rowCount() == 1
    assert proxy.data(proxy.index(0, 0)) == "Steam"

    proxy.set_filter_text("0")
    assert proxy.rowCount() == 1
    assert proxy.data(proxy.index(0, 0)) == "Water"

    proxy.set_filter_text("missing")
    assert proxy.rowCount() == 0


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
