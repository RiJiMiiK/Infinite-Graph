from __future__ import annotations

from pathlib import Path
from typing import Callable

from .analyzer import build_candidate_index, find_missing_combinations
from .community_analysis import build_cdlib_graph
from .discard_store import load_discarded_pairs
from .graph_model import build_graph_data, build_weight_statistics
from .save_loader import load_save


def select_render_graph_data(
    nodes: list[dict[str, object]],
    edges: list[dict[str, object]],
    focus_element: str | None,
) -> tuple[list[dict[str, object]], list[dict[str, object]], str]:
    _ = focus_element
    return nodes, edges, "complete_graph"


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
    community_graph = build_cdlib_graph(
        graph_data["nodes"],
        graph_data["edges"],
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
        "community_graph": community_graph,
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
