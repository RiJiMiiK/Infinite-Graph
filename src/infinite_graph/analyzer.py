from __future__ import annotations

import random
from collections import defaultdict
from typing import Iterable


def normalize_pair(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((left, right)))


def known_recipe_pairs(recipes: Iterable[dict[str, str]]) -> set[tuple[str, str]]:
    return {normalize_pair(recipe["left"], recipe["right"]) for recipe in recipes}


def candidate_result_weight(
    left: str,
    right: str,
    node_weights: dict[str, int | None],
) -> int | None:
    left_weight = node_weights.get(left)
    right_weight = node_weights.get(right)
    if left_weight is None or right_weight is None:
        return None
    return left_weight + right_weight + 1


def _candidate_allowed(
    pair: tuple[str, str],
    known_pairs: set[tuple[str, str]],
    discarded_pairs: set[tuple[str, str]],
    done_pairs: set[tuple[str, str]] | None = None,
) -> bool:
    done_pairs = done_pairs or set()
    return pair not in known_pairs and pair not in discarded_pairs and pair not in done_pairs


def find_missing_combinations(
    elements: list[str],
    recipes: list[dict[str, str]],
    limit: int = 1000,
    focus_element: str | None = None,
    discarded_pairs: set[tuple[str, str]] | None = None,
    done_pairs: set[tuple[str, str]] | None = None,
) -> list[tuple[str, str]]:
    known_pairs = known_recipe_pairs(recipes)
    discarded_pairs = discarded_pairs or set()
    done_pairs = done_pairs or set()
    sorted_elements = sorted(set(elements))
    missing: list[tuple[str, str]] = []

    if focus_element:
        if focus_element not in sorted_elements:
            return []
        for element in sorted_elements:
            pair = normalize_pair(focus_element, element)
            if _candidate_allowed(pair, known_pairs, discarded_pairs, done_pairs):
                missing.append(pair)
                if len(missing) >= limit:
                    break
        return missing

    for index, left in enumerate(sorted_elements):
        for right in sorted_elements[index:]:
            pair = (left, right)
            if _candidate_allowed(pair, known_pairs, discarded_pairs, done_pairs):
                missing.append(pair)
                if len(missing) >= limit:
                    return missing
    return missing


def find_cheapest_combination(
    elements: list[str],
    recipes: list[dict[str, str]],
    node_weights: dict[str, int | None],
    discarded_pairs: set[tuple[str, str]] | None = None,
    done_pairs: set[tuple[str, str]] | None = None,
) -> tuple[str, str] | None:
    known_pairs = known_recipe_pairs(recipes)
    discarded_pairs = discarded_pairs or set()
    done_pairs = done_pairs or set()

    elements_by_weight: dict[int, list[str]] = defaultdict(list)
    for element in sorted(set(elements)):
        weight = node_weights.get(element)
        if weight is not None:
            elements_by_weight[weight].append(element)

    weights = sorted(elements_by_weight)
    for left_weight_index, left_weight in enumerate(weights):
        for right_weight in weights[left_weight_index:]:
            target_weight = left_weight + right_weight + 1
            pairs: list[tuple[str, str]] = []
            for left in elements_by_weight[left_weight]:
                for right in elements_by_weight[right_weight]:
                    pair = normalize_pair(left, right)
                    if pair[0] != left and left_weight == right_weight:
                        continue
                    if candidate_result_weight(pair[0], pair[1], node_weights) != target_weight:
                        continue
                    if _candidate_allowed(pair, known_pairs, discarded_pairs, done_pairs):
                        pairs.append(pair)
            if pairs:
                return min(set(pairs))
    return None


def find_random_combination(
    elements: list[str],
    recipes: list[dict[str, str]],
    discarded_pairs: set[tuple[str, str]] | None = None,
    done_pairs: set[tuple[str, str]] | None = None,
    attempts: int = 5000,
) -> tuple[str, str] | None:
    known_pairs = known_recipe_pairs(recipes)
    discarded_pairs = discarded_pairs or set()
    done_pairs = done_pairs or set()
    sorted_elements = sorted(set(elements))
    if not sorted_elements:
        return None

    for _ in range(attempts):
        left = random.choice(sorted_elements)
        right = random.choice(sorted_elements)
        pair = normalize_pair(left, right)
        if _candidate_allowed(pair, known_pairs, discarded_pairs, done_pairs):
            return pair

    missing = find_missing_combinations(
        sorted_elements,
        recipes,
        limit=1,
        discarded_pairs=discarded_pairs,
        done_pairs=done_pairs,
    )
    return missing[0] if missing else None


def build_candidate_index(
    elements: list[str],
    recipes: list[dict[str, str]],
    node_weights: dict[str, int | None],
    focus_element: str | None = None,
    discarded_pairs: set[tuple[str, str]] | None = None,
    done_pairs: set[tuple[str, str]] | None = None,
) -> dict[str, object]:
    known_pairs = known_recipe_pairs(recipes)
    discarded_pairs = discarded_pairs or set()
    done_pairs = done_pairs or set()
    sorted_elements = sorted(set(elements))
    candidates: list[tuple[str, str]] = []

    if focus_element:
        if focus_element in sorted_elements:
            for element in sorted_elements:
                pair = normalize_pair(focus_element, element)
                if _candidate_allowed(pair, known_pairs, discarded_pairs, done_pairs):
                    candidates.append(pair)
    else:
        for index, left in enumerate(sorted_elements):
            for right in sorted_elements[index:]:
                pair = (left, right)
                if _candidate_allowed(pair, known_pairs, discarded_pairs, done_pairs):
                    candidates.append(pair)

    cheapest_pairs = sorted(
        candidates,
        key=lambda pair: (
            candidate_result_weight(pair[0], pair[1], node_weights) is None,
            candidate_result_weight(pair[0], pair[1], node_weights)
            if candidate_result_weight(pair[0], pair[1], node_weights) is not None
            else 10**9,
            pair,
        ),
    )
    return {
        "all_pairs": candidates,
        "cheapest_pairs": cheapest_pairs,
        "known_pairs": known_pairs,
    }
