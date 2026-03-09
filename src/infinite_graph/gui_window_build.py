"""UI construction helpers for the main window."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCompleter,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
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

        controls = self._build_controls_section()
        layout.addWidget(controls)
        self.current_candidate_toggle_button.clicked.connect(self._toggle_candidate_details)
        self.history_toggle_button.clicked.connect(self._toggle_history_panel)
        self.summary_toggle_button.clicked.connect(self._toggle_summary_panel)

        tabs = QTabWidget()
        tabs.addTab(self._build_graph_tab(), "Graphe")
        tabs.addTab(self._build_info_tab(), "Infos")
        tabs.addTab(self._build_stats_tab(), "Statistiques")
        layout.addWidget(tabs, 1)

        self.setCentralWidget(central)
        self._set_candidate_buttons_enabled(False)
        self._update_element_completion([])

    def _build_controls_section(self) -> QWidget:
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        load_group = self._build_load_group()
        current_candidate_group = self._build_current_candidate_group()
        history_group = self._build_history_group()
        load_group.setSizePolicy(
            load_group.sizePolicy().horizontalPolicy(),
            load_group.sizePolicy().verticalPolicy(),
        )
        current_candidate_group.setSizePolicy(
            current_candidate_group.sizePolicy().horizontalPolicy(),
            current_candidate_group.sizePolicy().verticalPolicy(),
        )
        history_group.setSizePolicy(
            history_group.sizePolicy().horizontalPolicy(),
            history_group.sizePolicy().verticalPolicy(),
        )
        controls_layout.addWidget(load_group, 2)
        controls_layout.addWidget(current_candidate_group, 5)
        controls_layout.addWidget(history_group, 3)
        controls_layout.setAlignment(Qt.AlignTop)
        return controls

    def _build_load_group(self) -> QGroupBox:
        group = QGroupBox("Chargement")
        group_layout = QFormLayout(group)
        self.stage_label.setWordWrap(True)
        summary_panel_layout = QVBoxLayout(self.summary_panel)
        summary_panel_layout.setContentsMargins(8, 8, 8, 8)
        summary_panel_layout.addWidget(self.summary_label)
        group_layout.addRow("Sauvegarde", self._build_file_row())
        group_layout.addRow("", self._build_action_row())
        group_layout.addRow("Etat", self.stage_label)
        group_layout.addRow("", self.summary_toggle_button)
        group_layout.addRow("", self.summary_panel)
        return group

    def _build_current_candidate_group(self) -> QGroupBox:
        group = QGroupBox("Combinaison courante")
        group_layout = QFormLayout(group)
        group_layout.addRow("Elements", self._build_candidate_row())
        group_layout.addRow("Suggestions", self._build_suggestion_buttons_row())
        group_layout.addRow("Actions", self._build_decision_buttons_row())
        group_layout.addRow("Statut", self.candidate_status_label)
        group_layout.addRow("Restant", self.candidate_count_label)
        details_panel = QWidget()
        details_layout = QVBoxLayout(details_panel)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(4)
        details_layout.addWidget(self.current_candidate_toggle_button)
        details_layout.addWidget(self.current_candidate_details)
        self.current_candidate_details.setVisible(False)
        group_layout.addRow("Details", details_panel)
        return group

    def _build_history_group(self) -> QGroupBox:
        group = QGroupBox("Historique local")
        group_layout = QVBoxLayout(group)
        history_panel_layout = QVBoxLayout(self.history_panel)
        history_panel_layout.setContentsMargins(6, 6, 6, 6)
        history_panel_layout.addWidget(self._build_history_widget())
        group_layout.addWidget(self.history_toggle_button)
        group_layout.addWidget(self.history_panel)
        return group

    def _build_file_row(self) -> QWidget:
        file_row = QWidget()
        file_row_layout = QHBoxLayout(file_row)
        file_row_layout.setContentsMargins(0, 0, 0, 0)
        browse_button = QPushButton("Parcourir")
        browse_button.clicked.connect(self._pick_input)
        file_row_layout.addWidget(self.input_edit)
        file_row_layout.addWidget(browse_button)
        return file_row

    def _build_action_row(self) -> QWidget:
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
        return action_row

    def _build_candidate_row(self) -> QWidget:
        candidate_row = QWidget()
        candidate_row_layout = QHBoxLayout(candidate_row)
        candidate_row_layout.setContentsMargins(0, 0, 0, 0)
        self.element1_edit.setPlaceholderText("Element 1")
        self.element2_edit.setPlaceholderText("Element 2")
        self.element1_edit.setReadOnly(False)
        self.element2_edit.setReadOnly(False)
        self.element1_edit.setClearButtonEnabled(True)
        self.element2_edit.setClearButtonEnabled(True)
        self.element1_edit.textChanged.connect(self._validate_combination_inputs)
        self.element2_edit.textChanged.connect(self._validate_combination_inputs)
        self._configure_element_completer(self.element1_completer)
        self._configure_element_completer(self.element2_completer)
        self.element1_edit.setCompleter(self.element1_completer)
        self.element2_edit.setCompleter(self.element2_completer)
        candidate_row_layout.addWidget(self.element1_edit)
        candidate_row_layout.addWidget(self.element2_edit)
        return candidate_row

    def _build_suggestion_buttons_row(self) -> QWidget:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(self.random_button)
        row_layout.addWidget(self.cheapest_button)
        row_layout.addWidget(self.next_button)
        row_layout.addStretch(1)
        return row

    def _build_decision_buttons_row(self) -> QWidget:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(self.done_button)
        row_layout.addWidget(self.undo_done_button)
        row_layout.addWidget(self.discard_button)
        row_layout.addWidget(self.undo_discard_button)
        row_layout.addStretch(1)
        return row

    def _build_history_widget(self) -> QWidget:
        self.suggestion_history_list.setMaximumHeight(120)
        self.suggestion_history_list.itemClicked.connect(self._restore_history_suggestion)
        return self.suggestion_history_list

    @staticmethod
    def _configure_element_completer(completer: QCompleter) -> None:
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setFilterMode(Qt.MatchContains)

    def _update_element_completion(self, elements: list[str]) -> None:
        self.element_completer_model.setStringList(sorted(elements, key=str.casefold))

    def _toggle_summary_panel(self) -> None:
        is_hidden = self.summary_panel.isHidden()
        self.summary_panel.setVisible(is_hidden)
        self.summary_toggle_button.setText(
            "Masquer details" if is_hidden else "Afficher details"
        )

    def _toggle_candidate_details(self) -> None:
        is_hidden = self.current_candidate_details.isHidden()
        self.current_candidate_details.setVisible(is_hidden)
        self.current_candidate_toggle_button.setText(
            "Masquer details candidat"
            if is_hidden
            else "Afficher details candidat"
        )

    def _toggle_history_panel(self) -> None:
        is_hidden = self.history_panel.isHidden()
        self.history_panel.setVisible(is_hidden)
        self.history_toggle_button.setText(
            "Masquer historique" if is_hidden else "Afficher historique"
        )

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

        details_container = QWidget()
        details_layout = QVBoxLayout(details_container)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.addWidget(self.selected_node_label)
        details_layout.addWidget(self.selected_node_details, 1)

        controls_container = QWidget()
        controls_container_layout = QVBoxLayout(controls_container)
        controls_container_layout.setContentsMargins(0, 0, 0, 0)
        controls_container_layout.addWidget(search_row)
        controls_container_layout.addWidget(subgraph_row)
        controls_container_layout.addWidget(weight_row)
        controls_container_layout.addWidget(layout_row)
        controls_container_layout.addStretch(1)

        bottom_splitter = QSplitter(Qt.Horizontal)
        bottom_splitter.addWidget(details_container)
        bottom_splitter.addWidget(controls_container)
        bottom_splitter.setSizes([420, 680])

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(self.graph_view)
        main_splitter.addWidget(bottom_splitter)
        main_splitter.setSizes([720, 360])

        layout.addWidget(main_splitter)
        return tab

    def _build_info_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)

        top_splitter = QSplitter(Qt.Horizontal)
        self.node_table.setModel(self.node_model)
        self.edge_table.setModel(self.edge_model)
        self.discarded_table.setModel(self.discarded_model)
        self.node_table.setSortingEnabled(True)
        self.edge_table.setSortingEnabled(True)
        self.discarded_table.setSortingEnabled(True)
        self.node_table.horizontalHeader().setStretchLastSection(True)
        self.edge_table.horizontalHeader().setStretchLastSection(True)
        self.discarded_table.horizontalHeader().setStretchLastSection(True)
        top_splitter.addWidget(self.node_table)
        top_splitter.addWidget(self.edge_table)
        top_splitter.setSizes([400, 900])

        discarded_container = QWidget()
        discarded_layout = QVBoxLayout(discarded_container)
        discarded_layout.setContentsMargins(0, 0, 0, 0)
        self.remove_discarded_button.clicked.connect(
            self._remove_selected_discarded_combination
        )
        self.reset_discarded_button.clicked.connect(self._reset_discarded_combinations)
        self.export_discarded_button.clicked.connect(self._export_discarded_combinations)
        self.import_discarded_button.clicked.connect(self._import_discarded_combinations)
        discarded_layout.addWidget(QLabel("Combinaisons discardees"))
        discarded_layout.addWidget(self.discarded_table)
        discarded_layout.addWidget(self.remove_discarded_button)
        discarded_layout.addWidget(self.reset_discarded_button)
        discarded_layout.addWidget(self.export_discarded_button)
        discarded_layout.addWidget(self.import_discarded_button)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(top_splitter)
        splitter.addWidget(discarded_container)
        splitter.setSizes([700, 220])
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
