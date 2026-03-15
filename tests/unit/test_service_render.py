from __future__ import annotations

from src.infinite_graph import service


def test_select_render_graph_data_always_returns_complete_graph() -> None:
    nodes = [
        {"id": "Water", "label": "Water", "weight": 0, "is_starter": True},
        {"id": "Steam", "label": "Steam", "weight": 1, "is_starter": False},
    ]
    edges = [{"source": "Water", "target": "Steam", "weight": 1, "elements": ["Fire"]}]

    render_nodes, render_edges, render_scope = service.select_render_graph_data(
        nodes,
        edges,
        focus_element="Steam",
    )

    assert render_nodes == nodes
    assert render_edges == edges
    assert render_scope == "complete_graph"
