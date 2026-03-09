"""UI construction helpers for the main window."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCompleter,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class WindowBuildMixin:
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
        self.next_button.clicked.connect(self._pick_next_combination)
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
        candidate_row_layout.addWidget(self.next_button)
        candidate_row_layout.addWidget(self.done_button)
        candidate_row_layout.addWidget(self.undo_done_button)
        candidate_row_layout.addWidget(self.discard_button)
        candidate_row_layout.addWidget(self.undo_discard_button)
        self.suggestion_history_list.setMaximumHeight(120)
        self.suggestion_history_list.itemClicked.connect(self._restore_history_suggestion)

        controls_layout.addRow("Sauvegarde", file_row)
        controls_layout.addRow("Element cible", self.focus_edit)
        controls_layout.addRow("Element 1 / Element 2", candidate_row)
        controls_layout.addRow("Historique", self.suggestion_history_list)
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
        gui_module = sys.modules[f"{__package__}.gui"]
        path, _ = gui_module.QFileDialog.getOpenFileName(
            self,
            "Choisir une sauvegarde Infinite Craft",
            "",
            "Tous les fichiers (*);;JSON (*.json)",
        )
        if path:
            self.input_edit.setText(path)
