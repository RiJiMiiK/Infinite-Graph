"""State and summary helpers for the Qt GUI."""


def build_summary_text(result: dict[str, object], elapsed_seconds: float | None = None) -> str:
    lines = [
        f"Loaded elements: {len(result['elements'])}",
        f"Loaded recipes: {len(result['recipes'])}",
        f"Ignored element entries: {result['ignored_element_entries']}",
        f"Ignored item entries: {result['ignored_item_entries']}",
        f"Ignored recipe entries: {result['ignored_recipe_entries']}",
        f"Graph nodes: {len(result['graph_nodes'])}",
        f"Graph edges: {len(result['graph_edges'])}",
        (
            "Rendered graph nodes: "
            f"{len(result.get('render_graph_nodes', result['graph_nodes']))}"
        ),
        (
            "Rendered graph edges: "
            f"{len(result.get('render_graph_edges', result['graph_edges']))}"
        ),
        f"Graph render mode: {result.get('render_scope', 'complete_graph')}",
        f"Computed missing combinations: {len(result['missing'])}",
        f"Discarded combinations: {len(result['discarded_pairs'])}",
        f"Session done combinations: {len(result['done_pairs'])}",
        f"Focus element: {result['focus_element'] or 'none'}",
    ]
    if elapsed_seconds is not None:
        lines.append(f"Total generation time: {elapsed_seconds:.2f}s")
    return "\n".join(lines)


def update_missing_statistics_for_pair(
    result: dict[str, object],
    delta: int,
    candidate_weight: int | None,
) -> None:
    if candidate_weight is None:
        return

    updated = []
    found = False
    for weight, count in result["statistics"]["missing_counts_by_result_weight"]:
        if weight == candidate_weight:
            found = True
            new_count = count + delta
            if new_count > 0:
                updated.append((weight, new_count))
        else:
            updated.append((weight, count))
    if not found and delta > 0:
        updated.append((candidate_weight, delta))
    result["statistics"]["missing_counts_by_result_weight"] = sorted(updated)
