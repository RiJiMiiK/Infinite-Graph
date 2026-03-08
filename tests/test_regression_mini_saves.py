from __future__ import annotations

from pathlib import Path

from src.infinite_graph import service


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_mini_infinite_craft_save_regression(monkeypatch) -> None:
    monkeypatch.setattr(service, "load_discarded_pairs", lambda path: {("Earth", "Fire")})

    result = service.process_save(FIXTURES_DIR / "mini_infinite_craft_save.json")

    assert result["elements"] == [
        "Dust",
        "Earth",
        "Fire",
        "Life",
        "Mud",
        "Steam",
        "Water",
        "Wind",
    ]
    assert result["recipes"] == [
        {"left": "Water", "right": "Fire", "result": "Steam"},
        {"left": "Water", "right": "Earth", "result": "Mud"},
        {"left": "Wind", "right": "Earth", "result": "Dust"},
        {"left": "Mud", "right": "Fire", "result": "Life"},
        {"left": "Mud", "right": "Wind", "result": "Life"},
    ]
    assert result["node_weights"] == {
        "Dust": 1,
        "Earth": 0,
        "Fire": 0,
        "Life": 2,
        "Mud": 1,
        "Steam": 1,
        "Water": 0,
        "Wind": 0,
    }
    assert result["known_pairs"] == {
        ("Fire", "Mud"),
        ("Fire", "Water"),
        ("Earth", "Water"),
        ("Earth", "Wind"),
        ("Mud", "Wind"),
    }
    assert result["discarded_pairs"] == {("Earth", "Fire")}
    assert result["statistics"] == {
        "node_counts_by_weight": [(0, 4), (1, 3), (2, 1)],
        "recipe_counts_by_result_weight": [(1, 3), (2, 2)],
        "missing_counts_by_result_weight": [(1, 6), (2, 10), (3, 10), (4, 3), (5, 1)],
    }
    assert any(
        edge == {"source": "Mud", "target": "Life", "elements": ["Fire", "Wind"], "weight": 2}
        for edge in result["graph_edges"]
    )
    assert result["missing"][:6] == [
        ("Dust", "Dust"),
        ("Dust", "Earth"),
        ("Dust", "Fire"),
        ("Dust", "Life"),
        ("Dust", "Mud"),
        ("Dust", "Steam"),
    ]


def test_mini_simple_save_regression(monkeypatch) -> None:
    monkeypatch.setattr(service, "load_discarded_pairs", lambda path: set())

    result = service.process_save(
        FIXTURES_DIR / "mini_simple_save.json",
        focus_element="Mist",
    )

    assert result["elements"] == ["Ash", "Earth", "Fire", "Mist", "Smoke", "Water", "Wind"]
    assert result["recipes"] == [
        {"left": "Water", "right": "Wind", "result": "Mist"},
        {"left": "Mist", "right": "Fire", "result": "Smoke"},
        {"left": "Smoke", "right": "Earth", "result": "Ash"},
    ]
    assert result["node_weights"] == {
        "Ash": 3,
        "Earth": 0,
        "Fire": 0,
        "Mist": 1,
        "Smoke": 2,
        "Water": 0,
        "Wind": 0,
    }
    assert result["statistics"] == {
        "node_counts_by_weight": [(0, 4), (1, 1), (2, 1), (3, 1)],
        "recipe_counts_by_result_weight": [(1, 1), (2, 1), (3, 1)],
        "missing_counts_by_result_weight": [(1, 9), (2, 3), (3, 4), (4, 5), (5, 2), (6, 1), (7, 1)],
    }
    assert result["focus_element"] == "Mist"
    assert result["missing"] == [
        ("Ash", "Mist"),
        ("Earth", "Mist"),
        ("Mist", "Mist"),
        ("Mist", "Smoke"),
        ("Mist", "Water"),
        ("Mist", "Wind"),
    ]
