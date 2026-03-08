"""Qt GUI for browsing and analyzing Infinite Craft saves."""

from __future__ import annotations

import sys
import time
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, QStringListModel, Signal
from PySide6.QtWidgets import (
    QApplication, QCompleter, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QMainWindow, QMessageBox, QProgressBar, QPushButton, QSplitter,
    QTableView, QTabWidget, QTextEdit, QVBoxLayout, QWidget,
)

from .analyzer import (
    candidate_result_weight,
    find_cheapest_combination,
    find_random_combination,
    normalize_pair,
)
from .discard_store import add_discarded_pair, remove_discarded_pair
from .service import process_save
from .gui_support import (
    GENERATION_STAGE_PROGRESS,
    INTERFACE_PROGRESS,
    LAYOUT_PROGRESS_END,
    CopyLineEdit,
    GraphViewWidget,
    ListTableModel,
    StatsCanvas,
    _layout_cache_file,
    build_graph_render_data,
    build_subgraph_render_data,
    build_weight_filtered_render_data,
    layout_cache_dir,
    load_cached_layout,
    nx,
    pg,
    save_cached_layout,
)

__all__ = ["CopyLineEdit", "GENERATION_STAGE_PROGRESS", "GenerateWorker", "GraphViewWidget"]
__all__ += ["INTERFACE_PROGRESS", "LAYOUT_PROGRESS_END", "InfiniteGraphWindow", "ListTableModel"]
__all__ += ["StatsCanvas", "_layout_cache_file", "build_graph_render_data"]
__all__ += ["build_subgraph_render_data", "build_weight_filtered_render_data", "layout_cache_dir"]
__all__ += ["load_cached_layout", "main", "nx", "pg", "save_cached_layout"]
PUBLIC_REEXPORTS = (LAYOUT_PROGRESS_END, _layout_cache_file, layout_cache_dir)
PUBLIC_REEXPORTS += (load_cached_layout, nx, pg, save_cached_layout)

class GenerateWorker(QObject):
    progress = Signal(int, str)
    finished = Signal(dict, dict, float)
    failed = Signal(str)

    def __init__(
        self,
        input_path: str,
        focus_element: str | None,
        layout_iterations: int,
        spring_scale: float,
    ) -> None:
        super().__init__()
        self.input_path = input_path
        self.focus_element = focus_element
        self.layout_iterations = layout_iterations
        self.spring_scale = spring_scale

    def run(self) -> None:
        started_at = time.perf_counter()
        try:
            self.progress.emit(0, "Starting generation")

            def emit_process_progress(message: str) -> None:
                self.progress.emit(GENERATION_STAGE_PROGRESS.get(message, 0), message)

            result = process_save(
                Path(self.input_path),
                focus_element=self.focus_element,
                progress_callback=emit_process_progress,
            )
            render_data = build_graph_render_data(
                result["graph_nodes"],
                result["graph_edges"],
                progress_callback=self.progress.emit,
                layout_iterations=self.layout_iterations,
                spring_scale=self.spring_scale,
                cache_save_path=Path(self.input_path),
            )
            self.progress.emit(
                GENERATION_STAGE_PROGRESS["Preparing interface update"],
                "Preparing interface update",
            )
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result, render_data, time.perf_counter() - started_at)

