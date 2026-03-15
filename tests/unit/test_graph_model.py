from __future__ import annotations

import pytest

from src.infinite_graph import graph_model


def test_validate_starter_elements_raises() -> None:
    with pytest.raises(ValueError, match="starter element manquant"):
        graph_model.validate_starter_elements(["Water", "Fire"])


def test_compute_node_weights_and_unreachable() -> None:
    elements = ["Water", "Fire", "Wind", "Earth", "Steam", "Mud", "Ghost"]
    recipes = [
        {"left": "Water", "right": "Fire", "result": "Steam"},
        {"left": "Water", "right": "Earth", "result": "Mud"},
        {"left": "Steam", "right": "Earth", "result": "Mud"},
    ]
    weights = graph_model.compute_node_weights(elements, recipes)
    assert weights["Steam"] == 1
    assert weights["Mud"] == 1
    assert weights["Ghost"] is None

    stale_weights = graph_model.compute_node_weights(
        ["Water", "Fire", "Wind", "Earth", "Ash", "Steam", "Boil"],
        [
            {"left": "Water", "right": "Fire", "result": "Ash"},
            {"left": "Wind", "right": "Earth", "result": "Steam"},
            {"left": "Ash", "right": "Ash", "result": "Boil"},
            {"left": "Steam", "right": "Fire", "result": "Boil"},
        ],
    )
    assert stale_weights["Boil"] == 2


def test_compute_node_weights_ignores_stale_heap_entries(monkeypatch) -> None:
    original_heappop = graph_model.heappop
    stale_returned = False

    def fake_heappop(heap):
        nonlocal stale_returned
        if not stale_returned:
            stale_returned = True
            return (99, "Water")
        return original_heappop(heap)

    monkeypatch.setattr(graph_model, "heappop", fake_heappop)
    weights = graph_model.compute_node_weights(
        ["Water", "Fire", "Wind", "Earth", "Steam"],
        [{"left": "Water", "right": "Fire", "result": "Steam"}],
    )
    assert weights["Steam"] == 1


def test_build_edge_data_and_graph_data() -> None:
    recipes = [
        {"left": "A", "right": "B", "result": "C"},
        {"left": "A", "right": "D", "result": "C"},
    ]
    edges = graph_model.build_edge_data(recipes, recipe_limit=1)
    assert edges == [
        {"source": "A", "target": "C", "elements": ["B"], "weight": 1},
        {"source": "B", "target": "C", "elements": ["A"], "weight": 1},
    ]

    data = graph_model.build_graph_data(
        ["Water", "Fire", "Wind", "Earth", "Steam"],
        [{"left": "Water", "right": "Fire", "result": "Steam"}],
    )
    assert len(data["nodes"]) == 5
    assert len(data["edges"]) == 2


def test_build_weight_statistics_with_discarded() -> None:
    elements = ["Water", "Fire", "Wind", "Earth", "Steam"]
    recipes = [{"left": "Water", "right": "Fire", "result": "Steam"}]
    node_weights = {"Water": 0, "Fire": 0, "Wind": 0, "Earth": 0, "Steam": 1}
    stats = graph_model.build_weight_statistics(
        elements,
        recipes,
        node_weights,
        discarded_pairs={("Earth", "Wind")},
    )
    assert stats["node_counts_by_weight"] == [(0, 4), (1, 1)]
    assert stats["recipe_counts_by_result_weight"] == [(1, 1)]
    assert stats["missing_counts_by_result_weight"] == [(1, 8), (2, 4), (3, 1)]

    stats = graph_model.build_weight_statistics(
        elements,
        recipes,
        {"Water": 0, "Fire": 0, "Wind": None, "Earth": 0, "Steam": 1},
        discarded_pairs={("Earth", "Fire"), ("Wind", "Earth"), ("Steam", "Steam")},
    )
    assert stats["missing_counts_by_result_weight"] == [(1, 4), (2, 3)]

    stats = graph_model.build_weight_statistics(
        ["Water", "Fire", "Wind", "Earth", "Steam", "Cloud"],
        [
            {"left": "Water", "right": "Fire", "result": "Steam"},
            {"left": "Wind", "right": "Earth", "result": "Cloud"},
        ],
        {"Water": 0, "Fire": 0, "Wind": None, "Earth": 0, "Steam": 1, "Cloud": None},
    )
    assert stats["recipe_counts_by_result_weight"] == [(1, 1)]
