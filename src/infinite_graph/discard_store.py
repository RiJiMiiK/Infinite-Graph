from __future__ import annotations

import json
from pathlib import Path


def _discard_path() -> Path:
    return Path(__file__).resolve().parents[2] / "discarded.json"


def _load_raw_store() -> dict[str, list[list[str]]]:
    path = _discard_path()
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _save_raw_store(data: dict[str, list[list[str]]]) -> None:
    path = _discard_path()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _normalize_pairs(raw_pairs: list[object]) -> set[tuple[str, str]]:
    discarded = set()
    for pair in raw_pairs:
        if isinstance(pair, list) and len(pair) == 2 and all(isinstance(value, str) for value in pair):
            discarded.add(tuple(sorted(pair)))
    return discarded


def load_discarded_pairs(save_path: Path | None = None) -> set[tuple[str, str]]:
    raw = _load_raw_store()
    # New format: {"discarded": [["A", "B"], ...]}
    if "discarded" in raw and isinstance(raw["discarded"], list):
        return _normalize_pairs(raw["discarded"])

    # Backward compatibility: old format keyed by save path.
    merged: set[tuple[str, str]] = set()
    for value in raw.values():
        if isinstance(value, list):
            merged.update(_normalize_pairs(value))
    return merged


def add_discarded_pair(save_path: Path | None, pair: tuple[str, str]) -> None:
    raw = _load_raw_store()
    pairs = load_discarded_pairs(save_path)
    pairs.add(tuple(sorted(pair)))
    _save_raw_store({"discarded": [list(values) for values in sorted(pairs)]})
