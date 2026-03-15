from __future__ import annotations

from src.infinite_graph import gui

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
