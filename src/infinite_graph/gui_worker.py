"""Background worker used by the Qt GUI."""

from __future__ import annotations

import sys
import time
from pathlib import Path

from PySide6.QtCore import QObject, Signal


class GenerateWorker(QObject):
    progress = Signal(int, str)
    finished = Signal(dict, dict, float)
    failed = Signal(str)

    def __init__(
        self,
        input_path: str,
        focus_element: str | None,
        layout_iterations: int,
        spring_scale: float,
    ) -> None:
        super().__init__()
        self.input_path = input_path
        self.focus_element = focus_element
        self.layout_iterations = layout_iterations
        self.spring_scale = spring_scale

    def run(self) -> None:
        started_at = time.perf_counter()
        try:
            gui_module = sys.modules[f"{__package__}.gui"]
            self.progress.emit(0, "Starting generation")

            def emit_process_progress(message: str) -> None:
                self.progress.emit(gui_module.GENERATION_STAGE_PROGRESS.get(message, 0), message)

            result = gui_module.process_save(
                Path(self.input_path),
                focus_element=self.focus_element,
                progress_callback=emit_process_progress,
            )
            render_data = gui_module.build_graph_render_data(
                result["graph_nodes"],
                result["graph_edges"],
                progress_callback=self.progress.emit,
                layout_iterations=self.layout_iterations,
                spring_scale=self.spring_scale,
                cache_save_path=Path(self.input_path),
            )
            self.progress.emit(
                gui_module.GENERATION_STAGE_PROGRESS["Preparing interface update"],
                "Preparing interface update",
            )
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result, render_data, time.perf_counter() - started_at)
