from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture()
def sample_result() -> dict[str, object]:
    return {
        "elements": ["Water", "Fire", "Wind", "Earth", "Steam"],
        "recipes": [{"left": "Water", "right": "Fire", "result": "Steam"}],
        "load_warnings": [],
        "ignored_element_entries": 0,
        "ignored_item_entries": 0,
        "ignored_recipe_entries": 0,
        "graph_nodes": [
            {"id": "Water", "label": "Water", "weight": 0, "is_starter": True},
            {"id": "Fire", "label": "Fire", "weight": 0, "is_starter": True},
        ],
        "graph_edges": [
            {"source": "Water", "target": "Fire", "weight": 1, "elements": ["Steam"]}
        ],
        "node_weights": {"Water": 0, "Fire": 0, "Wind": 0, "Earth": 0, "Steam": 1},
        "known_pairs": {("Fire", "Water")},
        "discarded_pairs": {("Earth", "Wind")},
        "done_pairs": set(),
        "skipped_pairs": set(),
        "statistics": {
            "recipe_counts_by_result_weight": [(1, 1)],
            "node_counts_by_weight": [(0, 2)],
            "missing_counts_by_result_weight": [(1, 4)],
        },
        "missing": [("Earth", "Water"), ("Earth", "Earth")],
        "missing_limit": 1000,
        "focus_element": None,
        "community_graph": object(),
    }


@pytest.fixture()
def qapp():
    app = QApplication.instance() or QApplication([])
    return app
