"""Generation lifecycle helpers for the main window."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QMessageBox

from .analyzer import candidate_result_weight
from .gui_constants import INTERFACE_PROGRESS
from .gui_state import build_summary_text, update_missing_statistics_for_pair


class WindowGenerationMixin:
    def _generate(self) -> None:
        gui_module = sys.modules[f"{__package__}.gui"]
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
        self.summary_panel.setVisible(True)
        self.summary_toggle_button.setText("Masquer details")
        self.stage_label.setText("Current step: Starting generation (0%)")
        try:
            layout_iterations, spring_scale = self._layout_settings()
        except ValueError as exc:
            self.generate_button.setEnabled(True)
            self.progress_bar.setVisible(False)
            QMessageBox.information(self, "Information", str(exc))
            return

        self._worker_thread = gui_module.QThread(self)
        self._worker = gui_module.GenerateWorker(
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
        self._last_suggestion_mode = None
        self.suggestion_history_list.clear()
        self._update_element_completion([str(element) for element in result["elements"]])
        self._validate_combination_inputs()
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
        self._refresh_discarded_table()

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
            build_summary_text(result, self._last_generation_elapsed_seconds)
        )
        self.summary_panel.setVisible(True)
        self.summary_toggle_button.setText("Masquer details")
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
        self.summary_panel.setVisible(True)
        self.summary_toggle_button.setText("Masquer details")
        self.progress_bar.setValue(0)
        self.stage_label.setText("Current step: failed (0%)")
        self._update_element_completion([])
        self._validate_combination_inputs()
        self._set_candidate_buttons_enabled(False)
        self.discarded_model.update_rows([])
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
        self.next_button.setEnabled(enabled)
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

    def _refresh_discarded_table(self) -> None:
        if not self._current_result:
            self.discarded_model.update_rows([])
            return

        rows = [list(pair) for pair in sorted(self._current_result["discarded_pairs"])]
        self.discarded_model.update_rows(rows)

    def _refresh_summary(self) -> None:
        if not self._current_result:
            return
        self.summary_label.setText(build_summary_text(self._current_result))

    def _update_missing_statistics_for_pair(self, pair: tuple[str, str], delta: int) -> None:
        if not self._current_result:
            return

        target_weight = candidate_result_weight(
            pair[0], pair[1], self._current_result["node_weights"]
        )
        update_missing_statistics_for_pair(self._current_result, delta, target_weight)
        self._refresh_missing_weight_list()

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
        gui_module = sys.modules[f"{__package__}.gui"]
        if not self._current_result:
            return
        try:
            layout_iterations, spring_scale = self._layout_settings()
        except ValueError as exc:
            QMessageBox.information(self, "Information", str(exc))
            return

        self.stage_label.setText("Current step: recomputing layout")
        render_data = gui_module.build_graph_render_data(
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
