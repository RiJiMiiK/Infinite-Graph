from __future__ import annotations

import networkx as nx

from src.infinite_graph import gui_layout


def test_spring_layout_strategy_uses_energy_method_for_large_graph() -> None:
    graph = nx.DiGraph()
    node_ids = [f"Node {index}" for index in range(300)]
    graph.add_nodes_from(node_ids)
    graph.add_edges_from((node_ids[index], node_ids[index + 1]) for index in range(299))

    layout_graph, layout_kwargs = gui_layout._spring_layout_strategy(graph, node_ids, 1.2)

    assert not layout_graph.is_directed()
    assert layout_kwargs["method"] == "energy"
    assert layout_kwargs["threshold"] == 1e-3


def test_spring_layout_strategy_keeps_default_method_for_small_graph() -> None:
    graph = nx.DiGraph()
    node_ids = ["Water", "Fire"]
    graph.add_nodes_from(node_ids)
    graph.add_edge("Water", "Fire")

    layout_graph, layout_kwargs = gui_layout._spring_layout_strategy(graph, node_ids, 1.2)

    assert not layout_graph.is_directed()
    assert "method" not in layout_kwargs
    assert "threshold" not in layout_kwargs
