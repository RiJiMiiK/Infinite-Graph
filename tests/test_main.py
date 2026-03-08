from __future__ import annotations

import runpy


def test_main_entrypoint_runs_gui(monkeypatch) -> None:
    called = {"value": False}

    def fake_main() -> None:
        called["value"] = True

    monkeypatch.setattr("src.infinite_graph.gui.main", fake_main)
    runpy.run_module("main", run_name="__main__")
    assert called["value"] is True
