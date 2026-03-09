from __future__ import annotations

from pathlib import Path
from typing import Callable

from .analyzer import build_candidate_index, find_missing_combinations
from .discard_store import load_discarded_pairs
from .graph_model import build_graph_data, build_weight_statistics
from .save_loader import load_save

RENDER_NODE_LIMIT = 1500
RENDER_EDGE_LIMIT = 6000


def _induce_render_subgraph(
    nodes: list[dict[str, object]],
    edges: list[dict[str, object]],
    kept_node_ids: set[str],
    edge_limit: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    kept_nodes = [node for node in nodes if str(node["id"]) in kept_node_ids]
    kept_edges = [
        edge
        for edge in edges
        if str(edge["source"]) in kept_node_ids and str(edge["target"]) in kept_node_ids
    ]
    return kept_nodes, kept_edges[:edge_limit]


def _select_centered_render_subgraph(
    nodes: list[dict[str, object]],
    edges: list[dict[str, object]],
    center_node_id: str,
    node_limit: int,
    edge_limit: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]] | None:
    adjacency: dict[str, set[str]] = {str(node["id"]): set() for node in nodes}
    for edge in edges:
        source = str(edge["source"])
        target = str(edge["target"])
        adjacency.setdefault(source, set()).add(target)
        adjacency.setdefault(target, set()).add(source)

    kept_node_ids = {center_node_id}
    frontier = {center_node_id}
    while frontier and len(kept_node_ids) < node_limit:
        next_frontier = set()
        for node_id in frontier:
            next_frontier.update(adjacency.get(node_id, set()) - kept_node_ids)
        if not next_frontier:
            break
        if len(kept_node_ids) + len(next_frontier) > node_limit:
            ordered_next = sorted(next_frontier)
            next_frontier = set(ordered_next[: node_limit - len(kept_node_ids)])
        kept_node_ids.update(next_frontier)
        frontier = next_frontier

    kept_nodes, kept_edges = _induce_render_subgraph(nodes, edges, kept_node_ids, edge_limit)
    if not kept_nodes:
        return None
    return kept_nodes, kept_edges


def _select_reduced_render_subgraph(
    nodes: list[dict[str, object]],
    edges: list[dict[str, object]],
    node_limit: int,
    edge_limit: int,
    preferred_node_ids: set[str] | None = None,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    preferred_node_ids = preferred_node_ids or set()
    sorted_nodes = sorted(
        nodes,
        key=lambda node: (
            str(node["id"]) not in preferred_node_ids,
            node["weight"] is None,
            node["weight"] if node["weight"] is not None else 10**9,
            str(node["label"]),
        ),
    )
    kept_node_ids = {str(node["id"]) for node in sorted_nodes[:node_limit]}
    return _induce_render_subgraph(nodes, edges, kept_node_ids, edge_limit)


def select_render_graph_data(
    nodes: list[dict[str, object]],
    edges: list[dict[str, object]],
    focus_element: str | None,
    node_limit: int = RENDER_NODE_LIMIT,
    edge_limit: int = RENDER_EDGE_LIMIT,
) -> tuple[list[dict[str, object]], list[dict[str, object]], str]:
    if len(nodes) <= node_limit and len(edges) <= edge_limit:
        return nodes, edges, "complete_graph"

    if focus_element:
        centered = _select_centered_render_subgraph(
            nodes,
            edges,
            focus_element,
            node_limit,
            edge_limit,
        )
        if centered is not None:
            return centered[0], centered[1], "focused_subgraph"

    reduced_nodes, reduced_edges = _select_reduced_render_subgraph(
        nodes,
        edges,
        node_limit,
        edge_limit,
        preferred_node_ids={focus_element} if focus_element else None,
    )
    return reduced_nodes, reduced_edges, "reduced_subgraph"


def process_save(
    input_path: Path,
    missing_limit: int = 1000,
    focus_element: str | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> dict[str, object]:
    if progress_callback is not None:
        progress_callback("Loading save file")
    save = load_save(input_path)
    if progress_callback is not None:
        progress_callback("Loading discarded combinations")
    discarded_pairs = load_discarded_pairs(input_path)
    if progress_callback is not None:
        progress_callback("Building graph model")
    graph_data = build_graph_data(
        save["elements"],
        save["recipes"],
        recipe_limit=None,
    )
    if progress_callback is not None:
        progress_callback("Computing graph statistics")
    statistics = build_weight_statistics(
        save["elements"],
        save["recipes"],
        graph_data["node_weights"],
        discarded_pairs=discarded_pairs,
    )
    if progress_callback is not None:
        progress_callback("Computing missing combinations")
    missing = find_missing_combinations(
        save["elements"],
        save["recipes"],
        limit=missing_limit,
        focus_element=focus_element,
        discarded_pairs=discarded_pairs,
    )
    candidate_index = build_candidate_index(
        save["elements"],
        save["recipes"],
        graph_data["node_weights"],
        focus_element=focus_element,
        discarded_pairs=discarded_pairs,
    )
    render_graph_nodes, render_graph_edges, render_scope = select_render_graph_data(
        graph_data["nodes"],
        graph_data["edges"],
        focus_element,
    )

    return {
        "elements": save["elements"],
        "recipes": save["recipes"],
        "load_warnings": save["warnings"],
        "ignored_element_entries": save["ignored_element_entries"],
        "ignored_item_entries": save["ignored_item_entries"],
        "ignored_recipe_entries": save["ignored_recipe_entries"],
        "graph_nodes": graph_data["nodes"],
        "graph_edges": graph_data["edges"],
        "render_graph_nodes": render_graph_nodes,
        "render_graph_edges": render_graph_edges,
        "render_scope": render_scope,
        "node_weights": graph_data["node_weights"],
        "known_pairs": candidate_index["known_pairs"],
        "candidate_pairs": candidate_index["all_pairs"],
        "candidate_pairs_by_weight": candidate_index["cheapest_pairs"],
        "discarded_pairs": discarded_pairs,
        "done_pairs": set(),
        "skipped_pairs": set(),
        "statistics": statistics,
        "missing": missing,
        "missing_limit": missing_limit,
        "focus_element": focus_element,
    }
