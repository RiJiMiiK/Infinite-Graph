"""Qt GUI entry point and main window assembly."""

from __future__ import annotations

import sys

from PySide6.QtCore import QThread as _QThread, Qt as _Qt
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog as _QFileDialog,
    QListWidgetItem as _QListWidgetItem,
    QMainWindow,
    QMenu as _QMenu,
    QMessageBox as _QMessageBox,
)

from .analyzer import (
    find_cheapest_combination as _find_cheapest_combination,
    find_random_combination as _find_random_combination,
)
from .discard_store import (
    add_discarded_pair as _add_discarded_pair,
    clear_discarded_pairs as _clear_discarded_pairs,
    export_discarded_pairs as _export_discarded_pairs,
    import_discarded_pairs as _import_discarded_pairs,
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
from .gui_preferences import (
    load_ui_preferences as _load_ui_preferences,
    save_ui_preferences as _save_ui_preferences,
    ui_preferences_path as _ui_preferences_path,
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
__all__ += ["QMenu"]
__all__ += ["find_random_combination", "find_cheapest_combination"]
__all__ += ["add_discarded_pair", "clear_discarded_pairs", "export_discarded_pairs"]
__all__ += ["import_discarded_pairs", "remove_discarded_pair"]
__all__ += ["load_ui_preferences", "save_ui_preferences", "ui_preferences_path"]

PUBLIC_REEXPORTS = (LAYOUT_PROGRESS_END, _layout_cache_file, layout_cache_dir)
PUBLIC_REEXPORTS += (load_cached_layout, nx, pg, save_cached_layout)
Qt = _Qt
QThread = _QThread
QFileDialog = _QFileDialog
QListWidgetItem = _QListWidgetItem
QMessageBox = _QMessageBox
QMenu = _QMenu
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
export_discarded_pairs = _export_discarded_pairs
import_discarded_pairs = _import_discarded_pairs
remove_discarded_pair = _remove_discarded_pair


def ui_preferences_path():
    """Return the UI preferences file path used by the GUI."""
    return _ui_preferences_path()


def load_ui_preferences():
    """Load persisted UI preferences using the public GUI hook."""
    preferences_module = sys.modules[f"{__package__}.gui_preferences"]
    original_path = preferences_module.ui_preferences_path
    preferences_module.ui_preferences_path = ui_preferences_path
    try:
        return _load_ui_preferences()
    finally:
        preferences_module.ui_preferences_path = original_path


def save_ui_preferences(preferences):
    """Persist UI preferences using the public GUI hook."""
    preferences_module = sys.modules[f"{__package__}.gui_preferences"]
    original_path = preferences_module.ui_preferences_path
    preferences_module.ui_preferences_path = ui_preferences_path
    try:
        _save_ui_preferences(preferences)
    finally:
        preferences_module.ui_preferences_path = original_path

WINDOW_STYLE = """
QMainWindow {
    background: #0f172a;
}
QWidget {
    color: #e2e8f0;
    font-size: 13px;
}
QGroupBox {
    background: #111c33;
    border: 1px solid #22314f;
    border-radius: 14px;
    margin-top: 12px;
    padding: 10px 12px 12px 12px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #cbd5e1;
}
QLabel {
    color: #cbd5e1;
}
QLineEdit,
QTextEdit,
QListWidget,
QTableView {
    background: #0b1220;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 6px 8px;
    selection-background-color: #1d4ed8;
    selection-color: #eff6ff;
}
QTextEdit,
QListWidget,
QTableView {
    background: #09111f;
}
QPushButton {
    background: #16233a;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 7px 12px;
    color: #e2e8f0;
    font-weight: 600;
}
QPushButton:hover {
    background: #1d2d4a;
    border-color: #475569;
}
QPushButton:pressed {
    background: #263652;
}
QPushButton:disabled {
    background: #0f172a;
    color: #64748b;
    border-color: #1e293b;
}
QPushButton#primaryButton {
    background: #1d4ed8;
    color: #eff6ff;
    border-color: #1d4ed8;
}
QPushButton#primaryButton:hover {
    background: #1e40af;
    border-color: #1e40af;
}
QPushButton#dangerButton {
    background: #3b1219;
    color: #fecaca;
    border-color: #7f1d1d;
}
QPushButton#dangerButton:hover {
    background: #4c161d;
    border-color: #991b1b;
}
QProgressBar {
    background: #1e293b;
    border: 0;
    border-radius: 8px;
    text-align: center;
    min-height: 18px;
    color: #e2e8f0;
}
QProgressBar::chunk {
    background: #2563eb;
    border-radius: 8px;
}
QTabWidget::pane {
    background: #111c33;
    border: 1px solid #22314f;
    border-radius: 14px;
    top: -1px;
}
QTabBar::tab {
    background: #16233a;
    color: #94a3b8;
    border: 1px solid #334155;
    padding: 8px 14px;
    margin-right: 6px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-weight: 600;
}
QTabBar::tab:selected {
    background: #111c33;
    color: #f8fafc;
    border-bottom-color: #111c33;
}
QHeaderView::section {
    background: #16233a;
    color: #cbd5e1;
    border: 0;
    border-right: 1px solid #334155;
    border-bottom: 1px solid #334155;
    padding: 8px;
    font-weight: 600;
}
QFrame {
    border-radius: 12px;
}
"""


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
        self._last_suggested_pair: tuple[str, str] | None = None
        self._current_candidate_origin: str | None = None
        self._ui_preferences: dict[str, object] = {}

        self.setStyleSheet(WINDOW_STYLE)
        self._build_ui()
        self._load_ui_preferences_state()

    def __getattr__(self, name: str) -> object:
        for bundle_name in ("controls", "graph_ui", "info_ui", "stats_ui"):
            bundle = self.__dict__.get(bundle_name)
            if bundle is not None and hasattr(bundle, name):
                return getattr(bundle, name)
        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._update_responsive_layout(event.size().width())

    def closeEvent(self, event) -> None:
        self._save_ui_preferences_state()
        super().closeEvent(event)


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    window = InfiniteGraphWindow()
    window.show()
    app.exec()
