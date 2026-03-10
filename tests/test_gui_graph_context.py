from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent

from src.infinite_graph import gui


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
        ],
        "graph_edges": [],
        "node_weights": {"Water": 0, "Fire": 0, "Wind": 0, "Earth": 0, "Steam": 1},
        "known_pairs": {("Fire", "Water")},
        "discarded_pairs": set(),
        "done_pairs": set(),
        "skipped_pairs": set(),
        "statistics": {
            "recipe_counts_by_result_weight": [],
            "node_counts_by_weight": [],
            "missing_counts_by_result_weight": [],
        },
        "missing": [],
        "missing_limit": 1000,
        "focus_element": None,
    }


def test_graph_view_widget_right_click_requests_context_menu(qapp, monkeypatch) -> None:
    widget = gui.GraphViewWidget()
    widget.update_graph(
        {
            "positions": [(0.0, 0.0)],
            "adj": [],
            "sizes": [10],
            "brushes": [gui.pg.mkBrush("#ffffff")],
            "labels": [],
            "node_ids": ["Water"],
        }
    )
    selected = []
    requested = []
    monkeypatch.setattr(widget, "_node_id_at", lambda position: "Water")
    monkeypatch.setattr(widget, "select_node_by_id", lambda node_id: selected.append(node_id))
    widget.contextMenuRequested.connect(lambda node_id, point: requested.append((node_id, point)))

    event = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(1, 1),
        QPointF(1, 1),
        Qt.MouseButton.RightButton,
        Qt.MouseButton.RightButton,
        Qt.KeyboardModifier.NoModifier,
    )
    widget.mousePressEvent(event)

    assert selected == ["Water"]
    assert requested
    assert requested[-1][0] == "Water"

    widget._selected_node_id = "Water"
    monkeypatch.setattr(widget, "_node_id_at", lambda position: None)
    widget.mousePressEvent(event)
    assert requested[-1][0] == "Water"


def test_window_graph_context_menu_actions(qapp, sample_result, monkeypatch) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    selected = []

    class _Clipboard:
        def __init__(self) -> None:
            self.text = ""

        def setText(self, value: str) -> None:
            self.text = value

    clipboard = _Clipboard()
    monkeypatch.setattr(gui.QApplication, "clipboard", staticmethod(lambda: clipboard))
    monkeypatch.setattr(window.graph_view, "select_node_by_id", lambda node_id: selected.append(node_id))

    chosen_label = {"value": None}

    class _FakeMenu:
        def __init__(self, parent=None) -> None:
            del parent
            self.actions = {}

        def addAction(self, label: str):
            action = object()
            self.actions[label] = action
            return action

        def exec(self, global_pos):
            del global_pos
            if chosen_label["value"] is None:
                return None
            return self.actions[chosen_label["value"]]

    monkeypatch.setattr(gui, "QMenu", _FakeMenu)

    window._show_graph_context_menu(None, None)

    chosen_label["value"] = "Copy element name"
    window._show_graph_context_menu("Water", None)
    assert clipboard.text == "Water"

    chosen_label["value"] = "Use as Element 1"
    window._show_graph_context_menu("Water", None)
    assert window.element1_edit.text() == "Water"

    chosen_label["value"] = "Use as Element 2"
    window._show_graph_context_menu("Steam", None)
    assert window.element2_edit.text() == "Steam"

    chosen_label["value"] = "Search this element"
    window._show_graph_context_menu("Water", None)
    assert window.graph_search_edit.text() == "Water"
    assert selected[-1] == "Water"

    window.subgraph_depth_edit.clear()
    chosen_label["value"] = "Set as subgraph center"
    window._show_graph_context_menu("Steam", None)
    assert window.subgraph_center_edit.text() == "Steam"
    assert window.subgraph_depth_edit.text() == "1"
    window.close()
