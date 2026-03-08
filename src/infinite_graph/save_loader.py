from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _extract_element_name(raw_element: Any) -> str | None:
    if isinstance(raw_element, str):
        return raw_element.strip() or None
    if isinstance(raw_element, dict):
        for key in ("name", "text", "result"):
            value = raw_element.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _extract_recipe(raw_recipe: dict[str, Any]) -> dict[str, str] | None:
    left = raw_recipe.get("left") or raw_recipe.get("first") or raw_recipe.get("a")
    right = raw_recipe.get("right") or raw_recipe.get("second") or raw_recipe.get("b")
    result = raw_recipe.get("result") or raw_recipe.get("output") or raw_recipe.get("res")

    if not all(isinstance(value, str) and value.strip() for value in (left, right, result)):
        return None

    return {
        "left": left.strip(),
        "right": right.strip(),
        "result": result.strip(),
    }


def _load_simple_save(data: dict[str, Any]) -> dict[str, list]:
    raw_elements = data.get("elements", [])
    raw_recipes = data.get("recipes", [])

    elements = []
    for raw_element in raw_elements:
        name = _extract_element_name(raw_element)
        if name:
            elements.append(name)

    recipes = []
    for raw_recipe in raw_recipes:
        if isinstance(raw_recipe, dict):
            recipe = _extract_recipe(raw_recipe)
            if recipe:
                recipes.append(recipe)

    for recipe in recipes:
        for key in ("left", "right", "result"):
            if recipe[key] not in elements:
                elements.append(recipe[key])

    return {"elements": sorted(set(elements)), "recipes": recipes}


def _load_infinite_craft_save(data: dict[str, Any]) -> dict[str, list]:
    items = data.get("items", [])
    id_to_name: dict[int, str] = {}

    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        text = item.get("text")
        if isinstance(item_id, int) and isinstance(text, str) and text.strip():
            id_to_name[item_id] = text.strip()

    recipes: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        result_name = item.get("text")
        raw_recipes = item.get("recipes", [])
        if (
            not isinstance(result_name, str)
            or not result_name.strip()
            or not isinstance(raw_recipes, list)
        ):
            continue

        for raw_recipe in raw_recipes:
            if (
                not isinstance(raw_recipe, list)
                or len(raw_recipe) != 2
                or not all(isinstance(value, int) for value in raw_recipe)
            ):
                continue

            left_name = id_to_name.get(raw_recipe[0])
            right_name = id_to_name.get(raw_recipe[1])
            if not left_name or not right_name:
                continue

            recipes.append(
                {
                    "left": left_name,
                    "right": right_name,
                    "result": result_name.strip(),
                }
            )

    return {"elements": sorted(set(id_to_name.values())), "recipes": recipes}


def load_save(path: Path) -> dict[str, list]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return _load_infinite_craft_save(data)
    if isinstance(data, dict):
        return _load_simple_save(data)
    raise ValueError("Format de sauvegarde non reconnu.")
