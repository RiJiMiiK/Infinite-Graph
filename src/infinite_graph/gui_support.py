"""Support classes and helpers for the Qt GUI."""

# pylint: disable=too-many-lines

from __future__ import annotations

import hashlib
import json
import time
from contextlib import suppress
from pathlib import Path
from typing import Callable

import networkx as nx
import numpy as np
import pyqtgraph as pg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtWidgets import QApplication, QLineEdit

GENERATION_STAGE_PROGRESS = {
    "Starting generation": 0,
    "Loading save file": 5,
    "Loading discarded combinations": 12,
    "Building graph model": 20,
    "Computing graph statistics": 35,
    "Computing missing combinations": 50,
    "Preparing graph structure": 58,
    "Checking layout cache": 59,
    "Initializing spring layout": 60,
    "Loading cached layout": 95,
    "Finalizing graph geometry": 96,
    "Preparing interface update": 100,
}
LAYOUT_PROGRESS_START = 60
LAYOUT_PROGRESS_END = 95
INTERFACE_PROGRESS = {
    "Updating graph view": 96,
    "Updating node table": 97,
    "Updating edge table": 98,
    "Updating statistics": 99,
    "Updating summary": 100,
}
LAYOUT_CACHE_VERSION = 1


class ListTableModel(QAbstractTableModel):
    def __init__(self, headers: list[str], rows: list[list[object]] | None = None) -> None:
        super().__init__()
        self.headers = headers
        self.rows = rows or []

    def update_rows(self, rows: list[list[object]]) -> None:
        self.beginResetModel()
        self.rows = rows
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> object:
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return str(self.rows[index.row()][index.column()])

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> object:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.headers[section]
        return str(section + 1)


class CopyLineEdit(QLineEdit):
    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton and self.text():
            QApplication.clipboard().setText(self.text())


class StatsCanvas(FigureCanvasQTAgg):
    def __init__(self) -> None:
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.axis = self.figure.add_subplot(111)
        super().__init__(self.figure)

    def update_series(
        self,
        recipe_series: list[tuple[int, int]],
        node_series: list[tuple[int, int]],
    ) -> None:
        self.axis.clear()
        if recipe_series:
            self.axis.plot(
                [weight for weight, _ in recipe_series],
                [count for _, count in recipe_series],
                label="Recipes faites par poids du resultat",
                color="#dc2626",
            )
        if node_series:
            self.axis.plot(
                [weight for weight, _ in node_series],
                [count for _, count in node_series],
                label="Elements par poids",
                color="#2563eb",
            )
        self.axis.set_xlabel("Poids")
        self.axis.set_ylabel("Nombre")
        self.axis.grid(True, alpha=0.2)
        if recipe_series or node_series:
            self.axis.legend()
        self.figure.tight_layout()
        self.draw()


def build_graph_render_data(
    nodes: list[dict[str, object]],
    edges: list[dict[str, object]],
    progress_callback: Callable[[int, str], None] | None = None,
    layout_iterations: int = 80,
    spring_scale: float = 1.2,
    cache_save_path: Path | None = None,
) -> dict[str, object]:
    ordered_nodes = sorted(nodes, key=lambda item: str(item["id"]))
    names = [str(node["id"]) for node in ordered_nodes]
    if progress_callback is not None:
        progress_callback(
            GENERATION_STAGE_PROGRESS["Preparing graph structure"],
            "Preparing graph structure",
        )
    graph = nx.DiGraph()
    graph.add_nodes_from(names)
    graph.add_edges_from((str(edge["source"]), str(edge["target"])) for edge in edges)

    positions = _compute_layout_positions(
        graph,
        names,
        layout_iterations,
        spring_scale,
        progress_callback,
        cache_save_path,
    )

    index_by_name = {name: idx for idx, name in enumerate(names)}
    adj = []
    for edge in edges:
        source = index_by_name.get(str(edge["source"]))
        target = index_by_name.get(str(edge["target"]))
        if source is not None and target is not None:
            adj.append((source, target))

    symbol_brush = []
    sizes = []
    for node in ordered_nodes:
        weight = node["weight"]
        symbol_brush.append(pg.mkBrush("#10b981" if node["is_starter"] else "#2563eb"))
        sizes.append(16 if weight is None else max(6, 16 - min(int(weight), 10) * 0.5))

    labels = []
    if len(nodes) <= 120:
        labels = [
            {"text": str(node["label"]), "x": x, "y": y}
            for node, (x, y) in zip(ordered_nodes, positions)
        ]

    return {
        "positions": positions,
        "adj": adj,
        "sizes": sizes,
        "brushes": symbol_brush,
        "labels": labels,
        "node_ids": names,
        "node_weights": [node["weight"] for node in ordered_nodes],
    }


