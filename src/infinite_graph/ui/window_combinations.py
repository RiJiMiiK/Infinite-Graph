"""Combination suggestion helpers for the main window."""

import random
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem, QMessageBox

from ..analyzer import candidate_result_weight, normalize_pair


class WindowCombinationsMixin:
    @staticmethod
    def _show_guidance(title: str, summary: str, guidance: str) -> tuple[str, str]:
        return title, f"{summary}\n\n{guidance}"

    def _combination_known_status(self, pair: tuple[str, str]) -> str | None:
        if pair in self._current_result["known_pairs"]:
            return "Combination status: recipe already known in the save."
        if pair in self._current_result["discarded_pairs"]:
            return "Combination status: globally discarded combination."
        if pair in self._current_result["done_pairs"]:
            return "Combination status: marked done for this session."
        if pair in self._current_result["skipped_pairs"]:
            return "Combination status: postponed for later in this session."
        return None

    def _combination_status_message(self, left: str, right: str) -> str:
        if not self._current_result:
            return "Combination status: load a save to analyze a pair."
        if not left or not right:
            return "Combination status: enter or generate a combination."
        if (
            left not in self._current_result["elements"]
            or right not in self._current_result["elements"]
        ):
            return "Combination status: at least one element was not found in the save."

        pair = normalize_pair(left, right)
        known_status = self._combination_known_status(pair)
        if known_status is not None:
            return known_status
        return "Combination status: candidate still available."

    def _refresh_candidate_status(self) -> None:
        left = self.element1_edit.text().strip()
        right = self.element2_edit.text().strip()
        self.candidate_status_label.setText(self._combination_status_message(left, right))
        self.current_candidate_details.setPlainText(
            self._current_candidate_details_text(left, right)
        )

    def _current_candidate_origin_label(self, left: str, right: str) -> str:
        if not left or not right:
            return "none"
        if self._last_suggested_pair is None or self._current_candidate_origin is None:
            return "manual"
        current_pair = normalize_pair(left, right)
        if current_pair != self._last_suggested_pair:
            return "manual"
        return self._current_candidate_origin

    def _current_candidate_details_text(self, left: str, right: str) -> str:
        if not left and not right:
            return "No current combination."

        lines = [f"Current pair: {left or '?'} + {right or '?'}"]
        lines.append(f"Origin: {self._current_candidate_origin_label(left, right)}")
        lines.append(self._combination_status_message(left, right))
        if not self._current_result:
            lines.append("Estimated result weight: unavailable without a loaded save.")
            return "\n".join(lines)
        if not left or not right:
            lines.append("Estimated result weight: unavailable while the pair is incomplete.")
            return "\n".join(lines)
        if (
            left not in self._current_result["elements"]
            or right not in self._current_result["elements"]
        ):
            lines.append("Estimated result weight: unavailable with an unknown element.")
            return "\n".join(lines)

        estimated_weight = candidate_result_weight(
            left,
            right,
            self._current_result["node_weights"],
        )
        lines.append(f"Estimated result weight: {estimated_weight}")
        lines.append(
            "Still present in candidate index: "
            + (
                "yes"
                if normalize_pair(left, right) in self._current_result.get("candidate_pairs", [])
                else "no"
            )
        )
        return "\n".join(lines)

    def _set_current_pair(
        self,
        pair: tuple[str, str],
        origin: str,
        suggestion_mode: str | None = None,
    ) -> None:
        self._last_suggested_pair = normalize_pair(pair[0], pair[1])
        self._current_candidate_origin = origin
        self.element1_edit.setText(pair[0])
        self.element2_edit.setText(pair[1])
        self._last_suggestion_mode = suggestion_mode

    def _indexed_candidate_allowed(self, pair: tuple[str, str], include_skipped: bool) -> bool:
        if not self._current_result:
            return False
        if pair in self._current_result["known_pairs"]:
            return False
        if pair in self._current_result["discarded_pairs"]:
            return False
        if pair in self._current_result["done_pairs"]:
            return False
        if not include_skipped and pair in self._current_result["skipped_pairs"]:
            return False
        return True

    def _pick_random_indexed_candidate(self, include_skipped: bool) -> tuple[str, str] | None:
        if not self._current_result:
            return None
        candidates = [
            pair
            for pair in self._current_result.get("candidate_pairs", [])
            if self._indexed_candidate_allowed(pair, include_skipped)
        ]
        if not candidates:
            return None
        return random.choice(candidates)

    def _pick_cheapest_indexed_candidate(self, include_skipped: bool) -> tuple[str, str] | None:
        if not self._current_result:
            return None
        for pair in self._current_result.get("candidate_pairs_by_weight", []):
            if self._indexed_candidate_allowed(pair, include_skipped):
                return pair
        return None

    def _restore_discarded_pair(self, pair: tuple[str, str]) -> None:
        if not self._current_result or self._current_save_path is None:
            return

        gui_module = sys.modules[f"{__package__.rsplit('.', 1)[0]}.gui"]
        gui_module.remove_discarded_pair(self._current_save_path, pair)
        self._current_result["discarded_pairs"].remove(pair)
        self._current_result["skipped_pairs"].discard(pair)
        if (
            pair not in self._current_result["known_pairs"]
            and pair not in self._current_result["done_pairs"]
            and pair not in self._current_result["missing"]
        ):
            self._current_result["missing"].append(pair)
        self._update_missing_statistics_for_pair(pair, 1)
        self._refresh_discarded_table()
        self._refresh_summary()

    def _validate_combination_inputs(self, *_args) -> None:
        self._validate_element_input(self.element1_edit)
        self._validate_element_input(self.element2_edit)
        self._refresh_candidate_status()

    def _validate_element_input(self, field) -> bool:
        if not self._current_result:
            field.setStyleSheet("")
            field.setToolTip("")
            return False

        text = field.text().strip()
        if not text:
            field.setStyleSheet("")
            field.setToolTip("")
            return False

        normalized = text.casefold()
        matched_name = next(
            (
                element
                for element in self._current_result["elements"]
                if str(element).casefold() == normalized
            ),
            None,
        )
        if matched_name is None:
            field.setStyleSheet("border: 1px solid #dc2626;")
            field.setToolTip("Element not found in the save.")
            return False

        field.setStyleSheet("border: 1px solid #16a34a;")
        field.setToolTip(f"Valid element: {matched_name}")
        return True

    def _record_suggestion(self, pair: tuple[str, str], mode: str) -> None:
        for index in range(self.suggestion_history_list.count()):
            item = self.suggestion_history_list.item(index)
            if item.data(Qt.UserRole) == pair:
                self.suggestion_history_list.takeItem(index)
                break
        history_item = QListWidgetItem(f"{mode.title()}: {pair[0]} + {pair[1]}")
        history_item.setData(Qt.UserRole, pair)
        self.suggestion_history_list.insertItem(0, history_item)
        while self.suggestion_history_list.count() > 10:
            self.suggestion_history_list.takeItem(self.suggestion_history_list.count() - 1)

    def _restore_history_suggestion(self, item: QListWidgetItem) -> None:
        pair = item.data(Qt.UserRole)
        if pair:
            self._set_current_pair((str(pair[0]), str(pair[1])), "history")

    def _pick_random_combination(self) -> None:
        gui_module = sys.modules[f"{__package__.rsplit('.', 1)[0]}.gui"]
        if not self._current_result:
            return
        pair = self._pick_random_indexed_candidate(include_skipped=False)
        if pair is None:
            pair = self._pick_random_indexed_candidate(include_skipped=True)
        if pair is None:
            pair = gui_module.find_random_combination(
                self._current_result["elements"],
                self._current_result["recipes"],
                discarded_pairs=self._current_result["discarded_pairs"],
                done_pairs=(
                    self._current_result["done_pairs"]
                    | self._current_result["skipped_pairs"]
                ),
            )
        if pair is None:
            pair = gui_module.find_random_combination(
                self._current_result["elements"],
                self._current_result["recipes"],
                discarded_pairs=self._current_result["discarded_pairs"],
                done_pairs=self._current_result["done_pairs"],
            )
        if pair is None:
            title, message = self._show_guidance(
                "Nothing left to suggest",
                "No unfinished combination is currently available.",
                "Try loading a different save or undoing a discarded/done combination.",
            )
            QMessageBox.information(self, title, message)
            return
        self._set_current_pair(pair, "random suggestion", suggestion_mode="random")
        self._record_suggestion(pair, "random")

    def _pick_cheapest_combination(self) -> None:
        gui_module = sys.modules[f"{__package__.rsplit('.', 1)[0]}.gui"]
        if not self._current_result:
            return
        pair = self._pick_cheapest_indexed_candidate(include_skipped=False)
        if pair is None:
            pair = self._pick_cheapest_indexed_candidate(include_skipped=True)
        if pair is None:
            pair = gui_module.find_cheapest_combination(
                self._current_result["elements"],
                self._current_result["recipes"],
                self._current_result["node_weights"],
                discarded_pairs=self._current_result["discarded_pairs"],
                done_pairs=(
                    self._current_result["done_pairs"]
                    | self._current_result["skipped_pairs"]
                ),
            )
        if pair is None:
            pair = gui_module.find_cheapest_combination(
                self._current_result["elements"],
                self._current_result["recipes"],
                self._current_result["node_weights"],
                discarded_pairs=self._current_result["discarded_pairs"],
                done_pairs=self._current_result["done_pairs"],
            )
        if pair is None:
            title, message = self._show_guidance(
                "Nothing left to suggest",
                "No unfinished combination is currently available.",
                "Try loading a different save or undoing a discarded/done combination.",
            )
            QMessageBox.information(self, title, message)
            return
        self._set_current_pair(pair, "cheapest suggestion", suggestion_mode="cheapest")
        self._record_suggestion(pair, "cheapest")

    def _pick_next_combination(self) -> None:
        if not self._current_result:
            return
        if self._last_suggestion_mode is None:
            title, message = self._show_guidance(
                "No suggestion to continue",
                "Generate a suggestion first.",
                "Use Random or Cheapest before asking for the next combination.",
            )
            QMessageBox.information(self, title, message)
            return
        left = self.element1_edit.text().strip()
        right = self.element2_edit.text().strip()
        if left and right:
            pair = normalize_pair(left, right)
            if (
                left in self._current_result["elements"]
                and right in self._current_result["elements"]
                and pair not in self._current_result["known_pairs"]
                and pair not in self._current_result["discarded_pairs"]
                and pair not in self._current_result["done_pairs"]
            ):
                self._current_result["skipped_pairs"].add(pair)

        if self._last_suggestion_mode == "random":
            self._pick_random_combination()
        else:
            self._pick_cheapest_combination()

    def _mark_current_combination_done(self) -> None:
        if not self._current_result:
            return
        left = self.element1_edit.text().strip()
        right = self.element2_edit.text().strip()
        if not left or not right:
            title, message = self._show_guidance(
                "Combination needed",
                "Enter or generate a combination first.",
                "Fill both element fields or use Random/Cheapest.",
            )
            QMessageBox.information(self, title, message)
            return
        if (
            left not in self._current_result["elements"]
            or right not in self._current_result["elements"]
        ):
            title, message = self._show_guidance(
                "Unknown element",
                "The entered elements do not exist in the loaded save.",
                "Pick elements from auto-complete or load the correct save file.",
            )
            QMessageBox.warning(self, title, message)
            return
        pair = normalize_pair(left, right)
        if pair in self._current_result["known_pairs"]:
            title, message = self._show_guidance(
                "Combination already known",
                "This combination already exists in the save.",
                "You can mark a different candidate as done instead.",
            )
            QMessageBox.information(self, title, message)
            return
        if pair in self._current_result["discarded_pairs"]:
            title, message = self._show_guidance(
                "Combination already discarded",
                "This combination is discarded.",
                "Use Undo Discard if you want to restore it first.",
            )
            QMessageBox.information(self, title, message)
            return
        if pair in self._current_result["done_pairs"]:
            title, message = self._show_guidance(
                "Already marked done",
                "This combination is already marked done for this session.",
                "Use Undo Done if you want to make it available again.",
            )
            QMessageBox.information(self, title, message)
            return
        self._current_result["skipped_pairs"].discard(pair)
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
            title, message = self._show_guidance(
                "Done combination needed",
                "Enter a done combination to undo.",
                "Fill both fields with a combination marked done in this session.",
            )
            QMessageBox.information(self, title, message)
            return
        if (
            left not in self._current_result["elements"]
            or right not in self._current_result["elements"]
        ):
            title, message = self._show_guidance(
                "Unknown element",
                "The entered elements do not exist in the loaded save.",
                "Pick elements from auto-complete or load the correct save file.",
            )
            QMessageBox.warning(self, title, message)
            return
        pair = normalize_pair(left, right)
        if pair not in self._current_result["done_pairs"]:
            title, message = self._show_guidance(
                "Nothing to undo",
                "This combination is not marked done for this session.",
                "Use Done first, or enter a combination that was already marked done.",
            )
            QMessageBox.information(self, title, message)
            return
        self._current_result["done_pairs"].remove(pair)
        self._current_result["skipped_pairs"].discard(pair)
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
        gui_module = sys.modules[f"{__package__.rsplit('.', 1)[0]}.gui"]
        if not self._current_result or self._current_save_path is None:
            return
        left = self.element1_edit.text().strip()
        right = self.element2_edit.text().strip()
        if not left or not right:
            title, message = self._show_guidance(
                "Combination needed",
                "Enter or generate a combination first.",
                "Fill both element fields or use Random/Cheapest.",
            )
            QMessageBox.information(self, title, message)
            return
        if (
            left not in self._current_result["elements"]
            or right not in self._current_result["elements"]
        ):
            title, message = self._show_guidance(
                "Unknown element",
                "The entered elements do not exist in the loaded save.",
                "Pick elements from auto-complete or load the correct save file.",
            )
            QMessageBox.warning(self, title, message)
            return
        pair = normalize_pair(left, right)
        if pair in self._current_result["known_pairs"]:
            title, message = self._show_guidance(
                "Combination already known",
                "This combination already exists in the save.",
                "Choose a different candidate instead of discarding it.",
            )
            QMessageBox.warning(self, title, message)
            return
        if pair in self._current_result["discarded_pairs"]:
            title, message = self._show_guidance(
                "Already discarded",
                "This combination is already discarded.",
                "Use Undo Discard if you want to restore it.",
            )
            QMessageBox.information(self, title, message)
            return
        self._current_result["skipped_pairs"].discard(pair)
        gui_module.add_discarded_pair(self._current_save_path, pair)
        self._current_result["discarded_pairs"].add(pair)
        self._current_result["missing"] = [
            item for item in self._current_result["missing"] if item != pair
        ]
        self._update_missing_statistics_for_pair(pair, -1)
        self._refresh_discarded_table()
        self._refresh_summary()
        self.element1_edit.clear()
        self.element2_edit.clear()
        title, message = self._show_guidance(
            "Combination discarded",
            f"Discarded combination: {pair[0]} + {pair[1]}",
            "It will no longer appear in suggestions until you undo the discard.",
        )
        QMessageBox.information(self, title, message)

    def _undo_current_combination_discard(self) -> None:
        if not self._current_result or self._current_save_path is None:
            return
        left = self.element1_edit.text().strip()
        right = self.element2_edit.text().strip()
        if not left or not right:
            title, message = self._show_guidance(
                "Discarded combination needed",
                "Enter a discarded combination to undo.",
                "Fill both fields with a combination that was previously discarded.",
            )
            QMessageBox.information(self, title, message)
            return
        if (
            left not in self._current_result["elements"]
            or right not in self._current_result["elements"]
        ):
            title, message = self._show_guidance(
                "Unknown element",
                "The entered elements do not exist in the loaded save.",
                "Pick elements from auto-complete or load the correct save file.",
            )
            QMessageBox.warning(self, title, message)
            return
        pair = normalize_pair(left, right)
        if pair not in self._current_result["discarded_pairs"]:
            title, message = self._show_guidance(
                "Nothing to undo",
                "This combination is not discarded.",
                "Use Discard first, or enter a combination that is currently discarded.",
            )
            QMessageBox.information(self, title, message)
            return
        self._restore_discarded_pair(pair)
        self.element1_edit.clear()
        self.element2_edit.clear()

    def _remove_selected_discarded_combination(self) -> None:
        if not self._current_result or self._current_save_path is None:
            return

        selected_indexes = self.discarded_table.selectionModel().selectedRows()
        if not selected_indexes:
            title, message = self._show_guidance(
                "Selection needed",
                "Select a discarded combination first.",
                "Choose a row in the discarded combinations table, then try again.",
            )
            QMessageBox.information(self, title, message)
            return

        proxy_index = selected_indexes[0]
        source_index = self.discarded_proxy_model.mapToSource(proxy_index)
        row = source_index.row()
        left = self.discarded_model.data(self.discarded_model.index(row, 0))
        right = self.discarded_model.data(self.discarded_model.index(row, 1))
        pair = normalize_pair(str(left), str(right))
        if pair not in self._current_result["discarded_pairs"]:
            title, message = self._show_guidance(
                "Nothing to remove",
                "This combination is not discarded.",
                "Refresh the table or select another discarded combination.",
            )
            QMessageBox.information(self, title, message)
            return

        self._restore_discarded_pair(pair)

    def _reset_discarded_combinations(self) -> None:
        if not self._current_result or self._current_save_path is None:
            return
        if not self._current_result["discarded_pairs"]:
            title, message = self._show_guidance(
                "Nothing to reset",
                "There is no discarded combination to reset.",
                "Discard at least one combination before using this action.",
            )
            QMessageBox.information(self, title, message)
            return

        answer = QMessageBox.question(
            self,
            "Reset discarded combinations",
            (
                "Reset all discarded combinations?\n\n"
                "This restores every discarded pair to the candidate pool."
            ),
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        gui_module = sys.modules[f"{__package__.rsplit('.', 1)[0]}.gui"]
        gui_module.clear_discarded_pairs(self._current_save_path)
        restored_pairs = sorted(self._current_result["discarded_pairs"])
        self._current_result["discarded_pairs"].clear()
        self._current_result["skipped_pairs"].difference_update(restored_pairs)
        for pair in restored_pairs:
            if (
                pair not in self._current_result["known_pairs"]
                and pair not in self._current_result["done_pairs"]
                and pair not in self._current_result["missing"]
            ):
                self._current_result["missing"].append(pair)
            self._update_missing_statistics_for_pair(pair, 1)
        self._refresh_discarded_table()
        self._refresh_summary()

    def _export_discarded_combinations(self) -> None:
        if not self._current_result or self._current_save_path is None:
            return

        gui_module = sys.modules[f"{__package__.rsplit('.', 1)[0]}.gui"]
        path, _ = gui_module.QFileDialog.getSaveFileName(
            self,
            "Export discarded combinations",
            str(Path("discarded_export.json")),
            "JSON (*.json);;All files (*)",
        )
        if not path:
            return

        gui_module.export_discarded_pairs(Path(path))
        title, message = self._show_guidance(
            "Export completed",
            "Discarded export completed.",
            "You can import this JSON file later on another machine or save file.",
        )
        QMessageBox.information(self, title, message)

    def _import_discarded_combinations(self) -> None:
        if not self._current_result or self._current_save_path is None:
            return

        gui_module = sys.modules[f"{__package__.rsplit('.', 1)[0]}.gui"]
        path, _ = gui_module.QFileDialog.getOpenFileName(
            self,
            "Import discarded combinations",
            "",
            "JSON (*.json);;All files (*)",
        )
        if not path:
            return

        try:
            imported_pairs = gui_module.import_discarded_pairs(Path(path))
        except (OSError, ValueError) as exc:
            title, message = self._show_guidance(
                "Import failed",
                "The discarded combinations file could not be imported.",
                f"Check that the file is a valid discarded JSON export.\n\nDetails: {exc}",
            )
            QMessageBox.warning(self, title, message)
            return

        new_pairs = imported_pairs - self._current_result["discarded_pairs"]
        for pair in new_pairs:
            self._current_result["discarded_pairs"].add(pair)
            if pair in self._current_result["missing"]:
                self._current_result["missing"].remove(pair)
                self._update_missing_statistics_for_pair(pair, -1)
        self._refresh_discarded_table()
        self._refresh_summary()
        title, message = self._show_guidance(
            "Import completed",
            f"{len(new_pairs)} discarded combination(s) imported.",
            "The discarded list and candidate counts were updated.",
        )
        QMessageBox.information(self, title, message)
