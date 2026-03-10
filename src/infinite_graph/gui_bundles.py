"""Widget bundle factories for the main Qt window."""

from types import SimpleNamespace

from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import (
    QCompleter,
    QFrame,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QProgressBar,
    QPushButton,
    QTableView,
    QTextEdit,
)

from .gui_table import ContainsFilterProxyModel, ListTableModel
from .gui_widgets import CopyLineEdit, GraphViewWidget, StatsCanvas


def create_controls_bundle(parent) -> SimpleNamespace:
    bundle = SimpleNamespace(
        input_edit=QLineEdit(),
        focus_edit=QLineEdit(),
        element1_edit=CopyLineEdit(),
        element2_edit=CopyLineEdit(),
        element_completer_model=QStringListModel(),
        generate_button=QPushButton("Generate"),
        random_button=QPushButton("Random"),
        cheapest_button=QPushButton("Cheapest"),
        next_button=QPushButton("Next"),
        done_button=QPushButton("Done"),
        undo_done_button=QPushButton("Undo Done"),
        discard_button=QPushButton("Discard"),
        undo_discard_button=QPushButton("Undo Discard"),
        progress_bar=QProgressBar(),
        summary_label=QLabel("Load an Infinite Craft save to build the graph."),
        stage_label=QLabel("Idle"),
        candidate_status_label=QLabel("Combination status: none"),
        candidate_count_label=QLabel("Remaining candidate combinations: no save loaded"),
        current_candidate_toggle_button=QPushButton("Show candidate details"),
        current_candidate_details=QTextEdit(),
        history_toggle_button=QPushButton("Show history"),
        history_panel=QFrame(),
        summary_toggle_button=QPushButton("Show details"),
        summary_panel=QFrame(),
        suggestion_history_list=QListWidget(),
    )
    bundle.summary_label.setWordWrap(True)
    bundle.candidate_status_label.setWordWrap(True)
    bundle.candidate_count_label.setWordWrap(True)
    bundle.generate_button.setObjectName("primaryButton")
    bundle.discard_button.setObjectName("dangerButton")
    bundle.current_candidate_details.setReadOnly(True)
    bundle.current_candidate_details.setMaximumHeight(90)
    bundle.current_candidate_details.setPlainText("No current combination.")
    bundle.summary_toggle_button.setMaximumWidth(220)
    bundle.history_panel.setFrameShape(QFrame.StyledPanel)
    bundle.history_panel.setVisible(False)
    bundle.summary_panel.setFrameShape(QFrame.StyledPanel)
    bundle.summary_panel.setVisible(False)
    bundle.element1_completer = QCompleter(bundle.element_completer_model, parent)
    bundle.element2_completer = QCompleter(bundle.element_completer_model, parent)
    return bundle


def create_graph_bundle() -> SimpleNamespace:
    return SimpleNamespace(
        graph_view=GraphViewWidget(),
        selected_node_label=QLabel("Selected node: none"),
        selected_node_details=QTextEdit(),
        graph_search_edit=QLineEdit(),
        graph_search_button=QPushButton("Search"),
        subgraph_center_edit=QLineEdit(),
        subgraph_depth_edit=QLineEdit("1"),
        subgraph_button=QPushButton("Apply subgraph"),
        subgraph_reset_button=QPushButton("Reset"),
        min_weight_edit=QLineEdit(),
        max_weight_edit=QLineEdit(),
        weight_filter_button=QPushButton("Filter weights"),
        layout_iterations_edit=QLineEdit("80"),
        layout_scale_edit=QLineEdit("1.2"),
        layout_apply_button=QPushButton("Apply layout"),
        export_graph_button=QPushButton("Export image"),
    )


def create_info_bundle() -> SimpleNamespace:
    bundle = SimpleNamespace(
        node_model=ListTableModel(["Element", "Weight"]),
        edge_model=ListTableModel(["Source", "Target", "Weight", "Element list"]),
        discarded_model=ListTableModel(["Element 1", "Element 2"]),
        node_proxy_model=ContainsFilterProxyModel(),
        edge_proxy_model=ContainsFilterProxyModel(),
        discarded_proxy_model=ContainsFilterProxyModel(),
        node_table=QTableView(),
        edge_table=QTableView(),
        discarded_table=QTableView(),
        node_filter_edit=QLineEdit(),
        edge_filter_edit=QLineEdit(),
        discarded_filter_edit=QLineEdit(),
        remove_discarded_button=QPushButton("Remove selection"),
        reset_discarded_button=QPushButton("Reset discarded"),
        export_discarded_button=QPushButton("Export discarded"),
        import_discarded_button=QPushButton("Import discarded"),
    )
    bundle.reset_discarded_button.setObjectName("dangerButton")
    bundle.node_filter_edit.setPlaceholderText("Filter nodes")
    bundle.edge_filter_edit.setPlaceholderText("Filter edges")
    bundle.discarded_filter_edit.setPlaceholderText("Filter discarded combinations")
    bundle.node_filter_edit.setClearButtonEnabled(True)
    bundle.edge_filter_edit.setClearButtonEnabled(True)
    bundle.discarded_filter_edit.setClearButtonEnabled(True)
    return bundle


def create_stats_bundle() -> SimpleNamespace:
    bundle = SimpleNamespace(
        stats_canvas=StatsCanvas(),
        missing_weight_list=QListWidget(),
        stats_overview_group=QGroupBox("Overview"),
        recipe_weight_summary_label=QLabel("Recipe series: no data"),
        node_weight_summary_label=QLabel("Element series: no data"),
        missing_recipe_summary_label=QLabel("Missing recipes: no data"),
        missing_weight_group=QGroupBox("Missing recipes by result weight"),
    )
    bundle.recipe_weight_summary_label.setWordWrap(True)
    bundle.node_weight_summary_label.setWordWrap(True)
    bundle.missing_recipe_summary_label.setWordWrap(True)
    return bundle