def _compute_layout_positions(
    graph: nx.DiGraph,
    names: list[str],
    layout_iterations: int,
    spring_scale: float,
    progress_callback: Callable[[int, str], None] | None,
    cache_save_path: Path | None,
) -> list[tuple[float, float]]:
    total_iterations = max(1, layout_iterations)
    batch_size = 5
    if progress_callback is not None:
        progress_callback(
            GENERATION_STAGE_PROGRESS["Checking layout cache"],
            "Checking layout cache",
        )

    if cache_save_path is not None:
        cached_positions = load_cached_layout(
            cache_save_path,
            names,
            layout_iterations,
            spring_scale,
        )
        if cached_positions is not None:
            if progress_callback is not None:
                progress_callback(
                    GENERATION_STAGE_PROGRESS["Loading cached layout"],
                    "Loading cached layout",
                )
                progress_callback(
                    GENERATION_STAGE_PROGRESS["Finalizing graph geometry"],
                    "Finalizing graph geometry",
                )
            return cached_positions

    spring_positions = _run_spring_layout(
        graph,
        names,
        total_iterations,
        batch_size,
        spring_scale,
        progress_callback,
    )
    positions = [
        (
            float(spring_positions[name][0] * 2000.0),
            float(spring_positions[name][1] * 2000.0),
        )
        for name in names
    ]
    if progress_callback is not None:
        progress_callback(
            GENERATION_STAGE_PROGRESS["Finalizing graph geometry"],
            "Finalizing graph geometry",
        )
    if cache_save_path is not None:
        save_cached_layout(
            cache_save_path,
            names,
            positions,
            layout_iterations,
            spring_scale,
        )
    return positions


def _run_spring_layout(
    graph: nx.DiGraph,
    names: list[str],
    total_iterations: int,
    batch_size: int,
    spring_scale: float,
    progress_callback: Callable[[int, str], None] | None,
) -> dict[str, np.ndarray]:
    spring_positions = None
    started_at = time.perf_counter()
    if progress_callback is not None:
        progress_callback(
            GENERATION_STAGE_PROGRESS["Initializing spring layout"],
            "Initializing spring layout",
        )
    for current_iteration in range(0, total_iterations, batch_size):
        iterations = min(batch_size, total_iterations - current_iteration)
        spring_positions = nx.spring_layout(
            graph,
            seed=42,
            k=None if len(names) < 2 else spring_scale / np.sqrt(len(names)),
            iterations=iterations,
            pos=spring_positions,
        )
        if progress_callback is not None:
            completed = current_iteration + iterations
            elapsed = time.perf_counter() - started_at
            eta = (
                0.0
                if completed == 0
                else max(0.0, elapsed * (total_iterations - completed) / completed)
            )
            progress = LAYOUT_PROGRESS_START + int(
                (completed / total_iterations) * (LAYOUT_PROGRESS_END - LAYOUT_PROGRESS_START)
            )
            progress_callback(
                min(progress, LAYOUT_PROGRESS_END),
                f"Computing spring layout: {completed}/{total_iterations} iterations "
                f"(elapsed {elapsed:.1f}s, ETA {eta:.1f}s)"
            )
    assert spring_positions is not None
    return spring_positions


def layout_cache_dir() -> Path:
    root_dir = Path(__file__).resolve().parents[2]
    return root_dir / ".cache" / "infinite_graph" / "layouts"


def _layout_cache_file(
    save_path: Path,
    layout_iterations: int,
    spring_scale: float,
) -> Path:
    file_stat = save_path.stat()
    cache_key = hashlib.sha256(
        (
            f"{LAYOUT_CACHE_VERSION}|{save_path.resolve()}|{file_stat.st_size}|"
            f"{file_stat.st_mtime_ns}|{layout_iterations}|{spring_scale:.6f}"
        ).encode("utf-8")
    ).hexdigest()
    return layout_cache_dir() / f"{cache_key}.json"


def load_cached_layout(
    save_path: Path,
    node_ids: list[str],
    layout_iterations: int,
    spring_scale: float,
) -> list[tuple[float, float]] | None:
    cache_file = _layout_cache_file(save_path, layout_iterations, spring_scale)
    if not cache_file.is_file():
        return None

    with suppress(OSError, ValueError, TypeError, KeyError):
        cache_payload = json.loads(cache_file.read_text(encoding="utf-8"))
        if cache_payload["version"] != LAYOUT_CACHE_VERSION:
            return None
        if cache_payload["node_ids"] != node_ids:
            return None
        return [
            (float(position[0]), float(position[1]))
            for position in cache_payload["positions"]
        ]
    return None


