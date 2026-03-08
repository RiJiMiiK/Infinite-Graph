from __future__ import annotations

from pathlib import Path
from typing import Callable

from .analyzer import find_missing_combinations, known_recipe_pairs
from .discard_store import load_discarded_pairs
from .graph_model import build_graph_data, build_weight_statistics
from .save_loader import load_save


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

    return {
        "elements": save["elements"],
        "recipes": save["recipes"],
        "load_warnings": save["warnings"],
        "ignored_element_entries": save["ignored_element_entries"],
        "ignored_item_entries": save["ignored_item_entries"],
        "ignored_recipe_entries": save["ignored_recipe_entries"],
        "graph_nodes": graph_data["nodes"],
        "graph_edges": graph_data["edges"],
        "node_weights": graph_data["node_weights"],
        "known_pairs": known_recipe_pairs(save["recipes"]),
        "discarded_pairs": discarded_pairs,
        "done_pairs": set(),
        "statistics": statistics,
        "missing": missing,
        "missing_limit": missing_limit,
        "focus_element": focus_element,
    }
