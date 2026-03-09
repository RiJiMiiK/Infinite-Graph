from __future__ import annotations

from src.infinite_graph import service


def test_select_render_graph_data_keeps_complete_graph_when_under_limits() -> None:
    nodes = [
        {"id": "Water", "label": "Water", "weight": 0, "is_starter": True},
        {"id": "Fire", "label": "Fire", "weight": 0, "is_starter": True},
    ]
    edges = [{"source": "Water", "target": "Fire", "weight": 1, "elements": ["Steam"]}]

    render_nodes, render_edges, render_scope = service.select_render_graph_data(
        nodes,
        edges,
        focus_element=None,
        node_limit=10,
        edge_limit=10,
    )

    assert render_nodes == nodes
    assert render_edges == edges
    assert render_scope == "complete_graph"


def test_select_render_graph_data_prefers_focused_subgraph_for_large_graph() -> None:
    nodes = [
        {"id": f"Node {index}", "label": f"Node {index}", "weight": index, "is_starter": False}
        for index in range(8)
    ]
    edges = [
        {"source": f"Node {index}", "target": f"Node {index + 1}", "weight": 1, "elements": ["x"]}
        for index in range(7)
    ]

    render_nodes, render_edges, render_scope = service.select_render_graph_data(
        nodes,
        edges,
        focus_element="Node 4",
        node_limit=5,
        edge_limit=10,
    )

    render_node_ids = {str(node["id"]) for node in render_nodes}
    assert "Node 4" in render_node_ids
    assert len(render_nodes) <= 5
    assert render_scope == "focused_subgraph"
    assert all(
        str(edge["source"]) in render_node_ids and str(edge["target"]) in render_node_ids
        for edge in render_edges
    )


def test_select_render_graph_data_limits_centered_frontier_when_needed() -> None:
    nodes = [
        {"id": "Center", "label": "Center", "weight": 0, "is_starter": False},
        {"id": "A", "label": "A", "weight": 1, "is_starter": False},
        {"id": "B", "label": "B", "weight": 1, "is_starter": False},
        {"id": "C", "label": "C", "weight": 1, "is_starter": False},
        {"id": "D", "label": "D", "weight": 1, "is_starter": False},
    ]
    edges = [
        {"source": "Center", "target": "A", "weight": 1, "elements": ["x"]},
        {"source": "Center", "target": "B", "weight": 1, "elements": ["x"]},
        {"source": "Center", "target": "C", "weight": 1, "elements": ["x"]},
        {"source": "Center", "target": "D", "weight": 1, "elements": ["x"]},
    ]

    render_nodes, render_edges, render_scope = service.select_render_graph_data(
        nodes,
        edges,
        focus_element="Center",
        node_limit=3,
        edge_limit=10,
    )

    assert render_scope == "focused_subgraph"
    assert [str(node["id"]) for node in render_nodes] == ["Center", "A", "B"]
    assert len(render_edges) == 2


def test_select_render_graph_data_falls_back_to_reduced_subgraph() -> None:
    nodes = [
        {"id": "Water", "label": "Water", "weight": 0, "is_starter": True},
        {"id": "Fire", "label": "Fire", "weight": 0, "is_starter": True},
        {"id": "Wind", "label": "Wind", "weight": 0, "is_starter": True},
        {"id": "Earth", "label": "Earth", "weight": 0, "is_starter": True},
        {"id": "Steam", "label": "Steam", "weight": 1, "is_starter": False},
        {"id": "Cloud", "label": "Cloud", "weight": 2, "is_starter": False},
    ]
    edges = [
        {"source": "Water", "target": "Steam", "weight": 1, "elements": ["Fire"]},
        {"source": "Fire", "target": "Steam", "weight": 1, "elements": ["Water"]},
        {"source": "Steam", "target": "Cloud", "weight": 1, "elements": ["Wind"]},
        {"source": "Wind", "target": "Cloud", "weight": 1, "elements": ["Steam"]},
    ]

    render_nodes, render_edges, render_scope = service.select_render_graph_data(
        nodes,
        edges,
        focus_element="Ghost",
        node_limit=3,
        edge_limit=2,
    )

    assert render_scope == "reduced_subgraph"
    assert [str(node["id"]) for node in render_nodes] == ["Water", "Fire", "Earth"]
    assert len(render_edges) <= 2
