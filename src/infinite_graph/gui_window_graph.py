"""Graph interaction helpers for the main window."""

from PySide6.QtWidgets import QMessageBox

from .gui_layout import build_subgraph_render_data, build_weight_filtered_render_data


class WindowGraphMixin:
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
        if min_weight is not None and max_weight is not None and min_weight > max_weight:
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
