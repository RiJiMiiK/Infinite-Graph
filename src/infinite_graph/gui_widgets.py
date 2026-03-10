"""Widget classes used by the Qt GUI."""

import numpy as np
import pyqtgraph as pg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QLineEdit


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


class GraphViewWidget(pg.PlotWidget):
    nodeSelected = Signal(object)
    contextMenuRequested = Signal(object, object)
    BACKGROUND_COLOR = "#0b1220"
    GRID_ALPHA = 0.16
    LABEL_COLOR = "#dbe4ff"
    EDGE_PEN = (148, 163, 184, 110)
    NEIGHBOR_HIGHLIGHT = "#fde047"
    SELECTED_HIGHLIGHT = "#fb923c"

    def __init__(self) -> None:
        super().__init__()
        self.setBackground(self.BACKGROUND_COLOR)
        self.showGrid(x=True, y=True, alpha=self.GRID_ALPHA)
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
            text_item = pg.TextItem(
                label["text"],
                color=self.LABEL_COLOR,
                anchor=(0.5, 1.2),
            )
            text_item.setPos(label["x"], label["y"])
            self.addItem(text_item)
            self._labels.append(text_item)

        self.autoRange()

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.LeftButton and self._render_data.get("positions"):
            scene_pos = self.mapToScene(ev.position().toPoint())
            view_pos = self.getViewBox().mapSceneToView(scene_pos)
            self.select_node_at((float(view_pos.x()), float(view_pos.y())))
        elif ev.button() == Qt.RightButton and self._render_data.get("positions"):
            scene_pos = self.mapToScene(ev.position().toPoint())
            view_pos = self.getViewBox().mapSceneToView(scene_pos)
            selected_id = self._node_id_at((float(view_pos.x()), float(view_pos.y())))
            if selected_id is not None:
                self.select_node_by_id(selected_id)
            elif self._selected_node_id is not None:
                selected_id = self._selected_node_id
            if selected_id is not None:
                self.contextMenuRequested.emit(selected_id, ev.globalPosition().toPoint())
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
        selected_id = self._node_id_at(position, max_distance=max_distance)
        self.select_node_by_id(selected_id)
        return selected_id

    def _node_id_at(
        self,
        position: tuple[float, float],
        max_distance: float = 80.0,
    ) -> str | None:
        node_ids = self._render_data.get("node_ids", [])
        positions = self._render_data.get("positions", [])
        if not node_ids or not positions:
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
                brushes[index] = pg.mkBrush(self.NEIGHBOR_HIGHLIGHT)
        if self._selected_node_id in node_ids:
            selected_index = node_ids.index(self._selected_node_id)
            sizes[selected_index] = float(sizes[selected_index]) + 8.0
            brushes[selected_index] = pg.mkBrush(self.SELECTED_HIGHLIGHT)

        self.graph_item.setData(
            pos=pos_array,
            adj=adj_array,
            size=np.array(sizes, dtype=float),
            symbol="o",
            pxMode=True,
            pen=pg.mkPen(*self.EDGE_PEN, width=0.7),
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
