from __future__ import annotations

import pytest
from PySide6.QtCore import QModelIndex

from src.infinite_graph import gui
from src.infinite_graph.gui_table import ContainsFilterProxyModel


@pytest.fixture()
def sample_result() -> dict[str, object]:
    return {
        "elements": ["Water", "Fire", "Wind", "Earth", "Steam"],
        "recipes": [{"left": "Water", "right": "Fire", "result": "Steam"}],
        "load_warnings": [],
        "ignored_element_entries": 0,
        "ignored_item_entries": 0,
        "ignored_recipe_entries": 0,
        "graph_nodes": [],
        "graph_edges": [],
        "node_weights": {"Water": 0, "Fire": 0, "Wind": 0, "Earth": 0, "Steam": 1},
        "known_pairs": {("Fire", "Water")},
        "discarded_pairs": {("Earth", "Wind")},
        "done_pairs": set(),
        "skipped_pairs": set(),
        "statistics": {
            "recipe_counts_by_result_weight": [],
            "node_counts_by_weight": [],
            "missing_counts_by_result_weight": [],
        },
        "missing": [],
        "missing_limit": 1000,
        "focus_element": None,
    }


def test_contains_filter_proxy_model_basic() -> None:
    model = gui.ListTableModel(
        ["Element", "Weight"],
        [["Water", 0], ["Steam", 1]],
    )
    proxy = ContainsFilterProxyModel()
    proxy.set_filter_text("water")
    assert proxy.filterAcceptsRow(0, QModelIndex()) is True

    proxy.setSourceModel(model)
    assert proxy.rowCount() == 1
    proxy.set_filter_text("")
    assert proxy.rowCount() == 2

    proxy.set_filter_text("ste")
    assert proxy.rowCount() == 1
    assert proxy.data(proxy.index(0, 0)) == "Steam"

    proxy.set_filter_text("0")
    assert proxy.rowCount() == 1
    assert proxy.data(proxy.index(0, 0)) == "Water"

    proxy.set_filter_text("missing")
    assert proxy.rowCount() == 0


def test_window_info_table_filters_and_hidden_node_selection(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    sample_result["graph_nodes"] = [
        {"id": "Water", "label": "Water", "weight": 0, "is_starter": True},
        {"id": "Steam", "label": "Steam", "weight": 1, "is_starter": False},
    ]
    sample_result["graph_edges"] = [
        {"source": "Water", "target": "Steam", "weight": 1, "elements": ["Fire"]},
        {"source": "Wind", "target": "Steam", "weight": 1, "elements": ["Water"]},
    ]
    sample_result["discarded_pairs"] = {("Earth", "Wind"), ("Steam", "Water")}

    window.node_model.update_rows([["Water", 0], ["Steam", 1]])
    window.edge_model.update_rows(
        [
            ["Water", "Steam", 1, "Fire"],
            ["Wind", "Steam", 1, "Water"],
        ]
    )
    window._refresh_discarded_table()

    window.node_filter_edit.setText("ste")
    assert window.node_proxy_model.rowCount() == 1
    assert window.node_proxy_model.data(window.node_proxy_model.index(0, 0)) == "Steam"

    window.edge_filter_edit.setText("water")
    assert window.edge_proxy_model.rowCount() == 2
    window.edge_filter_edit.setText("fire")
    assert window.edge_proxy_model.rowCount() == 1
    assert window.edge_proxy_model.data(window.edge_proxy_model.index(0, 0)) == "Water"

    window.discarded_filter_edit.setText("steam")
    assert window.discarded_proxy_model.rowCount() == 1
    assert (
        window.discarded_proxy_model.data(window.discarded_proxy_model.index(0, 0))
        == "Steam"
    )

    window.node_filter_edit.setText("steam")
    window._on_graph_node_selected("Water")
    assert window.node_table.selectionModel().hasSelection() is False
    window.close()