def save_cached_layout(
    save_path: Path,
    node_ids: list[str],
    positions: list[tuple[float, float]],
    layout_iterations: int,
    spring_scale: float,
) -> None:
    cache_file = _layout_cache_file(save_path, layout_iterations, spring_scale)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(
        json.dumps(
            {
                "version": LAYOUT_CACHE_VERSION,
                "node_ids": node_ids,
                "positions": positions,
            }
        ),
        encoding="utf-8",
    )


def build_subgraph_render_data(
    render_data: dict[str, object],
    center_node_id: str,
    max_depth: int,
) -> dict[str, object] | None:
    node_ids = list(render_data.get("node_ids", []))
    if center_node_id not in node_ids or max_depth < 0:
        return None

    adjacency: dict[int, set[int]] = {index: set() for index in range(len(node_ids))}
    for source_index, target_index in render_data.get("adj", []):
        if 0 <= source_index < len(node_ids) and 0 <= target_index < len(node_ids):
            adjacency[source_index].add(target_index)
            adjacency[target_index].add(source_index)

    center_index = node_ids.index(center_node_id)
    visited = {center_index}
    frontier = {center_index}
    for _ in range(max_depth):
        next_frontier = set()
        for node_index in frontier:
            next_frontier.update(adjacency.get(node_index, set()) - visited)
        visited.update(next_frontier)
        frontier = next_frontier
        if not frontier:
            break

    kept_indices = sorted(visited)
    index_map = {old_index: new_index for new_index, old_index in enumerate(kept_indices)}
    labels = render_data.get("labels", [])
    filtered_labels = []
    if len(labels) == len(node_ids):
        filtered_labels = [labels[index] for index in kept_indices]

    return {
        "positions": [render_data["positions"][index] for index in kept_indices],
        "adj": [
            (index_map[source_index], index_map[target_index])
            for source_index, target_index in render_data.get("adj", [])
            if source_index in index_map and target_index in index_map
        ],
        "sizes": [render_data["sizes"][index] for index in kept_indices],
        "brushes": [render_data["brushes"][index] for index in kept_indices],
        "labels": filtered_labels,
        "node_ids": [node_ids[index] for index in kept_indices],
        "node_weights": [render_data["node_weights"][index] for index in kept_indices],
    }


def build_weight_filtered_render_data(
    render_data: dict[str, object],
    min_weight: int | None,
    max_weight: int | None,
) -> dict[str, object]:
    node_weights = list(render_data.get("node_weights", []))
    kept_indices = []
    for index, weight in enumerate(node_weights):
        if weight is None:
            continue
        if min_weight is not None and int(weight) < min_weight:
            continue
        if max_weight is not None and int(weight) > max_weight:
            continue
        kept_indices.append(index)

    index_map = {old_index: new_index for new_index, old_index in enumerate(kept_indices)}
    labels = render_data.get("labels", [])
    filtered_labels = []
    if len(labels) == len(node_weights):
        filtered_labels = [labels[index] for index in kept_indices]

    return {
        "positions": [render_data["positions"][index] for index in kept_indices],
        "adj": [
            (index_map[source_index], index_map[target_index])
            for source_index, target_index in render_data.get("adj", [])
            if source_index in index_map and target_index in index_map
        ],
        "sizes": [render_data["sizes"][index] for index in kept_indices],
        "brushes": [render_data["brushes"][index] for index in kept_indices],
        "labels": filtered_labels,
        "node_ids": [render_data["node_ids"][index] for index in kept_indices],
        "node_weights": [node_weights[index] for index in kept_indices],
    }


