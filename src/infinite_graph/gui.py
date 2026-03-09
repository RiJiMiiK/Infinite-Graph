"""Qt GUI entry point and main window assembly."""

from __future__ import annotations

import sys

from PySide6.QtCore import QThread as _QThread, Qt as _Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog as _QFileDialog,
    QListWidgetItem as _QListWidgetItem,
    QMainWindow,
    QMessageBox as _QMessageBox,
)

from .analyzer import (
    find_cheapest_combination as _find_cheapest_combination,
    find_random_combination as _find_random_combination,
)
from .discard_store import (
    add_discarded_pair as _add_discarded_pair,
    clear_discarded_pairs as _clear_discarded_pairs,
    remove_discarded_pair as _remove_discarded_pair,
)

from .gui_bundles import (
    create_controls_bundle,
    create_graph_bundle,
    create_info_bundle,
    create_stats_bundle,
)
from .gui_constants import (
    GENERATION_STAGE_PROGRESS,
    INTERFACE_PROGRESS as _INTERFACE_PROGRESS,
    LAYOUT_PROGRESS_END,
)
from .gui_layout import (
    _layout_cache_file,
    build_graph_render_data as _build_graph_render_data,
    build_subgraph_render_data as _build_subgraph_render_data,
    build_weight_filtered_render_data as _build_weight_filtered_render_data,
    layout_cache_dir,
    load_cached_layout,
    nx,
    save_cached_layout,
)
from .gui_table import ListTableModel as _ListTableModel
from .gui_widgets import CopyLineEdit, GraphViewWidget, StatsCanvas as _StatsCanvas, pg
from .gui_window_build import WindowBuildMixin
from .gui_window_combinations import WindowCombinationsMixin
from .gui_window_generation import WindowGenerationMixin
from .gui_window_graph import WindowGraphMixin
from .gui_worker import GenerateWorker
from .service import process_save as _process_save

__all__ = ["CopyLineEdit", "GENERATION_STAGE_PROGRESS", "GenerateWorker", "GraphViewWidget"]
__all__ += ["INTERFACE_PROGRESS", "LAYOUT_PROGRESS_END", "InfiniteGraphWindow", "ListTableModel"]
__all__ += ["StatsCanvas", "_layout_cache_file", "build_graph_render_data"]
__all__ += ["build_subgraph_render_data", "build_weight_filtered_render_data", "layout_cache_dir"]
__all__ += ["load_cached_layout", "main", "nx", "pg", "save_cached_layout"]
__all__ += ["QFileDialog", "QListWidgetItem", "QMessageBox", "QThread", "Qt", "process_save"]
__all__ += ["find_random_combination", "find_cheapest_combination"]
__all__ += ["add_discarded_pair", "clear_discarded_pairs", "remove_discarded_pair"]

PUBLIC_REEXPORTS = (LAYOUT_PROGRESS_END, _layout_cache_file, layout_cache_dir)
PUBLIC_REEXPORTS += (load_cached_layout, nx, pg, save_cached_layout)
Qt = _Qt
QThread = _QThread
QFileDialog = _QFileDialog
QListWidgetItem = _QListWidgetItem
QMessageBox = _QMessageBox
INTERFACE_PROGRESS = _INTERFACE_PROGRESS
ListTableModel = _ListTableModel
StatsCanvas = _StatsCanvas
process_save = _process_save
build_graph_render_data = _build_graph_render_data
build_subgraph_render_data = _build_subgraph_render_data
build_weight_filtered_render_data = _build_weight_filtered_render_data
find_random_combination = _find_random_combination
find_cheapest_combination = _find_cheapest_combination
add_discarded_pair = _add_discarded_pair
clear_discarded_pairs = _clear_discarded_pairs
remove_discarded_pair = _remove_discarded_pair


class InfiniteGraphWindow(
    WindowBuildMixin,
    WindowGenerationMixin,
    WindowGraphMixin,
    WindowCombinationsMixin,
    QMainWindow,
):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Infinite Graph")
        self.resize(1480, 940)

        self.controls = create_controls_bundle(self)
        self.graph_ui = create_graph_bundle()
        self.info_ui = create_info_bundle()
        self.stats_ui = create_stats_bundle()
        self._worker_thread: QThread | None = None
        self._worker: GenerateWorker | None = None
        self._current_result: dict[str, object] | None = None
        self._current_save_path = None
        self._full_render_data: dict[str, object] | None = None
        self._last_generation_elapsed_seconds = 0.0
        self._last_suggestion_mode: str | None = None

        self._build_ui()

    def __getattr__(self, name: str) -> object:
        for bundle_name in ("controls", "graph_ui", "info_ui", "stats_ui"):
            bundle = self.__dict__.get(bundle_name)
            if bundle is not None and hasattr(bundle, name):
                return getattr(bundle, name)
        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    window = InfiniteGraphWindow()
    window.show()
    app.exec()
