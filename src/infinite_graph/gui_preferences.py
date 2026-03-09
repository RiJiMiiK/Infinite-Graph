"""Persistence helpers for local GUI preferences."""

from __future__ import annotations

import json
from contextlib import suppress
from pathlib import Path


def ui_preferences_path() -> Path:
    root_dir = Path(__file__).resolve().parents[2]
    return root_dir / ".cache" / "infinite_graph" / "ui_preferences.json"


def load_ui_preferences() -> dict[str, object]:
    path = ui_preferences_path()
    if not path.is_file():
        return {}

    with suppress(OSError, ValueError, TypeError):
        raw_value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw_value, dict):
            return raw_value
    return {}


def save_ui_preferences(preferences: dict[str, object]) -> None:
    path = ui_preferences_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(preferences, indent=2, sort_keys=True),
        encoding="utf-8",
    )
