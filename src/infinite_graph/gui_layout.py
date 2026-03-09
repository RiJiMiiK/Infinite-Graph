"""Graph rendering and layout helpers for the Qt GUI."""

import hashlib
import json
import time
from contextlib import suppress
from pathlib import Path
from typing import Callable

import networkx as nx
import numpy as np
import pyqtgraph as pg

from .gui_constants import (
    GENERATION_STAGE_PROGRESS,
    LAYOUT_CACHE_VERSION,
    LAYOUT_PROGRESS_END,
    LAYOUT_PROGRESS_START,
)


def build_graph_render_data(
    nodes: list[dict[str, object]],
    edges: list[dict[str, object]],
    progress_callback: Callable[[int, str], None] | None = None,
    layout_iterations: int = 80,
    spring_scale: float = 1.2,
    cache_save_path: Path | None = None,
) -> dict[str, object]:
    ordered_nodes = sorted(nodes, key=lambda item: str(item["id"]))
    names = [str(node["id"]) for node in ordered_nodes]
    if progress_callback is not None:
        progress_callback(
            GENERATION_STAGE_PROGRESS["Preparing graph structure"],
            "Preparing graph structure",
        )
    graph = nx.DiGraph()
    graph.add_nodes_from(names)
    graph.add_edges_from((str(edge["source"]), str(edge["target"])) for edge in edges)

    positions = _compute_layout_positions(
        graph,
        names,
        layout_iterations,
        spring_scale,
        progress_callback,
        cache_save_path,
    )

    index_by_name = {name: idx for idx, name in enumerate(names)}
    adj = []
    for edge in edges:
        source = index_by_name.get(str(edge["source"]))
        target = index_by_name.get(str(edge["target"]))
        if source is not None and target is not None:
            adj.append((source, target))

    symbol_brush = []
    sizes = []
    for node in ordered_nodes:
        weight = node["weight"]
        symbol_brush.append(pg.mkBrush("#10b981" if node["is_starter"] else "#2563eb"))
        sizes.append(16 if weight is None else max(6, 16 - min(int(weight), 10) * 0.5))

    labels = []
    if len(nodes) <= 120:
        labels = [
            {"text": str(node["label"]), "x": x, "y": y}
            for node, (x, y) in zip(ordered_nodes, positions)
        ]

    return {
        "positions": positions,
        "adj": adj,
        "sizes": sizes,
        "brushes": symbol_brush,
        "labels": labels,
        "node_ids": names,
        "node_weights": [node["weight"] for node in ordered_nodes],
    }


def _compute_layout_positions(
    graph: nx.DiGraph,
    names: list[str],
    layout_iterations: int,
    spring_scale: float,
    progress_callback: Callable[[int, str], None] | None,
    cache_save_path: Path | None,
) -> list[tuple[float, float]]:
    total_iterations = max(1, layout_iterations)
    batch_size = 5
    if progress_callback is not None:
        progress_callback(
            GENERATION_STAGE_PROGRESS["Checking layout cache"],
            "Checking layout cache",
        )

    if cache_save_path is not None:
        cached_positions = load_cached_layout(
            cache_save_path,
            names,
            layout_iterations,
            spring_scale,
        )
        if cached_positions is not None:
            if progress_callback is not None:
                progress_callback(
                    GENERATION_STAGE_PROGRESS["Loading cached layout"],
                    "Loading cached layout",
                )
                progress_callback(
                    GENERATION_STAGE_PROGRESS["Finalizing graph geometry"],
                    "Finalizing graph geometry",
                )
            return cached_positions

    spring_positions = _run_spring_layout(
        graph,
        names,
        total_iterations,
        batch_size,
        spring_scale,
        progress_callback,
    )
    positions = [
        (
            float(spring_positions[name][0] * 2000.0),
            float(spring_positions[name][1] * 2000.0),
        )
        for name in names
    ]
    if progress_callback is not None:
        progress_callback(
            GENERATION_STAGE_PROGRESS["Finalizing graph geometry"],
            "Finalizing graph geometry",
        )
    if cache_save_path is not None:
        save_cached_layout(
            cache_save_path,
            names,
            positions,
            layout_iterations,
            spring_scale,
        )
    return positions


def _run_spring_layout(
    graph: nx.DiGraph,
    names: list[str],
    total_iterations: int,
    batch_size: int,
    spring_scale: float,
    progress_callback: Callable[[int, str], None] | None,
) -> dict[str, np.ndarray]:
    layout_graph, layout_kwargs = _spring_layout_strategy(graph, names, spring_scale)
    spring_positions = None
    started_at = time.perf_counter()
    if progress_callback is not None:
        progress_callback(
            GENERATION_STAGE_PROGRESS["Initializing spring layout"],
            "Initializing spring layout",
        )
    for current_iteration in range(0, total_iterations, batch_size):
        iterations = min(batch_size, total_iterations - current_iteration)
        spring_positions = nx.spring_layout(
            layout_graph,
            iterations=iterations,
            pos=spring_positions,
            **layout_kwargs,
        )
        if progress_callback is not None:
            completed = current_iteration + iterations
            elapsed = time.perf_counter() - started_at
            eta = (
                0.0
                if completed == 0
                else max(0.0, elapsed * (total_iterations - completed) / completed)
            )
            progress = LAYOUT_PROGRESS_START + int(
                (completed / total_iterations) * (LAYOUT_PROGRESS_END - LAYOUT_PROGRESS_START)
            )
            progress_callback(
                min(progress, LAYOUT_PROGRESS_END),
                f"Computing spring layout: {completed}/{total_iterations} iterations "
                f"(elapsed {elapsed:.1f}s, ETA {eta:.1f}s)",
            )
    assert spring_positions is not None
    return spring_positions


