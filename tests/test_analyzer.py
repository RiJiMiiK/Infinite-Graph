from __future__ import annotations

from src.infinite_graph import analyzer


def test_normalize_and_known_pairs() -> None:
    assert analyzer.normalize_pair("B", "A") == ("A", "B")
    recipes = [{"left": "Water", "right": "Fire", "result": "Steam"}]
    assert analyzer.known_recipe_pairs(recipes) == {("Fire", "Water")}


def test_candidate_result_weight_handles_missing_weight() -> None:
    weights = {"Water": 0, "Fire": None}
    assert analyzer.candidate_result_weight("Water", "Fire", weights) is None
    assert analyzer.candidate_result_weight("Water", "Water", {"Water": 0}) == 1


def test_find_missing_combinations_focus_and_done_and_discarded() -> None:
    elements = ["Water", "Fire", "Steam"]
    recipes = [{"left": "Water", "right": "Fire", "result": "Steam"}]
    result = analyzer.find_missing_combinations(
        elements,
        recipes,
        focus_element="Water",
        discarded_pairs={("Steam", "Water")},
        done_pairs={("Water", "Water")},
    )
    assert result == []
    assert analyzer.find_missing_combinations(elements, recipes, focus_element="Unknown") == []
    assert analyzer.find_missing_combinations(
        ["A", "B", "C"],
        [],
        focus_element="A",
        limit=1,
    ) == [("A", "A")]


def test_find_missing_combinations_limit() -> None:
    elements = ["A", "B", "C"]
    recipes: list[dict[str, str]] = []
    result = analyzer.find_missing_combinations(elements, recipes, limit=2)
    assert len(result) == 2


def test_find_cheapest_combination_and_none() -> None:
    elements = ["Water", "Fire", "Wind", "Earth", "Rose"]
    recipes = [
        {"left": "Water", "right": "Fire", "result": "Steam"},
        {"left": "Fire", "right": "Earth", "result": "Lava"},
    ]
    weights = {"Water": 0, "Fire": 0, "Wind": 0, "Earth": 0, "Rose": 1}
    pair = analyzer.find_cheapest_combination(
        elements,
        recipes,
        weights,
        discarded_pairs={("Fire", "Water")},
        done_pairs={("Earth", "Fire")},
    )
    assert pair in {
        ("Earth", "Earth"),
        ("Earth", "Water"),
        ("Fire", "Wind"),
        ("Earth", "Wind"),
        ("Fire", "Rose"),
    }
    assert analyzer.find_cheapest_combination(
        ["A"],
        [],
        {"A": None},
    ) is None
    assert analyzer.find_cheapest_combination(
        ["A", "B"],
        [],
        {"A": 0, "B": 2},
    ) == ("A", "A")

    original = analyzer.candidate_result_weight
    try:
        analyzer.candidate_result_weight = lambda *args, **kwargs: 999
        assert analyzer.find_cheapest_combination(
            ["A", "B"],
            [],
            {"A": 0, "B": 0},
        ) is None
    finally:
        analyzer.candidate_result_weight = original


def test_find_random_combination_direct_and_fallback(monkeypatch) -> None:
    elements = ["A", "B"]
    recipes: list[dict[str, str]] = []
    choices = iter(["A", "B"])
    monkeypatch.setattr(analyzer.random, "choice", lambda seq: next(choices))
    assert analyzer.find_random_combination(elements, recipes, attempts=1) == ("A", "B")

    monkeypatch.setattr(analyzer.random, "choice", lambda seq: "A")
    assert analyzer.find_random_combination(
        elements,
        recipes,
        discarded_pairs={("A", "A")},
        done_pairs={("A", "B")},
        attempts=2,
    ) == ("B", "B")
    assert analyzer.find_random_combination([], recipes) is None
