from __future__ import annotations

from pathlib import Path

from src.infinite_graph import gui


def test_ui_preferences_helpers(tmp_path: Path, monkeypatch) -> None:
    prefs_path = tmp_path / "ui_preferences.json"
    monkeypatch.setattr(gui, "ui_preferences_path", lambda: prefs_path)

    assert gui.load_ui_preferences() == {}

    gui.save_ui_preferences({"window_width": 1234, "summary_panel_visible": True})
    assert gui.load_ui_preferences() == {
        "summary_panel_visible": True,
        "window_width": 1234,
    }

    prefs_path.write_text("{", encoding="utf-8")
    assert gui.load_ui_preferences() == {}
