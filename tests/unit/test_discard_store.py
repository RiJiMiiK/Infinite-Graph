from __future__ import annotations

import json
from pathlib import Path

from src.infinite_graph import discard_store


def test_discard_path_targets_repo_root_file() -> None:
    path = discard_store._discard_path()
    assert path.name == "discarded.json"
    assert path.parent.name == "Infinite_Graph"


def test_load_discarded_pairs_from_missing_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(discard_store, "_discard_path", lambda: tmp_path / "discarded.json")
    assert discard_store._discard_path() == tmp_path / "discarded.json"
    assert discard_store.load_discarded_pairs() == set()


def test_load_discarded_pairs_new_and_old_formats(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "discarded.json"
    monkeypatch.setattr(discard_store, "_discard_path", lambda: path)

    path.write_text(json.dumps({"discarded": [["B", "A"], ["A"]]}), encoding="utf-8")
    assert discard_store.load_discarded_pairs() == {("A", "B")}

    path.write_text(json.dumps({"save1": [["C", "A"]], "save2": [["D", "B"]]}), encoding="utf-8")
    assert discard_store.load_discarded_pairs() == {("A", "C"), ("B", "D")}


def test_add_discarded_pair_rewrites_global_format(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "discarded.json"
    monkeypatch.setattr(discard_store, "_discard_path", lambda: path)
    discard_store.add_discarded_pair(None, ("Water", "Fire"))
    discard_store.add_discarded_pair(None, ("Fire", "Water"))
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == {"discarded": [["Fire", "Water"]]}


def test_remove_discarded_pair_rewrites_global_format(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "discarded.json"
    monkeypatch.setattr(discard_store, "_discard_path", lambda: path)
    discard_store.add_discarded_pair(None, ("Water", "Fire"))
    discard_store.add_discarded_pair(None, ("Water", "Earth"))
    discard_store.remove_discarded_pair(None, ("Fire", "Water"))
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == {"discarded": [["Earth", "Water"]]}
    discard_store.remove_discarded_pair(None, ("Fire", "Wind"))
    assert json.loads(path.read_text(encoding="utf-8")) == {"discarded": [["Earth", "Water"]]}


def test_clear_discarded_pairs_rewrites_global_format(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "discarded.json"
    monkeypatch.setattr(discard_store, "_discard_path", lambda: path)
    discard_store.add_discarded_pair(None, ("Water", "Fire"))
    discard_store.add_discarded_pair(None, ("Water", "Earth"))
    discard_store.clear_discarded_pairs()
    assert json.loads(path.read_text(encoding="utf-8")) == {"discarded": []}


def test_export_and_import_discarded_pairs(monkeypatch, tmp_path: Path) -> None:
    store_path = tmp_path / "discarded.json"
    export_path = tmp_path / "export.json"
    import_path = tmp_path / "import.json"
    monkeypatch.setattr(discard_store, "_discard_path", lambda: store_path)
    discard_store.add_discarded_pair(None, ("Water", "Fire"))
    discard_store.export_discarded_pairs(export_path)
    assert json.loads(export_path.read_text(encoding="utf-8")) == {
        "discarded": [["Fire", "Water"]]
    }

    import_path.write_text(
        json.dumps({"discarded": [["Earth", "Wind"], ["Water", "Fire"]]}),
        encoding="utf-8",
    )
    imported_pairs = discard_store.import_discarded_pairs(import_path)
    assert imported_pairs == {("Earth", "Wind"), ("Fire", "Water")}
    assert discard_store.load_discarded_pairs() == {("Earth", "Wind"), ("Fire", "Water")}


def test_import_discarded_pairs_rejects_invalid_json_shape(monkeypatch, tmp_path: Path) -> None:
    store_path = tmp_path / "discarded.json"
    import_path = tmp_path / "import.json"
    monkeypatch.setattr(discard_store, "_discard_path", lambda: store_path)
    import_path.write_text("[]", encoding="utf-8")
    try:
        discard_store.import_discarded_pairs(import_path)
    except ValueError as exc:
        assert "JSON object" in str(exc)
    else:
        raise AssertionError("ValueError expected for invalid imported JSON shape")