def _spring_layout_strategy(
    graph: nx.DiGraph,
    names: list[str],
    spring_scale: float,
) -> tuple[nx.Graph, dict[str, object]]:
    node_count = len(names)
    layout_graph = graph.to_undirected(as_view=True)
    layout_kwargs: dict[str, object] = {
        "seed": 42,
        "k": None if node_count < 2 else spring_scale / np.sqrt(node_count),
    }
    if node_count >= 300:
        layout_kwargs["method"] = "energy"
        layout_kwargs["threshold"] = 1e-3
    return layout_graph, layout_kwargs


def layout_cache_dir() -> Path:
    root_dir = Path(__file__).resolve().parents[2]
    return root_dir / ".cache" / "infinite_graph" / "layouts"


def _layout_cache_file(
    save_path: Path,
    layout_iterations: int,
    spring_scale: float,
) -> Path:
    file_stat = save_path.stat()
    cache_key = hashlib.sha256(
        (
            f"{LAYOUT_CACHE_VERSION}|{save_path.resolve()}|{file_stat.st_size}|"
            f"{file_stat.st_mtime_ns}|{layout_iterations}|{spring_scale:.6f}"
        ).encode("utf-8")
    ).hexdigest()
    return layout_cache_dir() / f"{cache_key}.json"


def load_cached_layout(
    save_path: Path,
    node_ids: list[str],
    layout_iterations: int,
    spring_scale: float,
) -> list[tuple[float, float]] | None:
    cache_file = _layout_cache_file(save_path, layout_iterations, spring_scale)
    if not cache_file.is_file():
        return None

    with suppress(OSError, ValueError, TypeError, KeyError):
        cache_payload = json.loads(cache_file.read_text(encoding="utf-8"))
        if cache_payload["version"] != LAYOUT_CACHE_VERSION:
            return None
        if cache_payload["node_ids"] != node_ids:
            return None
        return [(float(position[0]), float(position[1])) for position in cache_payload["positions"]]
    return None


def save_cached_layout(
    save_path: Path,
    node_ids: list[str],
    positions: list[tuple[float, float]],
    layout_iterations: int,
    spring_scale: float,
) -> None:
    cache_file = _layout_cache_file(save_path, layout_iterations, spring_scale)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(
        json.dumps(
            {
                "version": LAYOUT_CACHE_VERSION,
                "node_ids": node_ids,
                "positions": positions,
            }
        ),
        encoding="utf-8",
    )


def build_subgraph_render_data(
    render_data: dict[str, object],
    center_node_id: str,
    max_depth: int,
) -> dict[str, object] | None:
    node_ids = list(render_data.get("node_ids", []))
    if center_node_id not in node_ids or max_depth < 0:
        return None

    adjacency: dict[int, set[int]] = {index: set() for index in range(len(node_ids))}
    for source_index, target_index in render_data.get("adj", []):
        if 0 <= source_index < len(node_ids) and 0 <= target_index < len(node_ids):
            adjacency[source_index].add(target_index)
            adjacency[target_index].add(source_index)

    center_index = node_ids.index(center_node_id)
    visited = {center_index}
    frontier = {center_index}
    for _ in range(max_depth):
        next_frontier = set()
        for node_index in frontier:
            next_frontier.update(adjacency.get(node_index, set()) - visited)
        visited.update(next_frontier)
        frontier = next_frontier
        if not frontier:
            break

    kept_indices = sorted(visited)
    index_map = {old_index: new_index for new_index, old_index in enumerate(kept_indices)}
    labels = render_data.get("labels", [])
    filtered_labels = []
    if len(labels) == len(node_ids):
        filtered_labels = [labels[index] for index in kept_indices]

    return {
        "positions": [render_data["positions"][index] for index in kept_indices],
        "adj": [
            (index_map[source_index], index_map[target_index])
            for source_index, target_index in render_data.get("adj", [])
            if source_index in index_map and target_index in index_map
        ],
        "sizes": [render_data["sizes"][index] for index in kept_indices],
        "brushes": [render_data["brushes"][index] for index in kept_indices],
        "labels": filtered_labels,
        "node_ids": [node_ids[index] for index in kept_indices],
        "node_weights": [render_data["node_weights"][index] for index in kept_indices],
    }


def build_weight_filtered_render_data(
    render_data: dict[str, object],
    min_weight: int | None,
    max_weight: int | None,
) -> dict[str, object]:
    node_weights = list(render_data.get("node_weights", []))
    kept_indices = []
    for index, weight in enumerate(node_weights):
        if weight is None:
            continue
        if min_weight is not None and int(weight) < min_weight:
            continue
        if max_weight is not None and int(weight) > max_weight:
            continue
        kept_indices.append(index)

    index_map = {old_index: new_index for new_index, old_index in enumerate(kept_indices)}
    labels = render_data.get("labels", [])
    filtered_labels = []
    if len(labels) == len(node_weights):
        filtered_labels = [labels[index] for index in kept_indices]

    return {
        "positions": [render_data["positions"][index] for index in kept_indices],
        "adj": [
            (index_map[source_index], index_map[target_index])
            for source_index, target_index in render_data.get("adj", [])
            if source_index in index_map and target_index in index_map
        ],
        "sizes": [render_data["sizes"][index] for index in kept_indices],
        "brushes": [render_data["brushes"][index] for index in kept_indices],
        "labels": filtered_labels,
        "node_ids": [render_data["node_ids"][index] for index in kept_indices],
        "node_weights": [node_weights[index] for index in kept_indices],
    }
