from __future__ import annotations

from pathlib import Path

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
