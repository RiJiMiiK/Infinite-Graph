"""Community analysis helpers for the main window."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDoubleSpinBox, QLabel, QMessageBox, QSpinBox


class WindowCommunitiesMixin:
    def _set_community_controls_enabled(self, enabled: bool) -> None:
        self.community_compute_button.setEnabled(enabled)
        self.community_algorithm_combo.setEnabled(enabled)
        self.community_parameters_group.setEnabled(enabled)

    def _reset_community_view(self) -> None:
        self._current_community_summary = None
        self.community_summary_label.setText("No community analysis has been run yet.")
        self.community_list.clear()
        self.community_details.setPlainText("No community selected.")

    def _refresh_community_parameter_inputs(self) -> None:
        gui_module = sys.modules[f"{__package__.rsplit('.', 1)[0]}.gui"]
        while self.community_parameters_layout.rowCount() > 0:
            self.community_parameters_layout.removeRow(0)

        self._community_parameter_inputs = {}
        algorithm_name = self.community_algorithm_combo.currentData()
        if not algorithm_name:
            self.community_parameters_group.setVisible(False)
            return

        parameter_definitions = gui_module.get_mono_community_algorithm_parameters(
            str(algorithm_name)
        )
        if not parameter_definitions:
            self.community_parameters_group.setVisible(False)
            return

        for parameter in parameter_definitions:
            parameter_name = str(parameter["name"])
            parameter_type = str(parameter.get("type", ""))
            if parameter_type == "int":
                spin_box = QSpinBox()
                minimum = int(parameter.get("minimum", 0))
                maximum = int(parameter.get("maximum", 999_999))
                default = int(parameter.get("default", minimum))
                spin_box.setRange(minimum, maximum)
                spin_box.setValue(max(default, minimum))
            elif parameter_type == "float":
                spin_box = QDoubleSpinBox()
                minimum = float(parameter.get("minimum", 0.0))
                maximum = float(parameter.get("maximum", 999_999.0))
                default = float(parameter.get("default", minimum))
                decimals = int(parameter.get("decimals", 4))
                step = float(parameter.get("step", 0.1))
                spin_box.setDecimals(decimals)
                spin_box.setSingleStep(step)
                spin_box.setRange(minimum, maximum)
                spin_box.setValue(max(default, minimum))
            else:
                continue
            spin_box.setObjectName(f"community_parameter_{parameter_name}")
            spin_box.setToolTip(str(parameter.get("label", parameter_name)))
            self.community_parameters_layout.addRow(
                QLabel(str(parameter.get("label", parameter_name))),
                spin_box,
            )
            self._community_parameter_inputs[parameter_name] = spin_box

        self.community_parameters_group.setVisible(
            bool(self._community_parameter_inputs)
        )

    def _read_community_parameter_values(self) -> dict[str, object]:
        values: dict[str, object] = {}
        for parameter_name, widget in self._community_parameter_inputs.items():
            if isinstance(widget, QSpinBox):
                values[parameter_name] = int(widget.value())
            elif isinstance(widget, QDoubleSpinBox):
                values[parameter_name] = float(widget.value())
        return values

    def _compute_communities(self) -> None:
        if not self._current_result:
            return

        algorithm_name = self.community_algorithm_combo.currentData()
        if not algorithm_name:
            return

        gui_module = sys.modules[f"{__package__.rsplit('.', 1)[0]}.gui"]
        graph = self._current_result["community_graph"]
        algorithm_parameters = self._read_community_parameter_values()
        if str(algorithm_name) == "lswl":
            selected_node = getattr(self.graph_view, "selected_node_id", None)
            if selected_node is None:
                QMessageBox.warning(
                    self,
                    "Community computation requires a selected node",
                    "LSWL requires a selected graph node. Select a node in the graph view first.",
                )
                return
            algorithm_parameters["query_node"] = str(selected_node)
        pre_run_warning = gui_module.get_mono_community_algorithm_pre_run_warning(
            str(algorithm_name),
            graph,
            algorithm_parameters,
        )
        if pre_run_warning:
            response = QMessageBox.warning(
                self,
                "Community computation warning",
                f"{pre_run_warning}\n\nContinue anyway?",
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )
            if response != QMessageBox.Ok:
                return

        try:
            result = gui_module.run_mono_community_algorithm(
                graph,
                str(algorithm_name),
                **algorithm_parameters,
            )
            summary = gui_module.summarize_mono_community_result(result)
        except Exception as exc:  # pragma: no cover - exercised via GUI tests
            QMessageBox.critical(
                self,
                "Community computation failed",
                gui_module.format_mono_community_algorithm_failure(
                    str(algorithm_name),
                    exc,
                    graph,
                ),
            )
            return

        self._current_community_summary = summary
        warning_text = gui_module.get_mono_community_algorithm_warning(str(algorithm_name))
        summary_lines = [
            f"Algorithm: {self.community_algorithm_combo.currentText()}",
            f"Method name: {summary['method_name']}",
            f"Detected communities: {summary['community_count']}",
            f"Min size: {summary['min_size']}",
            f"Max size: {summary['max_size']}",
            f"Average size: {summary['average_size']:.2f}",
        ]
        if algorithm_parameters:
            summary_lines.extend(
                [
                    "",
                    "Parameters:",
                    ", ".join(
                        f"{key}={value}"
                        for key, value in sorted(algorithm_parameters.items())
                    ),
                ]
            )
        if warning_text:
            summary_lines.extend(["", "Adaptation warning:", warning_text])
        self.community_summary_label.setText("\n".join(summary_lines))

        self.community_list.clear()
        for community_index, community_nodes in enumerate(summary["communities"]):
            item_text = f"Community {community_index + 1} ({len(community_nodes)} nodes)"
            item = gui_module.QListWidgetItem(item_text)
            item.setData(Qt.UserRole, community_index)
            self.community_list.addItem(item)

        if self.community_list.count() > 0:
            self.community_list.setCurrentRow(0)
            self._show_selected_community(self.community_list.item(0))
        else:
            self.community_details.setPlainText("No community selected.")

    def _show_selected_community(self, item) -> None:
        if item is None or not self._current_community_summary:
            self.community_details.setPlainText("No community selected.")
            return

        community_index = item.data(Qt.UserRole)
        if not isinstance(community_index, int):
            self.community_details.setPlainText("No community selected.")
            return

        communities = self._current_community_summary["communities"]
        if community_index < 0 or community_index >= len(communities):
            self.community_details.setPlainText("No community selected.")
            return

        community_nodes = communities[community_index]
        details_lines = [
            f"Community: {community_index + 1}",
            f"Size: {len(community_nodes)}",
            "",
            "Nodes:",
        ]
        details_lines.extend(community_nodes)
        self.community_details.setPlainText("\n".join(details_lines))
