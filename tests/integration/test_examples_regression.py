from __future__ import annotations

from pathlib import Path

from src.infinite_graph import save_loader, service


FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
STARTERS = {"Water", "Fire", "Wind", "Earth"}
GRAPH_FIXTURE_PATH = FIXTURES_DIR / "Graph Example"


def test_graph_example_loads_without_json_extension() -> None:
    result = save_loader.load_save(GRAPH_FIXTURE_PATH)

    assert STARTERS.issubset(result["elements"])
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
    assert result["ignored_element_entries"] == 0
    assert result["ignored_item_entries"] == 0
    assert result["ignored_recipe_entries"] == 0
    assert result["warnings"] == []

    for recipe in result["recipes"]:
        assert recipe.keys() == {"left", "right", "result"}
        assert recipe["left"] in result["elements"]
        assert recipe["right"] in result["elements"]
        assert recipe["result"] in result["elements"]


def test_graph_example_processes_end_to_end(monkeypatch) -> None:
    monkeypatch.setattr(service, "load_discarded_pairs", lambda path: set())

    result = service.process_save(GRAPH_FIXTURE_PATH)

    assert len(result["graph_nodes"]) == 8
    assert len(result["graph_edges"]) == 9
    assert result["known_pairs"] == {
        ("Fire", "Mud"),
        ("Fire", "Water"),
        ("Earth", "Water"),
        ("Earth", "Wind"),
        ("Mud", "Wind"),
    }
    assert result["discarded_pairs"] == set()
    assert result["done_pairs"] == set()
    assert result["load_warnings"] == []
    assert result["node_weights"]["Water"] == 0
    assert result["node_weights"]["Fire"] == 0
    assert result["node_weights"]["Wind"] == 0
    assert result["node_weights"]["Earth"] == 0
    assert result["node_weights"]["Steam"] == 1
    assert result["node_weights"]["Mud"] == 1
    assert result["node_weights"]["Dust"] == 1
    assert result["node_weights"]["Life"] == 2
    assert result["statistics"] == {
        "node_counts_by_weight": [(0, 4), (1, 3), (2, 1)],
        "recipe_counts_by_result_weight": [(1, 3), (2, 2)],
        "missing_counts_by_result_weight": [(1, 7), (2, 10), (3, 10), (4, 3), (5, 1)],
    }
