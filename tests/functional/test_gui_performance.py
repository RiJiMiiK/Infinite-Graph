from __future__ import annotations

import pytest

from src.infinite_graph import gui


@pytest.fixture()
def sample_render_data() -> dict[str, object]:
    return {
        "positions": [(0.0, 0.0), (100.0, 0.0), (50.0, 100.0)],
        "adj": [(0, 2), (1, 2)],
        "sizes": [16, 16, 15],
        "brushes": [
            gui.pg.mkBrush("#10b981"),
            gui.pg.mkBrush("#10b981"),
            gui.pg.mkBrush("#2563eb"),
        ],
        "labels": [],
        "node_ids": ["Water", "Fire", "Steam"],
        "node_weights": [0, 0, 1],
    }


def test_ui_only_graph_filters_do_not_trigger_full_recomputation(
    monkeypatch,
    qapp,
    sample_result,
    sample_render_data,
) -> None:
    del qapp
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._full_render_data = sample_render_data
    window.graph_view.update_graph(sample_render_data)

    monkeypatch.setattr(
        gui,
        "process_save",
        lambda *args, **kwargs: pytest.fail("process_save should not run for UI-only changes"),
    )
    monkeypatch.setattr(
        gui,
        "build_graph_render_data",
        lambda *args, **kwargs: pytest.fail(
            "build_graph_render_data should not run for graph view filters"
        ),
    )

    window.subgraph_center_edit.setText("Steam")
    window.subgraph_depth_edit.setText("1")
    window._apply_subgraph_filter()
    assert window.graph_view.current_render_data["node_ids"] == ["Water", "Fire", "Steam"]

    window.min_weight_edit.setText("0")
    window.max_weight_edit.setText("0")
    window._apply_weight_filter()
    assert window.graph_view.current_render_data["node_ids"] == ["Water", "Fire"]
    window.close()
