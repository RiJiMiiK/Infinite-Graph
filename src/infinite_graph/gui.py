from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Callable

import networkx as nx
import numpy as np
import pyqtgraph as pg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QObject, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .analyzer import (
    candidate_result_weight,
    find_cheapest_combination,
    find_random_combination,
    normalize_pair,
)
from .discard_store import add_discarded_pair
from .service import process_save


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
    progress_callback: Callable[[str], None] | None = None,
) -> dict[str, object]:
    ordered_nodes = sorted(nodes, key=lambda item: str(item["id"]))
    names = [str(node["id"]) for node in ordered_nodes]
    graph = nx.DiGraph()
    graph.add_nodes_from(names)
    graph.add_edges_from((str(edge["source"]), str(edge["target"])) for edge in edges)

    total_iterations = 80
    batch_size = 5
    spring_positions = None
    started_at = time.perf_counter()
    for current_iteration in range(0, total_iterations, batch_size):
        iterations = min(batch_size, total_iterations - current_iteration)
        spring_positions = nx.spring_layout(
            graph,
            seed=42,
            k=None if len(names) < 2 else 1.2 / np.sqrt(len(names)),
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
            progress_callback(
                f"Computing spring layout: {completed}/{total_iterations} iterations "
                f"(elapsed {elapsed:.1f}s, ETA {eta:.1f}s)"
            )

    assert spring_positions is not None
    positions = [
        (
            float(spring_positions[name][0] * 2000.0),
            float(spring_positions[name][1] * 2000.0),
        )
        for name in names
    ]

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
    }


class GraphViewWidget(pg.PlotWidget):
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

    def update_graph(self, render_data: dict[str, object]) -> None:
        self.clear()
        self.addItem(self.graph_item)
        for label in self._labels:
            self.removeItem(label)
        self._labels = []

        positions = render_data["positions"]
        if not positions:
            return

        pos_array = np.array(positions, dtype=float)
        adj = render_data["adj"]
        adj_array = np.array(adj, dtype=int) if adj else np.empty((0, 2), dtype=int)

        self.graph_item.setData(
            pos=pos_array,
            adj=adj_array,
            size=np.array(render_data["sizes"], dtype=float),
            symbol="o",
            pxMode=True,
            pen=pg.mkPen(100, 116, 139, 80, width=0.6),
            symbolPen=None,
            symbolBrush=render_data["brushes"],
        )

        for label in render_data["labels"]:
            text_item = pg.TextItem(label["text"], color="#0f172a", anchor=(0.5, 1.2))
            text_item.setPos(label["x"], label["y"])
            self.addItem(text_item)
            self._labels.append(text_item)

        self.autoRange()


class GenerateWorker(QObject):
    progress = Signal(str)
    finished = Signal(dict, dict)
    failed = Signal(str)

    def __init__(self, input_path: str, focus_element: str | None) -> None:
        super().__init__()
        self.input_path = input_path
        self.focus_element = focus_element

    def run(self) -> None:
        try:
            self.progress.emit("Loading save file")
            result = process_save(
                Path(self.input_path),
                focus_element=self.focus_element,
                progress_callback=self.progress.emit,
            )
            render_data = build_graph_render_data(
                result["graph_nodes"],
                result["graph_edges"],
                progress_callback=self.progress.emit,
            )
            self.progress.emit("Preparing interface update")
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result, render_data)


class InfiniteGraphWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Infinite Graph")
        self.resize(1480, 940)

        self.input_edit = QLineEdit()
        self.focus_edit = QLineEdit()
        self.element1_edit = CopyLineEdit()
        self.element2_edit = CopyLineEdit()
        self.generate_button = QPushButton("Generer")
        self.random_button = QPushButton("Random")
        self.cheapest_button = QPushButton("Cheapest")
        self.done_button = QPushButton("Done")
        self.discard_button = QPushButton("Discard")
        self.progress_bar = QProgressBar()
        self.summary_label = QLabel(
            "Charge une sauvegarde Infinite Craft pour construire le graphe."
        )
        self.summary_label.setWordWrap(True)
        self.stage_label = QLabel("Idle")

        self.graph_view = GraphViewWidget()
        self.node_model = ListTableModel(["Element", "Poids"])
        self.edge_model = ListTableModel(["Source", "Cible", "Poids", "Liste d'elements"])
        self.node_table = QTableView()
        self.edge_table = QTableView()
        self.stats_canvas = StatsCanvas()
        self.missing_weight_list = QListWidget()
        self._worker_thread: QThread | None = None
        self._worker: GenerateWorker | None = None
        self._current_result: dict[str, object] | None = None
        self._current_save_path: Path | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        controls = QWidget()
        controls_layout = QFormLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        file_row = QWidget()
        file_row_layout = QHBoxLayout(file_row)
        file_row_layout.setContentsMargins(0, 0, 0, 0)
        browse_button = QPushButton("Parcourir")
        browse_button.clicked.connect(self._pick_input)
        file_row_layout.addWidget(self.input_edit)
        file_row_layout.addWidget(browse_button)

        action_row = QWidget()
        action_row_layout = QHBoxLayout(action_row)
        action_row_layout.setContentsMargins(0, 0, 0, 0)
        self.generate_button.clicked.connect(self._generate)
        self.random_button.clicked.connect(self._pick_random_combination)
        self.cheapest_button.clicked.connect(self._pick_cheapest_combination)
        self.done_button.clicked.connect(self._mark_current_combination_done)
        self.discard_button.clicked.connect(self._discard_current_combination)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedWidth(220)
        action_row_layout.addWidget(self.generate_button)
        action_row_layout.addWidget(self.progress_bar)
        action_row_layout.addStretch(1)

        candidate_row = QWidget()
        candidate_row_layout = QHBoxLayout(candidate_row)
        candidate_row_layout.setContentsMargins(0, 0, 0, 0)
        self.element1_edit.setPlaceholderText("Element 1")
        self.element2_edit.setPlaceholderText("Element 2")
        self.element1_edit.setReadOnly(False)
        self.element2_edit.setReadOnly(False)
        self.element1_edit.setClearButtonEnabled(True)
        self.element2_edit.setClearButtonEnabled(True)
        candidate_row_layout.addWidget(self.element1_edit)
        candidate_row_layout.addWidget(self.element2_edit)
        candidate_row_layout.addWidget(self.random_button)
        candidate_row_layout.addWidget(self.cheapest_button)
        candidate_row_layout.addWidget(self.done_button)
        candidate_row_layout.addWidget(self.discard_button)

        controls_layout.addRow("Sauvegarde", file_row)
        controls_layout.addRow("Element cible", self.focus_edit)
        controls_layout.addRow("Element 1 / Element 2", candidate_row)
        controls_layout.addRow("", action_row)

        layout.addWidget(controls)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.stage_label)

        tabs = QTabWidget()
        tabs.addTab(self._build_graph_tab(), "Graphe")
        tabs.addTab(self._build_info_tab(), "Infos")
        tabs.addTab(self._build_stats_tab(), "Statistiques")
        layout.addWidget(tabs, 1)

        self.setCentralWidget(central)
        self._set_candidate_buttons_enabled(False)

    def _build_graph_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.graph_view)
        return tab

    def _build_info_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)
        self.node_table.setModel(self.node_model)
        self.edge_table.setModel(self.edge_model)
        self.node_table.setSortingEnabled(True)
        self.edge_table.setSortingEnabled(True)
        self.node_table.horizontalHeader().setStretchLastSection(True)
        self.edge_table.horizontalHeader().setStretchLastSection(True)
        splitter.addWidget(self.node_table)
        splitter.addWidget(self.edge_table)
        splitter.setSizes([400, 900])
        layout.addWidget(splitter)
        return tab

    def _build_stats_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stats_canvas, 2)
        layout.addWidget(self.missing_weight_list, 1)
        return tab

    def _pick_input(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir une sauvegarde Infinite Craft",
            "",
            "Tous les fichiers (*);;JSON (*.json)",
        )
        if path:
            self.input_edit.setText(path)

    def _generate(self) -> None:
        input_value = self.input_edit.text().strip()
        if not input_value:
            QMessageBox.critical(self, "Erreur", "Choisis un fichier de sauvegarde.")
            return

        if self._worker_thread is not None:
            return

        self.generate_button.setEnabled(False)
        self._set_candidate_buttons_enabled(False)
        self.progress_bar.setVisible(True)
        self.summary_label.setText("Generation en cours...")
        self.stage_label.setText("Current step: starting")

        self._worker_thread = QThread(self)
        self._worker = GenerateWorker(input_value, self.focus_edit.text().strip() or None)
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_generation_progress)
        self._worker.finished.connect(self._on_generation_finished)
        self._worker.failed.connect(self._on_generation_failed)
        self._worker.finished.connect(self._cleanup_worker)
        self._worker.failed.connect(self._cleanup_worker)
        self._worker_thread.start()

    def _on_generation_progress(self, message: str) -> None:
        self.stage_label.setText(f"Current step: {message}")

    def _on_generation_finished(self, result: dict, render_data: dict) -> None:
        self._current_result = result
        self._current_save_path = Path(self.input_edit.text().strip())
        self._set_candidate_buttons_enabled(True)
        self.graph_view.update_graph(render_data)

        node_rows = []
        for node in sorted(
            result["graph_nodes"],
            key=lambda item: (
                item["weight"] is None,
                item["weight"] if item["weight"] is not None else 10**9,
                item["label"],
            ),
        ):
            node_rows.append([node["label"], "?" if node["weight"] is None else node["weight"]])
        self.node_model.update_rows(node_rows)

        edge_rows = []
        for edge in sorted(
            result["graph_edges"],
            key=lambda item: (-int(item["weight"]), item["source"], item["target"]),
        ):
            edge_rows.append(
                [
                    edge["source"],
                    edge["target"],
                    edge["weight"],
                    ", ".join(edge["elements"]),
                ]
            )
        self.edge_model.update_rows(edge_rows)

        statistics = result["statistics"]
        self.stats_canvas.update_series(
            statistics["recipe_counts_by_result_weight"],
            statistics["node_counts_by_weight"],
        )
        self.missing_weight_list.clear()
        for weight, count in statistics["missing_counts_by_result_weight"]:
            self.missing_weight_list.addItem(
                f"Poids {weight}: {count} recipes non faites possibles"
            )

        self.summary_label.setText(
            "\n".join(
                [
                    f"Elements charges : {len(result['elements'])}",
                    f"Recettes chargees : {len(result['recipes'])}",
                    f"Entrees element ignorees : {result['ignored_element_entries']}",
                    f"Entrees item ignorees : {result['ignored_item_entries']}",
                    f"Entrees recette ignorees : {result['ignored_recipe_entries']}",
                    f"Noeuds du graphe : {len(result['graph_nodes'])}",
                    f"Edges du graphe : {len(result['graph_edges'])}",
                    f"Combinaisons manquantes calculees : {len(result['missing'])}",
                    f"Combinaisons discardees : {len(result['discarded_pairs'])}",
                    f"Combinaisons done session : {len(result['done_pairs'])}",
                    f"Element cible : {result['focus_element'] or 'aucun'}",
                ]
            )
        )
        if result["load_warnings"]:
            self.stage_label.setText(
                "Current step: done with warnings - " + " | ".join(result["load_warnings"])
            )
        else:
            self.stage_label.setText("Current step: done")

    def _on_generation_failed(self, message: str) -> None:
        self.summary_label.setText("La generation a echoue.")
        self.stage_label.setText("Current step: failed")
        self._set_candidate_buttons_enabled(False)
        QMessageBox.critical(self, "Erreur", message)

    def _cleanup_worker(self) -> None:
        self.generate_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        if self._worker_thread is not None:
            self._worker_thread.quit()
            self._worker_thread.wait()
        self._worker_thread = None
        self._worker = None

    def _set_candidate_buttons_enabled(self, enabled: bool) -> None:
        self.random_button.setEnabled(enabled)
        self.cheapest_button.setEnabled(enabled)
        self.done_button.setEnabled(enabled)
        self.discard_button.setEnabled(enabled)

    def _pick_random_combination(self) -> None:
        if not self._current_result:
            return
        pair = find_random_combination(
            self._current_result["elements"],
            self._current_result["recipes"],
            discarded_pairs=self._current_result["discarded_pairs"],
            done_pairs=self._current_result["done_pairs"],
        )
        if pair is None:
            QMessageBox.information(self, "Information", "Aucune combinaison non faite disponible.")
            return
        self.element1_edit.setText(pair[0])
        self.element2_edit.setText(pair[1])

    def _pick_cheapest_combination(self) -> None:
        if not self._current_result:
            return
        pair = find_cheapest_combination(
            self._current_result["elements"],
            self._current_result["recipes"],
            self._current_result["node_weights"],
            discarded_pairs=self._current_result["discarded_pairs"],
            done_pairs=self._current_result["done_pairs"],
        )
        if pair is None:
            QMessageBox.information(self, "Information", "Aucune combinaison non faite disponible.")
            return
        self.element1_edit.setText(pair[0])
        self.element2_edit.setText(pair[1])

    def _mark_current_combination_done(self) -> None:
        if not self._current_result:
            return

        left = self.element1_edit.text().strip()
        right = self.element2_edit.text().strip()
        if not left or not right:
            QMessageBox.information(
                self, "Information", "Renseigne ou genere d'abord une combinaison."
            )
            return

        if (
            left not in self._current_result["elements"]
            or right not in self._current_result["elements"]
        ):
            QMessageBox.warning(self, "Erreur", "Les elements saisis n'existent pas dans la save.")
            return

        pair = normalize_pair(left, right)
        if pair in self._current_result["known_pairs"]:
            QMessageBox.information(
                self, "Information", "Cette combinaison existe deja dans la save."
            )
            return
        if pair in self._current_result["discarded_pairs"]:
            QMessageBox.information(self, "Information", "Cette combinaison est discardee.")
            return
        if pair in self._current_result["done_pairs"]:
            QMessageBox.information(
                self, "Information", "Cette combinaison est deja marquee done pour cette session."
            )
            return

        self._current_result["done_pairs"].add(pair)
        self._current_result["missing"] = [
            item for item in self._current_result["missing"] if item != pair
        ]
        self.summary_label.setText(
            "\n".join(
                [
                    f"Elements charges : {len(self._current_result['elements'])}",
                    f"Recettes chargees : {len(self._current_result['recipes'])}",
                    f"Entrees element ignorees : {self._current_result['ignored_element_entries']}",
                    f"Entrees item ignorees : {self._current_result['ignored_item_entries']}",
                    f"Entrees recette ignorees : {self._current_result['ignored_recipe_entries']}",
                    f"Noeuds du graphe : {len(self._current_result['graph_nodes'])}",
                    f"Edges du graphe : {len(self._current_result['graph_edges'])}",
                    f"Combinaisons manquantes calculees : {len(self._current_result['missing'])}",
                    f"Combinaisons discardees : {len(self._current_result['discarded_pairs'])}",
                    f"Combinaisons done session : {len(self._current_result['done_pairs'])}",
                    f"Element cible : {self._current_result['focus_element'] or 'aucun'}",
                ]
            )
        )
        self.element1_edit.clear()
        self.element2_edit.clear()

    def _discard_current_combination(self) -> None:
        if not self._current_result or self._current_save_path is None:
            return

        left = self.element1_edit.text().strip()
        right = self.element2_edit.text().strip()
        if not left or not right:
            QMessageBox.information(
                self, "Information", "Renseigne ou genere d'abord une combinaison."
            )
            return

        if (
            left not in self._current_result["elements"]
            or right not in self._current_result["elements"]
        ):
            QMessageBox.warning(self, "Erreur", "Les elements saisis n'existent pas dans la save.")
            return

        pair = normalize_pair(left, right)
        if pair in self._current_result["known_pairs"]:
            QMessageBox.warning(self, "Erreur", "Cette combinaison existe deja dans la save.")
            return
        if pair in self._current_result["discarded_pairs"]:
            QMessageBox.information(self, "Information", "Cette combinaison est deja discardee.")
            return

        add_discarded_pair(self._current_save_path, pair)
        self._current_result["discarded_pairs"].add(pair)
        self._current_result["missing"] = [
            item for item in self._current_result["missing"] if item != pair
        ]

        target_weight = candidate_result_weight(
            pair[0], pair[1], self._current_result["node_weights"]
        )
        if target_weight is not None:
            updated = []
            found = False
            for weight, count in self._current_result["statistics"][
                "missing_counts_by_result_weight"
            ]:
                if weight == target_weight:
                    found = True
                    if count > 1:
                        updated.append((weight, count - 1))
                else:
                    updated.append((weight, count))
            if not found:
                updated = self._current_result["statistics"]["missing_counts_by_result_weight"]
            self._current_result["statistics"]["missing_counts_by_result_weight"] = updated
            self.missing_weight_list.clear()
            for weight, count in updated:
                self.missing_weight_list.addItem(
                    f"Poids {weight}: {count} recipes non faites possibles"
                )

        self.summary_label.setText(
            "\n".join(
                [
                    f"Elements charges : {len(self._current_result['elements'])}",
                    f"Recettes chargees : {len(self._current_result['recipes'])}",
                    f"Entrees element ignorees : {self._current_result['ignored_element_entries']}",
                    f"Entrees item ignorees : {self._current_result['ignored_item_entries']}",
                    f"Entrees recette ignorees : {self._current_result['ignored_recipe_entries']}",
                    f"Noeuds du graphe : {len(self._current_result['graph_nodes'])}",
                    f"Edges du graphe : {len(self._current_result['graph_edges'])}",
                    f"Combinaisons manquantes calculees : {len(self._current_result['missing'])}",
                    f"Combinaisons discardees : {len(self._current_result['discarded_pairs'])}",
                    f"Combinaisons done session : {len(self._current_result['done_pairs'])}",
                    f"Element cible : {self._current_result['focus_element'] or 'aucun'}",
                ]
            )
        )
        self.element1_edit.clear()
        self.element2_edit.clear()
        QMessageBox.information(
            self, "Information", f"Combinaison discardee: {pair[0]} + {pair[1]}"
        )


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    window = InfiniteGraphWindow()
    window.show()
    app.exec()
