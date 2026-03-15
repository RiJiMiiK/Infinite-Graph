from __future__ import annotations

from pathlib import Path

import networkx as nx

from src.infinite_graph import service


def test_process_save_reports_progress_and_returns_expected_data(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        service,
        "load_save",
        lambda path: {
            "elements": ["Water", "Fire", "Wind", "Earth", "Steam"],
            "recipes": [{"left": "Water", "right": "Fire", "result": "Steam"}],
            "warnings": ["warning"],
            "ignored_element_entries": 1,
            "ignored_item_entries": 2,
            "ignored_recipe_entries": 3,
        },
    )
    monkeypatch.setattr(service, "load_discarded_pairs", lambda path: {("Earth", "Wind")})
    steps: list[str] = []
    result = service.process_save(tmp_path / "save.json", progress_callback=steps.append)
    assert steps == [
        "Loading save file",
        "Loading discarded combinations",
        "Building graph model",
        "Computing graph statistics",
        "Computing missing combinations",
    ]
    assert result["load_warnings"] == ["warning"]
    assert result["ignored_recipe_entries"] == 3
    assert result["discarded_pairs"] == {("Earth", "Wind")}
    assert result["done_pairs"] == set()
    assert result["render_scope"] == "complete_graph"
    assert result["render_graph_nodes"] == result["graph_nodes"]
    assert result["render_graph_edges"] == result["graph_edges"]
    assert isinstance(result["community_graph"], nx.DiGraph)
    assert sorted(result["community_graph"].nodes) == ["Earth", "Fire", "Steam", "Water", "Wind"]
    assert result["community_graph"]["Water"]["Steam"]["weight"] == 1.0
    assert ("Earth", "Earth") in result["candidate_pairs"]
    assert result["candidate_pairs_by_weight"][0] == ("Earth", "Earth")
