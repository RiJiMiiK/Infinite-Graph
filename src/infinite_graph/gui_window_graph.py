import sys
from pathlib import Path

from PySide6.QtWidgets import QMessageBox

from .gui_layout import build_subgraph_render_data, build_weight_filtered_render_data


class WindowGraphMixin:
    def _export_graph_image(self) -> None:
        current_render = self.graph_view.current_render_data
        if not current_render or not current_render.get("positions"):
            QMessageBox.information(
                self,
                "Information",
                "Generate or display a graph before exporting an image.",
            )
            return

        gui_module = sys.modules[f"{__package__}.gui"]
        path, _ = gui_module.QFileDialog.getSaveFileName(
            self,
            "Export graph image",
            str(Path("graph_export.png")),
            "PNG (*.png);;All files (*)",
        )
        if not path:
            return

        target_path = Path(path)
        if not target_path.suffix:
            target_path = target_path.with_suffix(".png")

        image = self.graph_view.grab().toImage()
        if image.isNull():
            QMessageBox.warning(
                self,
                "Error",
                "Unable to capture the graph view for export.",
            )
            return

        if image.save(str(target_path), "PNG"):
            QMessageBox.information(
                self,
                "Information",
                f"Graph image exported to: {target_path}",
            )
            return

        QMessageBox.warning(
            self,
            "Error",
            f"Unable to save the graph image to: {target_path}",
        )

    def _show_graph_context_menu(self, node_id: object, global_pos) -> None:
        node_name = str(node_id) if node_id is not None else ""
        if not node_name:
            return

        gui_module = sys.modules[f"{__package__}.gui"]
        menu = gui_module.QMenu(self)
        copy_action = menu.addAction("Copy element name")
        element1_action = menu.addAction("Use as Element 1")
        element2_action = menu.addAction("Use as Element 2")
        search_action = menu.addAction("Search this element")
        subgraph_action = menu.addAction("Set as subgraph center")
        chosen_action = menu.exec(global_pos)

        if chosen_action == copy_action:
            self._copy_graph_node_name(node_name)
        elif chosen_action == element1_action:
            self._set_graph_node_in_element_field(node_name, self.element1_edit)
        elif chosen_action == element2_action:
            self._set_graph_node_in_element_field(node_name, self.element2_edit)
        elif chosen_action == search_action:
            self._reuse_graph_node_as_search(node_name)
        elif chosen_action == subgraph_action:
            self._set_graph_node_as_subgraph_center(node_name)

    def _on_graph_node_selected(self, node_id: object) -> None:
        node_name = str(node_id) if node_id is not None else ""
        if not node_name:
            self.selected_node_label.setText("Selected node: none")
            self.selected_node_details.setPlainText("No node selected.")
            self.node_table.clearSelection()
            return

        self.selected_node_label.setText(f"Selected node: {node_name}")
        self.selected_node_details.setPlainText(self._build_selected_node_details(node_name))
        for row_index, row in enumerate(self.node_model.rows):
            if row[0] == node_name:
                source_index = self.node_model.index(row_index, 0)
                proxy_index = self.node_proxy_model.mapFromSource(source_index)
                if proxy_index.isValid():
                    self.node_table.selectRow(proxy_index.row())
                    self.node_table.scrollTo(proxy_index)
                else:
                    self.node_table.clearSelection()
                break

    @staticmethod
    def _copy_graph_node_name(node_name: str) -> None:
        gui_module = sys.modules[f"{__package__}.gui"]
        gui_module.QApplication.clipboard().setText(node_name)

    @staticmethod
    def _set_graph_node_in_element_field(node_name: str, field) -> None:
        field.setText(node_name)

    def _reuse_graph_node_as_search(self, node_name: str) -> None:
        self.graph_search_edit.setText(node_name)
        self.graph_view.select_node_by_id(node_name)

    def _set_graph_node_as_subgraph_center(self, node_name: str) -> None:
        self.subgraph_center_edit.setText(node_name)
        if not self.subgraph_depth_edit.text().strip():
            self.subgraph_depth_edit.setText("1")

    def _search_graph_node(self) -> None:
        if not self._current_result:
            return

        query = self.graph_search_edit.text().strip()
        if not query:
            QMessageBox.information(self, "Information", "Enter an element to search.")
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
            f"Element not found in the graph: {query}",
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
                "Enter a subgraph center or select a node.",
            )
            return

        depth_text = self.subgraph_depth_edit.text().strip() or "1"
        if not depth_text.isdigit():
            QMessageBox.information(
                self,
                "Information",
                "Subgraph depth must be a non-negative integer.",
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
                f"Unable to build a subgraph for: {center_node}",
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
                "Enter at least a minimum or maximum weight.",
            )
            return

        if (min_text and not min_text.isdigit()) or (max_text and not max_text.isdigit()):
            QMessageBox.information(
                self,
                "Information",
                "Min and max weights must be non-negative integers.",
            )
            return

        min_weight = int(min_text) if min_text else None
        max_weight = int(max_text) if max_text else None
        if min_weight is not None and max_weight is not None and min_weight > max_weight:
            QMessageBox.information(
                self,
                "Information",
                "Minimum weight cannot be greater than maximum weight.",
            )
            return

        filtered = build_weight_filtered_render_data(
            current_render,
            min_weight,
            max_weight,
        )
        self.graph_view.update_graph(filtered)

    def _build_selected_node_details(self, node_name: str) -> str:
        if not self._current_result:
            return f"Name: {node_name}"

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

        lines = [f"Name: {node_name}"]
        if node_data is not None:
            lines.append(f"Weight: {'?' if node_data['weight'] is None else node_data['weight']}")
            lines.append(f"Starter: {'yes' if node_data['is_starter'] else 'no'}")
        lines.append(f"Incoming neighbors: {', '.join(sorted(set(incoming))) or 'none'}")
        lines.append(f"Outgoing neighbors: {', '.join(sorted(set(outgoing))) or 'none'}")
        lines.append(f"Related edges: {len(related_edges)}")
        if related_edges:
            lines.append("")
            lines.extend(related_edges[:20])
        return "\n".join(lines)
