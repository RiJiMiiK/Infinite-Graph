"""State and summary helpers for the Qt GUI."""


def build_summary_text(result: dict[str, object], elapsed_seconds: float | None = None) -> str:
    lines = [
        f"Elements charges : {len(result['elements'])}",
        f"Recettes chargees : {len(result['recipes'])}",
        f"Entrees element ignorees : {result['ignored_element_entries']}",
        f"Entrees item ignorees : {result['ignored_item_entries']}",
        f"Entrees recette ignorees : {result['ignored_recipe_entries']}",
        f"Noeuds du graphe : {len(result['graph_nodes'])}",
        f"Edges du graphe : {len(result['graph_edges'])}",
        (
            "Noeuds affiches dans le graphe : "
            f"{len(result.get('render_graph_nodes', result['graph_nodes']))}"
        ),
        (
            "Edges affiches dans le graphe : "
            f"{len(result.get('render_graph_edges', result['graph_edges']))}"
        ),
        f"Mode de rendu du graphe : {result.get('render_scope', 'complete_graph')}",
        f"Combinaisons manquantes calculees : {len(result['missing'])}",
        f"Combinaisons discardees : {len(result['discarded_pairs'])}",
        f"Combinaisons done session : {len(result['done_pairs'])}",
        f"Element cible : {result['focus_element'] or 'aucun'}",
    ]
    if elapsed_seconds is not None:
        lines.append(f"Temps total de generation : {elapsed_seconds:.2f}s")
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
