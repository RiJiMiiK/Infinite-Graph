from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.infinite_graph import save_loader


def test_extract_helpers() -> None:
    assert save_loader._extract_element_name(" Water ") == "Water"
    assert save_loader._extract_element_name({"text": "Fire"}) == "Fire"
    assert save_loader._extract_element_name({"bad": "x"}) is None
    assert save_loader._extract_recipe({"left": "A", "right": "B", "result": "C"}) == {
        "left": "A",
        "right": "B",
        "result": "C",
    }
    assert save_loader._extract_recipe({"left": "A"}) is None


def test_load_simple_save_reports_ignored_entries(tmp_path: Path) -> None:
    path = tmp_path / "save.json"
    path.write_text(
        json.dumps(
            {
                "elements": ["Water", {"name": "Fire"}, {"bad": "x"}],
                "recipes": [
                    {"left": "Water", "right": "Fire", "result": "Steam"},
                    {"left": "Water"},
                    "bad",
                ],
            }
        ),
        encoding="utf-8",
    )
    result = save_loader.load_save(path)
    assert result["elements"] == ["Fire", "Steam", "Water"]
    assert result["ignored_element_entries"] == 1
    assert result["ignored_recipe_entries"] == 2
    assert result["warnings"]


def test_load_infinite_craft_save_reports_invalid_entries(tmp_path: Path) -> None:
    path = tmp_path / "save.json"
    path.write_text(
        json.dumps(
            {
                "items": [
                    {"id": 0, "text": "Water", "recipes": []},
                    {"id": 1, "text": "Fire", "recipes": []},
                    {"id": 2, "text": "Steam", "recipes": [[0, 1], [0], [0, 9]]},
                    {"id": 3, "recipes": []},
                    {"id": "bad", "text": "Ghost"},
                    "bad",
                ]
            }
        ),
        encoding="utf-8",
    )
    result = save_loader.load_save(path)
    assert result["elements"] == ["Fire", "Steam", "Water"]
    assert result["ignored_item_entries"] == 3
    assert result["ignored_recipe_entries"] == 3
    assert result["recipes"] == [{"left": "Water", "right": "Fire", "result": "Steam"}]


def test_load_save_invalid_json_and_format(tmp_path: Path) -> None:
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON save file"):
        save_loader.load_save(bad_json)

    unknown = tmp_path / "unknown.json"
    unknown.write_text(json.dumps(["bad"]), encoding="utf-8")
    with pytest.raises(ValueError, match="Format de sauvegarde non reconnu"):
        save_loader.load_save(unknown)