class InfiniteGraphWindow(QMainWindow):  # pylint: disable=too-many-instance-attributes
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Infinite Graph")
        self.resize(1480, 940)

        self.input_edit = QLineEdit()
        self.focus_edit = QLineEdit()
        self.element1_edit = CopyLineEdit()
        self.element2_edit = CopyLineEdit()
        self.element_completer_model = QStringListModel()
        self.element1_completer = QCompleter(self.element_completer_model, self)
        self.element2_completer = QCompleter(self.element_completer_model, self)
        self.generate_button = QPushButton("Generer")
        self.random_button = QPushButton("Random")
        self.cheapest_button = QPushButton("Cheapest")
        self.done_button = QPushButton("Done")
        self.undo_done_button = QPushButton("Undo Done")
        self.discard_button = QPushButton("Discard")
        self.undo_discard_button = QPushButton("Undo Discard")
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
        self.selected_node_label = QLabel("Noeud selectionne : aucun")
        self.selected_node_details = QTextEdit()
        self.graph_search_edit = QLineEdit()
        self.graph_search_button = QPushButton("Rechercher")
        self.subgraph_center_edit = QLineEdit()
        self.subgraph_depth_edit = QLineEdit("1")
        self.subgraph_button = QPushButton("Sous-graphe")
        self.subgraph_reset_button = QPushButton("Reinitialiser")
        self.min_weight_edit = QLineEdit()
        self.max_weight_edit = QLineEdit()
        self.weight_filter_button = QPushButton("Filtrer poids")
        self.layout_iterations_edit = QLineEdit("80")
        self.layout_scale_edit = QLineEdit("1.2")
        self.layout_apply_button = QPushButton("Appliquer layout")
        self._worker_thread: QThread | None = None
        self._worker: GenerateWorker | None = None
        self._current_result: dict[str, object] | None = None
        self._current_save_path: Path | None = None
        self._full_render_data: dict[str, object] | None = None
        self._last_generation_elapsed_seconds = 0.0

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
        self.undo_done_button.clicked.connect(self._undo_current_combination_done)
        self.discard_button.clicked.connect(self._discard_current_combination)
        self.undo_discard_button.clicked.connect(self._undo_current_combination_discard)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
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
        self._configure_element_completer(self.element1_completer)
        self._configure_element_completer(self.element2_completer)
        self.element1_edit.setCompleter(self.element1_completer)
        self.element2_edit.setCompleter(self.element2_completer)
        candidate_row_layout.addWidget(self.element1_edit)
        candidate_row_layout.addWidget(self.element2_edit)
        candidate_row_layout.addWidget(self.random_button)
        candidate_row_layout.addWidget(self.cheapest_button)
        candidate_row_layout.addWidget(self.done_button)
        candidate_row_layout.addWidget(self.undo_done_button)
        candidate_row_layout.addWidget(self.discard_button)
        candidate_row_layout.addWidget(self.undo_discard_button)

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
        self._update_element_completion([])

    @staticmethod
    def _configure_element_completer(completer: QCompleter) -> None:
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setFilterMode(Qt.MatchContains)

    def _update_element_completion(self, elements: list[str]) -> None:
        self.element_completer_model.setStringList(sorted(elements, key=str.casefold))

    def _build_graph_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        self.graph_view.nodeSelected.connect(self._on_graph_node_selected)
        search_row = QWidget()
        search_layout = QHBoxLayout(search_row)
        search_layout.setContentsMargins(0, 0, 0, 0)
        self.graph_search_edit.setPlaceholderText("Rechercher un element dans le graphe")
        self.graph_search_button.clicked.connect(self._search_graph_node)
        search_layout.addWidget(self.graph_search_edit)
        search_layout.addWidget(self.graph_search_button)

        subgraph_row = QWidget()
        subgraph_layout = QHBoxLayout(subgraph_row)
        subgraph_layout.setContentsMargins(0, 0, 0, 0)
        self.subgraph_center_edit.setPlaceholderText("Centre du sous-graphe")
        self.subgraph_depth_edit.setPlaceholderText("Profondeur")
        self.subgraph_depth_edit.setFixedWidth(90)
        self.subgraph_button.clicked.connect(self._apply_subgraph_filter)
        self.subgraph_reset_button.clicked.connect(self._reset_subgraph_filter)
        subgraph_layout.addWidget(self.subgraph_center_edit)
        subgraph_layout.addWidget(self.subgraph_depth_edit)
        subgraph_layout.addWidget(self.subgraph_button)
        subgraph_layout.addWidget(self.subgraph_reset_button)

        weight_row = QWidget()
        weight_layout = QHBoxLayout(weight_row)
        weight_layout.setContentsMargins(0, 0, 0, 0)
        self.min_weight_edit.setPlaceholderText("Poids min")
        self.max_weight_edit.setPlaceholderText("Poids max")
        self.min_weight_edit.setFixedWidth(120)
        self.max_weight_edit.setFixedWidth(120)
        self.weight_filter_button.clicked.connect(self._apply_weight_filter)
        weight_layout.addWidget(self.min_weight_edit)
        weight_layout.addWidget(self.max_weight_edit)
        weight_layout.addWidget(self.weight_filter_button)
        weight_layout.addStretch(1)

        layout_row = QWidget()
        layout_controls = QHBoxLayout(layout_row)
        layout_controls.setContentsMargins(0, 0, 0, 0)
        self.layout_iterations_edit.setPlaceholderText("Iterations")
        self.layout_scale_edit.setPlaceholderText("Spring scale")
        self.layout_iterations_edit.setFixedWidth(120)
        self.layout_scale_edit.setFixedWidth(120)
        self.layout_apply_button.clicked.connect(self._rebuild_layout)
        layout_controls.addWidget(self.layout_iterations_edit)
        layout_controls.addWidget(self.layout_scale_edit)
        layout_controls.addWidget(self.layout_apply_button)
        layout_controls.addStretch(1)

        self.selected_node_details.setReadOnly(True)
        self.selected_node_details.setMinimumWidth(280)
        self.selected_node_details.setPlainText("Aucun noeud selectionne.")

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.graph_view)

        details_container = QWidget()
        details_layout = QVBoxLayout(details_container)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.addWidget(self.selected_node_label)
        details_layout.addWidget(self.selected_node_details, 1)
        splitter.addWidget(details_container)
        splitter.setSizes([1100, 320])

        layout.addWidget(search_row)
        layout.addWidget(subgraph_row)
        layout.addWidget(weight_row)
        layout.addWidget(layout_row)
        layout.addWidget(splitter)
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
        self.progress_bar.setValue(0)
        self.summary_label.setText("Generation en cours...")
        self.stage_label.setText("Current step: Starting generation (0%)")
        try:
            layout_iterations, spring_scale = self._layout_settings()
        except ValueError as exc:
            self.generate_button.setEnabled(True)
            self.progress_bar.setVisible(False)
            QMessageBox.information(self, "Information", str(exc))
            return

        self._worker_thread = QThread(self)
        self._worker = GenerateWorker(
            input_value,
            self.focus_edit.text().strip() or None,
            layout_iterations,
            spring_scale,
        )
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_generation_progress)
        self._worker.finished.connect(self._on_generation_finished)
        self._worker.failed.connect(self._on_generation_failed)
        self._worker.finished.connect(self._cleanup_worker)
        self._worker.failed.connect(self._cleanup_worker)
        self._worker_thread.start()

    def _on_generation_progress(self, percent: int, message: str) -> None:
        bounded_percent = max(0, min(100, percent))
        self.progress_bar.setValue(bounded_percent)
        self.stage_label.setText(f"Current step: {message} ({bounded_percent}%)")

    def _on_generation_finished(
        self,
        result: dict,
        render_data: dict,
        elapsed_seconds: float = 0.0,
    ) -> None:
        self._current_result = result
        self._current_save_path = Path(self.input_edit.text().strip())
        self._full_render_data = render_data
        self._last_generation_elapsed_seconds = max(0.0, float(elapsed_seconds))
        self._update_element_completion([str(element) for element in result["elements"]])
        self._set_candidate_buttons_enabled(True)
        self._on_generation_progress(
            INTERFACE_PROGRESS["Updating graph view"],
            "Updating graph view",
        )
        self.graph_view.update_graph(render_data)
        self.selected_node_label.setText("Noeud selectionne : aucun")
        self.selected_node_details.setPlainText("Aucun noeud selectionne.")
        self.subgraph_center_edit.clear()
        self.subgraph_depth_edit.setText("1")

        self._on_generation_progress(
            INTERFACE_PROGRESS["Updating node table"],
            "Updating node table",
        )
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

        self._on_generation_progress(
            INTERFACE_PROGRESS["Updating edge table"],
            "Updating edge table",
        )
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
        self._on_generation_progress(
            INTERFACE_PROGRESS["Updating statistics"],
            "Updating statistics",
        )
        self.stats_canvas.update_series(
            statistics["recipe_counts_by_result_weight"],
            statistics["node_counts_by_weight"],
        )
        self.missing_weight_list.clear()
        for weight, count in statistics["missing_counts_by_result_weight"]:
            self.missing_weight_list.addItem(
                f"Poids {weight}: {count} recipes non faites possibles"
            )

        self._on_generation_progress(
            INTERFACE_PROGRESS["Updating summary"],
            "Updating summary",
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
                    f"Temps total de generation : {self._last_generation_elapsed_seconds:.2f}s",
                ]
            )
        )
        self.progress_bar.setValue(100)
        if result["load_warnings"]:
            self.stage_label.setText(
                "Current step: done with warnings "
                f"(100%, {self._last_generation_elapsed_seconds:.2f}s) - "
                + " | ".join(result["load_warnings"])
            )
        else:
            self.stage_label.setText(
                f"Current step: done (100%, {self._last_generation_elapsed_seconds:.2f}s)"
            )

    def _on_generation_failed(self, message: str) -> None:
        self.summary_label.setText("La generation a echoue.")
        self.progress_bar.setValue(0)
        self.stage_label.setText("Current step: failed (0%)")
        self._update_element_completion([])
        self._set_candidate_buttons_enabled(False)
        QMessageBox.critical(self, "Erreur", message)

    def _cleanup_worker(self) -> None:
        self.generate_button.setEnabled(True)
        self.progress_bar.setValue(0)
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
        self.undo_done_button.setEnabled(enabled)
        self.discard_button.setEnabled(enabled)
        self.undo_discard_button.setEnabled(enabled)

    def _refresh_missing_weight_list(self) -> None:
        if not self._current_result:
            return

        self.missing_weight_list.clear()
        for weight, count in self._current_result["statistics"]["missing_counts_by_result_weight"]:
            self.missing_weight_list.addItem(
                f"Poids {weight}: {count} recipes non faites possibles"
            )

    def _refresh_summary(self) -> None:
        if not self._current_result:
            return

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

    def _update_missing_statistics_for_pair(self, pair: tuple[str, str], delta: int) -> None:
        if not self._current_result:
            return

        target_weight = candidate_result_weight(
            pair[0], pair[1], self._current_result["node_weights"]
        )
        if target_weight is None:
            return

        updated = []
        found = False
        for weight, count in self._current_result["statistics"]["missing_counts_by_result_weight"]:
            if weight == target_weight:
                found = True
                new_count = count + delta
                if new_count > 0:
                    updated.append((weight, new_count))
            else:
                updated.append((weight, count))
        if not found and delta > 0:
            updated.append((target_weight, delta))
        self._current_result["statistics"]["missing_counts_by_result_weight"] = sorted(updated)
        self._refresh_missing_weight_list()

    def _on_graph_node_selected(self, node_id: object) -> None:
        node_name = str(node_id) if node_id is not None else ""
        if not node_name:
            self.selected_node_label.setText("Noeud selectionne : aucun")
            self.selected_node_details.setPlainText("Aucun noeud selectionne.")
            self.node_table.clearSelection()
            return

        self.selected_node_label.setText(f"Noeud selectionne : {node_name}")
        self.selected_node_details.setPlainText(self._build_selected_node_details(node_name))
        for row_index, row in enumerate(self.node_model.rows):
            if row[0] == node_name:
                self.node_table.selectRow(row_index)
                self.node_table.scrollTo(self.node_model.index(row_index, 0))
                break

    def _search_graph_node(self) -> None:
        if not self._current_result:
            return

        query = self.graph_search_edit.text().strip()
        if not query:
            QMessageBox.information(self, "Information", "Saisis un element a rechercher.")
            return

        normalized_query = query.casefold()
        for node in self._current_result["graph_nodes"]:
            node_name = str(node["label"])
            if node_name.casefold() == normalized_query:
                self.graph_search_edit.setText(node_name)
                self.graph_view.select_node_by_id(node_name)
                return

        QMessageBox.information(
            self,
            "Information",
            f"Element introuvable dans le graphe : {query}",
        )

    def _apply_subgraph_filter(self) -> None:
        if not self._current_result or not self._full_render_data:
            return

        center_node = self.subgraph_center_edit.text().strip()
        if not center_node:
            center_node = self.graph_view.selected_node_id or ""
            if center_node:
                self.subgraph_center_edit.setText(center_node)
        if not center_node:
            QMessageBox.information(
                self,
                "Information",
                "Saisis un centre de sous-graphe ou selectionne un noeud.",
            )
            return

        depth_text = self.subgraph_depth_edit.text().strip() or "1"
        if not depth_text.isdigit():
            QMessageBox.information(
                self,
                "Information",
                "La profondeur du sous-graphe doit etre un entier positif ou nul.",
            )
            return

        filtered = build_subgraph_render_data(
            self._full_render_data,
            center_node,
            int(depth_text),
        )
        if filtered is None:
            QMessageBox.information(
                self,
                "Information",
                f"Impossible de construire un sous-graphe pour : {center_node}",
            )
            return

        self.graph_view.update_graph(filtered)
        self.graph_view.select_node_by_id(center_node)

    def _reset_subgraph_filter(self) -> None:
        if not self._full_render_data:
            return
        self.graph_view.update_graph(self._full_render_data)

    def _apply_weight_filter(self) -> None:
        current_render = self.graph_view.current_render_data or self._full_render_data
        if not current_render:
            return

        min_text = self.min_weight_edit.text().strip()
        max_text = self.max_weight_edit.text().strip()
        if not min_text and not max_text:
            QMessageBox.information(
                self,
                "Information",
                "Saisis au moins un poids minimal ou maximal.",
            )
            return

        if (min_text and not min_text.isdigit()) or (max_text and not max_text.isdigit()):
            QMessageBox.information(
                self,
                "Information",
                "Les poids min et max doivent etre des entiers positifs ou nuls.",
            )
            return

        min_weight = int(min_text) if min_text else None
        max_weight = int(max_text) if max_text else None
        if (
            min_weight is not None
            and max_weight is not None
            and min_weight > max_weight
        ):
            QMessageBox.information(
                self,
                "Information",
                "Le poids minimal ne peut pas etre superieur au poids maximal.",
            )
            return

        filtered = build_weight_filtered_render_data(
            current_render,
            min_weight,
            max_weight,
        )
        self.graph_view.update_graph(filtered)

    def _layout_settings(self) -> tuple[int, float]:
        iterations_text = self.layout_iterations_edit.text().strip() or "80"
        scale_text = self.layout_scale_edit.text().strip() or "1.2"
        if not iterations_text.isdigit():
            raise ValueError("Les iterations du layout doivent etre un entier positif.")
        try:
            spring_scale = float(scale_text)
        except ValueError as exc:
            raise ValueError("Le spring scale du layout doit etre un nombre positif.") from exc

        layout_iterations = int(iterations_text)
        if layout_iterations <= 0:
            raise ValueError("Les iterations du layout doivent etre un entier positif.")
        if spring_scale <= 0:
            raise ValueError("Le spring scale du layout doit etre un nombre positif.")
        return layout_iterations, spring_scale

    def _rebuild_layout(self) -> None:
        if not self._current_result:
            return
        try:
            layout_iterations, spring_scale = self._layout_settings()
        except ValueError as exc:
            QMessageBox.information(self, "Information", str(exc))
            return

        self.stage_label.setText("Current step: recomputing layout")
        render_data = build_graph_render_data(
            self._current_result["graph_nodes"],
            self._current_result["graph_edges"],
            layout_iterations=layout_iterations,
            spring_scale=spring_scale,
            cache_save_path=self._current_save_path,
        )
        self._full_render_data = render_data
        self.graph_view.update_graph(render_data)
        self.selected_node_label.setText("Noeud selectionne : aucun")
        self.selected_node_details.setPlainText("Aucun noeud selectionne.")
        self.stage_label.setText("Current step: done")

    def _build_selected_node_details(self, node_name: str) -> str:
        if not self._current_result:
            return f"Nom : {node_name}"

        node_data = next(
            (
                node
                for node in self._current_result["graph_nodes"]
                if str(node["id"]) == node_name
            ),
            None,
        )
        incoming: list[str] = []
        outgoing: list[str] = []
        related_edges: list[str] = []
        for edge in self._current_result["graph_edges"]:
            if edge["target"] == node_name:
                incoming.append(str(edge["source"]))
                edge_text = ", ".join(edge["elements"])
                related_edges.append(
                    f"{edge['source']} -> {edge['target']} (co-elements: {edge_text})"
                )
            elif edge["source"] == node_name:
                outgoing.append(str(edge["target"]))
                edge_text = ", ".join(edge["elements"])
                related_edges.append(
                    f"{edge['source']} -> {edge['target']} (co-elements: {edge_text})"
                )

        lines = [f"Nom : {node_name}"]
        if node_data is not None:
            lines.append(f"Poids : {'?' if node_data['weight'] is None else node_data['weight']}")
            lines.append(f"Starter : {'oui' if node_data['is_starter'] else 'non'}")
        lines.append(f"Voisins entrants : {', '.join(sorted(set(incoming))) or 'aucun'}")
        lines.append(f"Voisins sortants : {', '.join(sorted(set(outgoing))) or 'aucun'}")
        lines.append(f"Edges liees : {len(related_edges)}")
        if related_edges:
            lines.append("")
            lines.extend(related_edges[:20])
        return "\n".join(lines)

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
        self._update_missing_statistics_for_pair(pair, -1)
        self._refresh_summary()
        self.element1_edit.clear()
        self.element2_edit.clear()

    def _undo_current_combination_done(self) -> None:
        if not self._current_result:
            return

        left = self.element1_edit.text().strip()
        right = self.element2_edit.text().strip()
        if not left or not right:
            QMessageBox.information(
                self, "Information", "Renseigne une combinaison marquee done a annuler."
            )
            return

        if (
            left not in self._current_result["elements"]
            or right not in self._current_result["elements"]
        ):
            QMessageBox.warning(self, "Erreur", "Les elements saisis n'existent pas dans la save.")
            return

        pair = normalize_pair(left, right)
        if pair not in self._current_result["done_pairs"]:
            QMessageBox.information(
                self,
                "Information",
                "Cette combinaison n'est pas marquee done pour cette session.",
            )
            return

        self._current_result["done_pairs"].remove(pair)
        if (
            pair not in self._current_result["known_pairs"]
            and pair not in self._current_result["discarded_pairs"]
            and pair not in self._current_result["missing"]
        ):
            self._current_result["missing"].append(pair)
        self._update_missing_statistics_for_pair(pair, 1)
        self._refresh_summary()
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

        self._update_missing_statistics_for_pair(pair, -1)
        self._refresh_summary()
        self.element1_edit.clear()
        self.element2_edit.clear()
        QMessageBox.information(
            self, "Information", f"Combinaison discardee: {pair[0]} + {pair[1]}"
        )

    def _undo_current_combination_discard(self) -> None:
        if not self._current_result or self._current_save_path is None:
            return

        left = self.element1_edit.text().strip()
        right = self.element2_edit.text().strip()
        if not left or not right:
            QMessageBox.information(
                self, "Information", "Renseigne une combinaison discardee a annuler."
            )
            return

        if (
            left not in self._current_result["elements"]
            or right not in self._current_result["elements"]
        ):
            QMessageBox.warning(self, "Erreur", "Les elements saisis n'existent pas dans la save.")
            return

        pair = normalize_pair(left, right)
        if pair not in self._current_result["discarded_pairs"]:
            QMessageBox.information(
                self,
                "Information",
                "Cette combinaison n'est pas discardee.",
            )
            return

        remove_discarded_pair(self._current_save_path, pair)
        self._current_result["discarded_pairs"].remove(pair)
        if (
            pair not in self._current_result["known_pairs"]
            and pair not in self._current_result["done_pairs"]
            and pair not in self._current_result["missing"]
        ):
            self._current_result["missing"].append(pair)
        self._update_missing_statistics_for_pair(pair, 1)
        self._refresh_summary()
        self.element1_edit.clear()
        self.element2_edit.clear()


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    window = InfiniteGraphWindow()
    window.show()
    app.exec()
