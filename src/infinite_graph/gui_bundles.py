"""Widget bundle factories for the main Qt window."""

from types import SimpleNamespace

from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import (
    QCompleter,
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QProgressBar,
    QPushButton,
    QTableView,
    QTextEdit,
)

from .gui_table import ListTableModel
from .gui_widgets import CopyLineEdit, GraphViewWidget, StatsCanvas


def create_controls_bundle(parent) -> SimpleNamespace:
    bundle = SimpleNamespace(
        input_edit=QLineEdit(),
        focus_edit=QLineEdit(),
        element1_edit=CopyLineEdit(),
        element2_edit=CopyLineEdit(),
        element_completer_model=QStringListModel(),
        generate_button=QPushButton("Generer"),
        random_button=QPushButton("Random"),
        cheapest_button=QPushButton("Cheapest"),
        next_button=QPushButton("Next"),
        done_button=QPushButton("Done"),
        undo_done_button=QPushButton("Undo Done"),
        discard_button=QPushButton("Discard"),
        undo_discard_button=QPushButton("Undo Discard"),
        progress_bar=QProgressBar(),
        summary_label=QLabel("Charge une sauvegarde Infinite Craft pour construire le graphe."),
        stage_label=QLabel("Idle"),
        summary_toggle_button=QPushButton("Afficher details"),
        summary_panel=QFrame(),
        suggestion_history_list=QListWidget(),
    )
    bundle.summary_label.setWordWrap(True)
    bundle.summary_panel.setFrameShape(QFrame.StyledPanel)
    bundle.summary_panel.setVisible(False)
    bundle.element1_completer = QCompleter(bundle.element_completer_model, parent)
    bundle.element2_completer = QCompleter(bundle.element_completer_model, parent)
    return bundle


def create_graph_bundle() -> SimpleNamespace:
    return SimpleNamespace(
        graph_view=GraphViewWidget(),
        selected_node_label=QLabel("Noeud selectionne : aucun"),
        selected_node_details=QTextEdit(),
        graph_search_edit=QLineEdit(),
        graph_search_button=QPushButton("Rechercher"),
        subgraph_center_edit=QLineEdit(),
        subgraph_depth_edit=QLineEdit("1"),
        subgraph_button=QPushButton("Sous-graphe"),
        subgraph_reset_button=QPushButton("Reinitialiser"),
        min_weight_edit=QLineEdit(),
        max_weight_edit=QLineEdit(),
        weight_filter_button=QPushButton("Filtrer poids"),
        layout_iterations_edit=QLineEdit("80"),
        layout_scale_edit=QLineEdit("1.2"),
        layout_apply_button=QPushButton("Appliquer layout"),
    )


def create_info_bundle() -> SimpleNamespace:
    return SimpleNamespace(
        node_model=ListTableModel(["Element", "Poids"]),
        edge_model=ListTableModel(["Source", "Cible", "Poids", "Liste d'elements"]),
        discarded_model=ListTableModel(["Element 1", "Element 2"]),
        node_table=QTableView(),
        edge_table=QTableView(),
        discarded_table=QTableView(),
        remove_discarded_button=QPushButton("Supprimer la selection"),
        reset_discarded_button=QPushButton("Reset discarded"),
    )


def create_stats_bundle() -> SimpleNamespace:
    return SimpleNamespace(
        stats_canvas=StatsCanvas(),
        missing_weight_list=QListWidget(),
    )
