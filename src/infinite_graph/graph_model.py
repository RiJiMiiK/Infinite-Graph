from __future__ import annotations

from collections import defaultdict
from heapq import heappop, heappush
from math import inf

from .analyzer import known_recipe_pairs

STARTER_ELEMENTS = ("Water", "Fire", "Wind", "Earth")


def validate_starter_elements(elements: list[str]) -> None:
    missing = [element for element in STARTER_ELEMENTS if element not in elements]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Save invalide: starter element manquant: {missing_text}")


def compute_node_weights(
    elements: list[str],
    recipes: list[dict[str, str]],
) -> dict[str, int | None]:
    validate_starter_elements(elements)

    weights: dict[str, float] = {element: inf for element in elements}
    dependents: dict[str, list[dict[str, str]]] = defaultdict(list)

    for recipe in recipes:
        dependents[recipe["left"]].append(recipe)
        dependents[recipe["right"]].append(recipe)

    heap: list[tuple[int, str]] = []
    for starter in STARTER_ELEMENTS:
        weights[starter] = 0
        heappush(heap, (0, starter))

    while heap:
        current_weight, element = heappop(heap)
        if current_weight != weights.get(element):
            continue

        for recipe in dependents.get(element, []):
            left_weight = weights.get(recipe["left"], inf)
            right_weight = weights.get(recipe["right"], inf)
            if left_weight == inf or right_weight == inf:
                continue

            candidate = int(left_weight + right_weight + 1)
            result = recipe["result"]
            if candidate < weights.get(result, inf):
                weights[result] = candidate
                heappush(heap, (candidate, result))

    return {
        element: None if value == inf else int(value)
        for element, value in weights.items()
    }


def build_edge_data(
    recipes: list[dict[str, str]],
    recipe_limit: int | None = None,
) -> list[dict[str, object]]:
    edge_map: dict[tuple[str, str], set[str]] = {}
    selected_recipes = recipes if recipe_limit is None else recipes[:recipe_limit]

    for recipe in selected_recipes:
        left = recipe["left"]
        right = recipe["right"]
        result = recipe["result"]

        left_key = (left, result)
        left_companions = edge_map.setdefault(left_key, set())
        left_companions.add(right)

        right_key = (right, result)
        right_companions = edge_map.setdefault(right_key, set())
        right_companions.add(left)

    return [
        {
            "source": source,
            "target": target,
            "elements": sorted(companions),
            "weight": len(companions),
        }
        for (source, target), companions in sorted(edge_map.items())
    ]


def build_graph_data(
    elements: list[str],
    recipes: list[dict[str, str]],
    recipe_limit: int | None = None,
) -> dict[str, object]:
    node_weights = compute_node_weights(elements, recipes)
    nodes = [
        {
            "id": element,
            "label": element,
            "weight": node_weights[element],
            "is_starter": element in STARTER_ELEMENTS,
        }
        for element in sorted(elements)
    ]
    edges = build_edge_data(recipes, recipe_limit=recipe_limit)

    return {
        "nodes": nodes,
        "edges": edges,
        "node_weights": node_weights,
    }


def build_weight_statistics(
    elements: list[str],
    recipes: list[dict[str, str]],
    node_weights: dict[str, int | None],
    discarded_pairs: set[tuple[str, str]] | None = None,
) -> dict[str, list[tuple[int, int]]]:
    discarded_pairs = discarded_pairs or set()
    node_counts: dict[int, int] = defaultdict(int)
    for element in elements:
        weight = node_weights.get(element)
        if weight is not None:
            node_counts[weight] += 1

    recipe_counts: dict[int, int] = defaultdict(int)
    for recipe in recipes:
        result_weight = node_weights.get(recipe["result"])
        if result_weight is not None:
            recipe_counts[result_weight] += 1

    known_pairs = known_recipe_pairs(recipes)
    known_pair_counts: dict[int, int] = defaultdict(int)
    for left, right in known_pairs:
        left_weight = node_weights.get(left)
        right_weight = node_weights.get(right)
        if left_weight is None or right_weight is None:
            continue
        known_pair_counts[left_weight + right_weight + 1] += 1

    all_pair_counts: dict[int, int] = defaultdict(int)
    sorted_node_counts = sorted(node_counts.items())
    for index, (left_weight, left_count) in enumerate(sorted_node_counts):
        for right_weight, right_count in sorted_node_counts[index:]:
            if left_weight == right_weight:
                pair_count = left_count * (left_count + 1) // 2
            else:
                pair_count = left_count * right_count
            all_pair_counts[left_weight + right_weight + 1] += pair_count

    missing_pair_counts = {
        weight: all_pair_counts[weight] - known_pair_counts.get(weight, 0)
        for weight in all_pair_counts
        if all_pair_counts[weight] - known_pair_counts.get(weight, 0) > 0
    }

    for left, right in discarded_pairs:
        left_weight = node_weights.get(left)
        right_weight = node_weights.get(right)
        if left_weight is None or right_weight is None:
            continue
        target_weight = left_weight + right_weight + 1
        current = missing_pair_counts.get(target_weight, 0)
        if current <= 1:
            missing_pair_counts.pop(target_weight, None)
        else:
            missing_pair_counts[target_weight] = current - 1

    return {
        "node_counts_by_weight": sorted(node_counts.items()),
        "recipe_counts_by_result_weight": sorted(recipe_counts.items()),
        "missing_counts_by_result_weight": sorted(missing_pair_counts.items()),
    }
