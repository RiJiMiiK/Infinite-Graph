from __future__ import annotations

from pathlib import Path

import json
import pytest

from src.infinite_graph import gui


def test_window_remove_selected_discarded_combination(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    infos = []
    removed = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(gui, "remove_discarded_pair", lambda path, pair: removed.append((path, pair)))

    window._remove_selected_discarded_combination()
    window._restore_discarded_pair(("Earth", "Wind"))
    window._current_result = sample_result
    window._current_save_path = Path("save.json")
    window._refresh_discarded_table()

    window._remove_selected_discarded_combination()
    assert "Select a discarded combination first" in infos[-1][-1]

    sample_result["discarded_pairs"].clear()
    window.discarded_model.update_rows([["Earth", "Wind"]])
    window.discarded_table.selectRow(0)
    window._remove_selected_discarded_combination()
    assert "is not discarded" in infos[-1][-1]

    sample_result["discarded_pairs"].add(("Earth", "Wind"))
    window._refresh_discarded_table()
    window.discarded_table.selectRow(0)
    window._remove_selected_discarded_combination()
    assert removed == [(Path("save.json"), ("Earth", "Wind"))]
    assert ("Earth", "Wind") not in sample_result["discarded_pairs"]
    assert ("Earth", "Wind") in sample_result["missing"]
    assert window.discarded_model.rowCount() == 0
    window.close()


def test_window_reset_discarded_combinations(monkeypatch, qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    infos = []
    cleared = []
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(
        gui.QMessageBox,
        "question",
        lambda *args: gui.QMessageBox.StandardButton.No,
    )
    monkeypatch.setattr(gui, "clear_discarded_pairs", lambda path: cleared.append(path))

    window._reset_discarded_combinations()
    window._current_result = sample_result
    window._current_save_path = Path("save.json")
    window._refresh_discarded_table()
    sample_result["statistics"]["missing_counts_by_result_weight"] = []

    window._reset_discarded_combinations()
    assert cleared == []
    assert ("Earth", "Wind") in sample_result["discarded_pairs"]

    monkeypatch.setattr(
        gui.QMessageBox,
        "question",
        lambda *args: gui.QMessageBox.StandardButton.Yes,
    )
    window._reset_discarded_combinations()
    assert cleared == [Path("save.json")]
    assert sample_result["discarded_pairs"] == set()
    assert ("Earth", "Wind") in sample_result["missing"]
    assert window.discarded_model.rowCount() == 0

    window._reset_discarded_combinations()
    assert "There is no discarded combination" in infos[-1][-1]
    window.close()


def test_window_export_and_import_discarded_combinations(monkeypatch, qapp, sample_result, tmp_path: Path) -> None:
    window = gui.InfiniteGraphWindow()
    infos = []
    warns = []
    export_path = tmp_path / "discarded_export.json"
    import_path = tmp_path / "discarded_import.json"
    monkeypatch.setattr(gui.QMessageBox, "information", lambda *args: infos.append(args))
    monkeypatch.setattr(gui.QMessageBox, "warning", lambda *args: warns.append(args))
    monkeypatch.setattr(
        gui.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(export_path), "JSON (*.json)"),
    )
    monkeypatch.setattr(
        gui.QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(import_path), "JSON (*.json)"),
    )

    window._export_discarded_combinations()
    window._import_discarded_combinations()
    window._current_result = sample_result
    window._current_save_path = Path("save.json")
    window._refresh_discarded_table()
    sample_result["missing"] = [("Earth", "Wind"), ("Earth", "Earth")]
    sample_result["statistics"]["missing_counts_by_result_weight"] = [(1, 2)]

    monkeypatch.setattr(gui, "export_discarded_pairs", lambda path: path.write_text(
        json.dumps({"discarded": [["Earth", "Wind"]]}), encoding="utf-8"
    ))
    window._export_discarded_combinations()
    assert export_path.exists()
    assert "Discarded export completed" in infos[-1][-1]

    import_path.write_text(
        json.dumps({"discarded": [["Earth", "Wind"], ["Earth", "Earth"]]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(gui, "import_discarded_pairs", lambda path: {("Earth", "Earth"), ("Earth", "Wind")})
    window._import_discarded_combinations()
    assert ("Earth", "Earth") in sample_result["discarded_pairs"]
    assert ("Earth", "Earth") not in sample_result["missing"]
    assert sample_result["statistics"]["missing_counts_by_result_weight"] == [(1, 1)]
    assert "1 discarded combination(s) imported." in infos[-1][-1]

    monkeypatch.setattr(
        gui.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: ("", "JSON (*.json)"),
    )
    window._export_discarded_combinations()
    monkeypatch.setattr(
        gui.QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: ("", "JSON (*.json)"),
    )
    window._import_discarded_combinations()

    monkeypatch.setattr(gui, "import_discarded_pairs", lambda path: (_ for _ in ()).throw(ValueError("bad import")))
    monkeypatch.setattr(
        gui.QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(import_path), "JSON (*.json)"),
    )
    window._import_discarded_combinations()
    assert "bad import" in warns[-1][-1]
    window.close()