class GraphViewWidget(pg.PlotWidget):
    nodeSelected = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.setBackground("w")
        self.showGrid(x=True, y=True, alpha=0.08)
        self.setMenuEnabled(False)
        self.setMouseEnabled(x=True, y=True)
        self.getViewBox().setDefaultPadding(0.05)
        self.getPlotItem().hideAxis("left")
        self.getPlotItem().hideAxis("bottom")
        self.graph_item = pg.GraphItem()
        self.addItem(self.graph_item)
        self._labels: list[pg.TextItem] = []
        self._render_data: dict[str, object] = {}
        self._selected_node_id: str | None = None

    def update_graph(self, render_data: dict[str, object]) -> None:
        self.clear()
        self.addItem(self.graph_item)
        for label in self._labels:
            self.removeItem(label)
        self._labels = []
        self._render_data = render_data
        self._selected_node_id = None

        positions = render_data["positions"]
        if not positions:
            self.nodeSelected.emit(None)
            return

        self._apply_graph_style()

        for label in render_data["labels"]:
            text_item = pg.TextItem(label["text"], color="#0f172a", anchor=(0.5, 1.2))
            text_item.setPos(label["x"], label["y"])
            self.addItem(text_item)
            self._labels.append(text_item)

        self.autoRange()

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.LeftButton and self._render_data.get("positions"):
            scene_pos = self.mapToScene(ev.position().toPoint())
            view_pos = self.getViewBox().mapSceneToView(scene_pos)
            self.select_node_at((float(view_pos.x()), float(view_pos.y())))
        super().mousePressEvent(ev)

    def select_node_by_id(self, node_id: str | None) -> None:
        available_ids = set(self._render_data.get("node_ids", []))
        self._selected_node_id = node_id if node_id in available_ids else None
        if self._render_data.get("positions"):
            self._apply_graph_style()
            self._center_on_selected_node()
        self.nodeSelected.emit(self._selected_node_id)

    def select_node_at(
        self,
        position: tuple[float, float],
        max_distance: float = 80.0,
    ) -> str | None:
        node_ids = self._render_data.get("node_ids", [])
        positions = self._render_data.get("positions", [])
        if not node_ids or not positions:
            self.select_node_by_id(None)
            return None

        selected_id = None
        best_distance = max_distance**2
        for node_id, node_position in zip(node_ids, positions):
            dx = float(node_position[0]) - position[0]
            dy = float(node_position[1]) - position[1]
            distance = dx * dx + dy * dy
            if distance <= best_distance:
                selected_id = str(node_id)
                best_distance = distance

        self.select_node_by_id(selected_id)
        return selected_id

    def _apply_graph_style(self) -> None:
        pos_array = np.array(self._render_data["positions"], dtype=float)
        adj = self._render_data["adj"]
        adj_array = np.array(adj, dtype=int) if adj else np.empty((0, 2), dtype=int)
        sizes = list(self._render_data["sizes"])
        brushes = list(self._render_data["brushes"])
        node_ids = list(self._render_data.get("node_ids", []))
        neighbor_ids = self._neighbor_node_ids()
        for index, node_id in enumerate(node_ids):
            if node_id in neighbor_ids:
                sizes[index] = float(sizes[index]) + 4.0
                brushes[index] = pg.mkBrush("#facc15")
        if self._selected_node_id in node_ids:
            selected_index = node_ids.index(self._selected_node_id)
            sizes[selected_index] = float(sizes[selected_index]) + 8.0
            brushes[selected_index] = pg.mkBrush("#f59e0b")

        self.graph_item.setData(
            pos=pos_array,
            adj=adj_array,
            size=np.array(sizes, dtype=float),
            symbol="o",
            pxMode=True,
            pen=pg.mkPen(100, 116, 139, 80, width=0.6),
            symbolPen=None,
            symbolBrush=brushes,
        )

    def _neighbor_node_ids(self) -> set[str]:
        node_ids = list(self._render_data.get("node_ids", []))
        if self._selected_node_id not in node_ids:
            return set()

        selected_index = node_ids.index(self._selected_node_id)
        neighbors = set()
        for source_index, target_index in self._render_data.get("adj", []):
            if source_index == selected_index and 0 <= target_index < len(node_ids):
                neighbors.add(node_ids[target_index])
            if target_index == selected_index and 0 <= source_index < len(node_ids):
                neighbors.add(node_ids[source_index])
        return neighbors

    def _center_on_selected_node(self) -> None:
        node_ids = list(self._render_data.get("node_ids", []))
        positions = list(self._render_data.get("positions", []))
        if self._selected_node_id not in node_ids or not positions:
            return

        selected_index = node_ids.index(self._selected_node_id)
        center_x, center_y = positions[selected_index]
        x_range, y_range = self.getViewBox().viewRange()
        width = max(abs(float(x_range[1]) - float(x_range[0])), 200.0)
        height = max(abs(float(y_range[1]) - float(y_range[0])), 200.0)
        self.getViewBox().setRange(
            xRange=(float(center_x) - width / 2.0, float(center_x) + width / 2.0),
            yRange=(float(center_y) - height / 2.0, float(center_y) + height / 2.0),
            padding=0.0,
        )

    @property
    def selected_node_id(self) -> str | None:
        return self._selected_node_id

    @property
    def current_render_data(self) -> dict[str, object]:
        return self._render_data
