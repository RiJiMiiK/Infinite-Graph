"""UI construction helpers for the main window."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QBoxLayout,
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
    WIDE_LAYOUT_BREAKPOINT = 1320
    STACKED_LAYOUT_BREAKPOINT = 980

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
        self._main_tabs = tabs
        tabs.addTab(self._build_graph_tab(), "Graph")
        tabs.addTab(self._build_info_tab(), "Info")
        tabs.addTab(self._build_stats_tab(), "Statistics")
        tabs.addTab(self._build_communities_tab(), "Communities")
        layout.addWidget(tabs, 1)

        self.setCentralWidget(central)
        self._set_candidate_buttons_enabled(False)
        self._update_element_completion([])
        self._update_responsive_layout(self.width())

    def _build_controls_section(self) -> QWidget:
        controls = QWidget()
        controls_layout = QBoxLayout(QBoxLayout.LeftToRight, controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        self._controls_layout = controls_layout
        load_group = self._build_load_group()
        current_candidate_group = self._build_current_candidate_group()
        history_group = self._build_history_group()
        self._load_group = load_group
        self._current_candidate_group = current_candidate_group
        self._history_group = history_group
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
        group = QGroupBox("Loading")
        group_layout = QFormLayout(group)
        self.stage_label.setWordWrap(True)
        summary_panel_layout = QVBoxLayout(self.summary_panel)
        summary_panel_layout.setContentsMargins(8, 8, 8, 8)
        summary_panel_layout.addWidget(self.summary_label)
        group_layout.addRow("Save file", self._build_file_row())
        group_layout.addRow("", self._build_action_row())
        group_layout.addRow("Status", self.stage_label)
        group_layout.addRow("", self.summary_toggle_button)
        group_layout.addRow("", self.summary_panel)
        return group

    def _build_current_candidate_group(self) -> QGroupBox:
        group = QGroupBox("Current combination")
        group_layout = QFormLayout(group)
        group_layout.addRow("Elements", self._build_candidate_row())
        group_layout.addRow("Suggestions", self._build_suggestion_buttons_row())
        group_layout.addRow("Actions", self._build_decision_buttons_row())
        group_layout.addRow("Status", self.candidate_status_label)
        group_layout.addRow("Remaining", self.candidate_count_label)
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
        group = QGroupBox("Local history")
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
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._pick_input)
        file_row_layout.addWidget(self.input_edit)
        file_row_layout.addWidget(browse_button)
        return file_row

    def _build_action_row(self) -> QWidget:
        action_row = QWidget()
        action_row_layout = QBoxLayout(QBoxLayout.LeftToRight, action_row)
        action_row_layout.setContentsMargins(0, 0, 0, 0)
        self._action_row_layout = action_row_layout
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
        candidate_row_layout = QBoxLayout(QBoxLayout.LeftToRight, candidate_row)
        candidate_row_layout.setContentsMargins(0, 0, 0, 0)
        self._candidate_row_layout = candidate_row_layout
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
        row_layout = QBoxLayout(QBoxLayout.LeftToRight, row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        self._suggestion_row_layout = row_layout
        row_layout.addWidget(self.random_button)
        row_layout.addWidget(self.cheapest_button)
        row_layout.addWidget(self.next_button)
        row_layout.addStretch(1)
        return row

    def _build_decision_buttons_row(self) -> QWidget:
        row = QWidget()
        row_layout = QBoxLayout(QBoxLayout.LeftToRight, row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        self._decision_row_layout = row_layout
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
            "Hide details" if is_hidden else "Show details"
        )
        self._save_ui_preferences_state()

    def _toggle_candidate_details(self) -> None:
        is_hidden = self.current_candidate_details.isHidden()
        self.current_candidate_details.setVisible(is_hidden)
        self.current_candidate_toggle_button.setText(
            "Hide candidate details"
            if is_hidden
            else "Show candidate details"
        )
        self._save_ui_preferences_state()

    def _toggle_history_panel(self) -> None:
        is_hidden = self.history_panel.isHidden()
        self.history_panel.setVisible(is_hidden)
        self.history_toggle_button.setText(
            "Hide history" if is_hidden else "Show history"
        )
        self._save_ui_preferences_state()

    def _update_responsive_layout(self, window_width: int) -> None:
        if window_width >= self.WIDE_LAYOUT_BREAKPOINT:
            self._controls_layout.setDirection(QBoxLayout.LeftToRight)
            self._controls_layout.setStretch(0, 2)
            self._controls_layout.setStretch(1, 5)
            self._controls_layout.setStretch(2, 3)
            row_direction = QBoxLayout.LeftToRight
        else:
            self._controls_layout.setDirection(QBoxLayout.TopToBottom)
            self._controls_layout.setStretch(0, 0)
            self._controls_layout.setStretch(1, 0)
            self._controls_layout.setStretch(2, 0)
            row_direction = (
                QBoxLayout.TopToBottom
                if window_width < self.STACKED_LAYOUT_BREAKPOINT
                else QBoxLayout.LeftToRight
            )

        for row_layout in (
            self._candidate_row_layout,
            self._suggestion_row_layout,
            self._decision_row_layout,
            self._action_row_layout,
        ):
            row_layout.setDirection(row_direction)

    def _load_ui_preferences_state(self) -> None:
        gui_module = sys.modules[f"{__package__}.gui"]
        self._ui_preferences = gui_module.load_ui_preferences()
        preferences = self._ui_preferences

        width = preferences.get("window_width")
        height = preferences.get("window_height")
        if isinstance(width, int) and isinstance(height, int):
            self.resize(max(width, 960), max(height, 720))

        if isinstance(preferences.get("layout_iterations"), int):
            self.layout_iterations_edit.setText(str(preferences["layout_iterations"]))
        if isinstance(preferences.get("layout_scale"), (int, float)):
            self.layout_scale_edit.setText(str(preferences["layout_scale"]))

        self._apply_saved_panel_state(
            self.summary_panel,
            self.summary_toggle_button,
            bool(preferences.get("summary_panel_visible", False)),
            "Hide details",
            "Show details",
        )
        self._apply_saved_panel_state(
            self.current_candidate_details,
            self.current_candidate_toggle_button,
            bool(preferences.get("candidate_details_visible", False)),
            "Hide candidate details",
            "Show candidate details",
        )
        self._apply_saved_panel_state(
            self.history_panel,
            self.history_toggle_button,
            bool(preferences.get("history_panel_visible", False)),
            "Hide history",
            "Show history",
        )

        self._restore_splitter_sizes(
            self._graph_main_splitter,
            preferences.get("graph_main_splitter_sizes"),
        )
        self._restore_splitter_sizes(
            self._graph_bottom_splitter,
            preferences.get("graph_bottom_splitter_sizes"),
        )
        self._restore_splitter_sizes(
            self._info_top_splitter,
            preferences.get("info_top_splitter_sizes"),
        )
        self._restore_splitter_sizes(
            self._info_splitter,
            preferences.get("info_splitter_sizes"),
        )
        self._update_responsive_layout(self.width())

    def _save_ui_preferences_state(self) -> None:
        gui_module = sys.modules[f"{__package__}.gui"]
        preferences = {
            "window_width": int(self.width()),
            "window_height": int(self.height()),
            "summary_panel_visible": self.summary_panel.isVisible(),
            "candidate_details_visible": self.current_candidate_details.isVisible(),
            "history_panel_visible": self.history_panel.isVisible(),
            "layout_iterations": self.layout_iterations_edit.text().strip() or "80",
            "layout_scale": self.layout_scale_edit.text().strip() or "1.2",
            "graph_main_splitter_sizes": self._graph_main_splitter.sizes(),
            "graph_bottom_splitter_sizes": self._graph_bottom_splitter.sizes(),
            "info_top_splitter_sizes": self._info_top_splitter.sizes(),
            "info_splitter_sizes": self._info_splitter.sizes(),
        }
        gui_module.save_ui_preferences(preferences)
        self._ui_preferences = preferences

    @staticmethod
    def _apply_saved_panel_state(
        panel: QWidget,
        button: QPushButton,
        visible: bool,
        visible_text: str,
        hidden_text: str,
    ) -> None:
        panel.setVisible(visible)
        button.setText(visible_text if visible else hidden_text)

    @staticmethod
    def _restore_splitter_sizes(splitter: QSplitter, sizes: object) -> None:
        if (
            isinstance(sizes, list)
            and sizes
            and all(isinstance(size, int) and size > 0 for size in sizes)
        ):
            splitter.setSizes(sizes)

    def _build_graph_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        self.graph_view.nodeSelected.connect(self._on_graph_node_selected)
        self.graph_view.contextMenuRequested.connect(self._show_graph_context_menu)
        search_row = QWidget()
        search_layout = QHBoxLayout(search_row)
        search_layout.setContentsMargins(0, 0, 0, 0)
        self.graph_search_edit.setPlaceholderText("Search an element in the graph")
        self.graph_search_button.clicked.connect(self._search_graph_node)
        search_layout.addWidget(self.graph_search_edit)
        search_layout.addWidget(self.graph_search_button)

        subgraph_row = QWidget()
        subgraph_layout = QHBoxLayout(subgraph_row)
        subgraph_layout.setContentsMargins(0, 0, 0, 0)
        self.subgraph_center_edit.setPlaceholderText("Subgraph center")
        self.subgraph_depth_edit.setPlaceholderText("Depth")
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
        self.min_weight_edit.setPlaceholderText("Min weight")
        self.max_weight_edit.setPlaceholderText("Max weight")
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
        self.export_graph_button.clicked.connect(self._export_graph_image)
        layout_controls.addWidget(self.layout_iterations_edit)
        layout_controls.addWidget(self.layout_scale_edit)
        layout_controls.addWidget(self.layout_apply_button)
        layout_controls.addWidget(self.export_graph_button)
        layout_controls.addStretch(1)

        self.selected_node_details.setReadOnly(True)
        self.selected_node_details.setMinimumWidth(280)
        self.selected_node_details.setPlainText("No node selected.")

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
        self._graph_bottom_splitter = bottom_splitter
        bottom_splitter.splitterMoved.connect(
            lambda _pos, _index: self._save_ui_preferences_state()
        )
        bottom_splitter.addWidget(details_container)
        bottom_splitter.addWidget(controls_container)
        bottom_splitter.setSizes([420, 680])

        main_splitter = QSplitter(Qt.Vertical)
        self._graph_main_splitter = main_splitter
        main_splitter.splitterMoved.connect(
            lambda _pos, _index: self._save_ui_preferences_state()
        )
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
        self._info_top_splitter = top_splitter
        top_splitter.splitterMoved.connect(
            lambda _pos, _index: self._save_ui_preferences_state()
        )
        self.node_proxy_model.setSourceModel(self.node_model)
        self.edge_proxy_model.setSourceModel(self.edge_model)
        self.discarded_proxy_model.setSourceModel(self.discarded_model)
        self.node_filter_edit.textChanged.connect(self.node_proxy_model.set_filter_text)
        self.edge_filter_edit.textChanged.connect(self.edge_proxy_model.set_filter_text)
        self.discarded_filter_edit.textChanged.connect(
            self.discarded_proxy_model.set_filter_text
        )
        self.node_table.setModel(self.node_proxy_model)
        self.edge_table.setModel(self.edge_proxy_model)
        self.discarded_table.setModel(self.discarded_proxy_model)
        self.node_table.setSortingEnabled(True)
        self.edge_table.setSortingEnabled(True)
        self.discarded_table.setSortingEnabled(True)
        self.node_table.horizontalHeader().setStretchLastSection(True)
        self.edge_table.horizontalHeader().setStretchLastSection(True)
        self.discarded_table.horizontalHeader().setStretchLastSection(True)
        top_splitter.addWidget(
            self._build_info_table_container(
                "Nodes",
                self.node_filter_edit,
                self.node_table,
            )
        )
        top_splitter.addWidget(
            self._build_info_table_container(
                "Edges",
                self.edge_filter_edit,
                self.edge_table,
            )
        )
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
        discarded_layout.addWidget(QLabel("Discarded combinations"))
        discarded_layout.addWidget(self.discarded_filter_edit)
        discarded_layout.addWidget(self.discarded_table)
        discarded_layout.addWidget(self.remove_discarded_button)
        discarded_layout.addWidget(self.reset_discarded_button)
        discarded_layout.addWidget(self.export_discarded_button)
        discarded_layout.addWidget(self.import_discarded_button)

        splitter = QSplitter(Qt.Vertical)
        self._info_splitter = splitter
        splitter.splitterMoved.connect(
            lambda _pos, _index: self._save_ui_preferences_state()
        )
        splitter.addWidget(top_splitter)
        splitter.addWidget(discarded_container)
        splitter.setSizes([700, 220])
        layout.addWidget(splitter)
        return tab

    @staticmethod
    def _build_info_table_container(
        title: str,
        filter_edit,
        table,
    ) -> QWidget:
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(QLabel(title))
        container_layout.addWidget(filter_edit)
        container_layout.addWidget(table)
        return container

    def _build_stats_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        overview_layout = QHBoxLayout(self.stats_overview_group)
        overview_layout.setContentsMargins(12, 12, 12, 12)
        overview_layout.setSpacing(12)
        overview_layout.addWidget(
            self._build_stats_card("Recipes", self.recipe_weight_summary_label)
        )
        overview_layout.addWidget(
            self._build_stats_card("Elements", self.node_weight_summary_label)
        )
        overview_layout.addWidget(
            self._build_stats_card("Missing", self.missing_recipe_summary_label)
        )

        missing_group_layout = QVBoxLayout(self.missing_weight_group)
        missing_group_layout.setContentsMargins(12, 12, 12, 12)
        missing_group_layout.addWidget(self.missing_weight_list)
        self.missing_weight_list.setAlternatingRowColors(True)

        layout.addWidget(self.stats_overview_group)
        layout.addWidget(self.stats_canvas, 2)
        layout.addWidget(self.missing_weight_group, 1)
        return tab

    def _build_communities_tab(self) -> QWidget:
        gui_module = sys.modules[f"{__package__}.gui"]
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.community_algorithm_combo.clear()
        algorithms = gui_module.get_mono_community_algorithms()
        default_algorithm = gui_module.get_default_mono_community_algorithm()
        for algorithm in algorithms:
            self.community_algorithm_combo.addItem(str(algorithm["label"]), algorithm["key"])
        default_index = self.community_algorithm_combo.findData(default_algorithm)
        if default_index >= 0:
            self.community_algorithm_combo.setCurrentIndex(default_index)

        community_mode_layout = QVBoxLayout(self.community_mode_group)
        community_mode_layout.setContentsMargins(12, 12, 12, 12)
        community_mode_layout.addWidget(self.mono_community_mode_label)
        community_mode_layout.addWidget(QLabel("Algorithm"))
        community_mode_layout.addWidget(self.community_algorithm_combo)
        community_mode_layout.addWidget(self.community_compute_button)
        community_mode_layout.addStretch(1)

        summary_layout = QVBoxLayout(self.community_summary_group)
        summary_layout.setContentsMargins(12, 12, 12, 12)
        summary_layout.addWidget(self.community_summary_label)

        community_list_layout = QVBoxLayout(self.community_list_group)
        community_list_layout.setContentsMargins(12, 12, 12, 12)
        self.community_list.setAlternatingRowColors(True)
        community_list_layout.addWidget(self.community_list)

        community_details_layout = QVBoxLayout(self.community_details_group)
        community_details_layout.setContentsMargins(12, 12, 12, 12)
        community_details_layout.addWidget(self.community_details)

        bottom_splitter = QSplitter(Qt.Horizontal)
        bottom_splitter.addWidget(self.community_list_group)
        bottom_splitter.addWidget(self.community_details_group)
        bottom_splitter.setSizes([420, 760])

        top_row = QHBoxLayout()
        top_row.addWidget(self.community_mode_group, 1)
        top_row.addWidget(self.community_summary_group, 2)

        layout.addLayout(top_row)
        layout.addWidget(bottom_splitter, 1)
        return tab

    @staticmethod
    def _build_stats_card(title: str, value_label) -> QWidget:
        card = QGroupBox(title)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.addWidget(value_label)
        return card

    def _pick_input(self) -> None:
        gui_module = sys.modules[f"{__package__}.gui"]
        path, _ = gui_module.QFileDialog.getOpenFileName(
            self,
            "Choose an Infinite Craft save",
            "",
            "All files (*);;JSON (*.json)",
        )
        if path:
            self.input_edit.setText(path)
