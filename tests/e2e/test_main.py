from __future__ import annotations

import runpy

from src.infinite_graph import gui


def test_main_entrypoint_runs_gui(monkeypatch) -> None:
    called = {"value": False}

    def fake_main() -> None:
        called["value"] = True

    monkeypatch.setattr("src.infinite_graph.gui.main", fake_main)
    runpy.run_module("main", run_name="__main__")
    assert called["value"] is True


def test_gui_main(monkeypatch, qapp) -> None:
    created = {}

    class FakeWindow:
        def __init__(self) -> None:
            created["window"] = self
            self.shown = False

        def show(self) -> None:
            self.shown = True

    monkeypatch.setattr(gui, "InfiniteGraphWindow", FakeWindow)
    monkeypatch.setattr(gui.QApplication, "instance", staticmethod(lambda: qapp))
    monkeypatch.setattr(qapp, "exec", lambda: 0)
    gui.main()
    assert created["window"].shown is True
