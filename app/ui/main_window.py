"""Main window: tool rail | canvas | control panel, with a status line.

M6 wires the full loop with no CLI: import -> (threshold inspect) -> Re-trace ->
move/scale/rotate -> Export .blk. Heavy work (threshold preview, tracing, export)
runs on the worker pool so the UI stays responsive.
"""

from __future__ import annotations

import os
from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app import __version__
from app.application.editing_service import SessionStore
from app.application.export_service import export_to_file
from app.application.shading_service import generate as generate_shading_geometry
from app.application.tracing_service import TraceMode, trace
from app.blk.coordinate_mapper import CoordinateMapper
from app.domain.geometry import Point
from app.domain.transform import ArtworkTransform
from app.infrastructure import config
from app.infrastructure.config import APP_NAME
from app.infrastructure.logging_config import get_logger
from app.infrastructure.workers import CancellationToken, Debouncer, TaskRunner
from app.processing.import_service import ImageImportError, load_image
from app.processing.preprocess import preprocess
from app.processing.threshold import adaptive, global_threshold, otsu, should_invert
from app.ui import theme
from app.ui.canvas import Canvas
from app.ui.panels.export_footer import ExportFooter
from app.ui.panels.shading_panel import ShadingPanel
from app.ui.panels.source_panel import SourcePanel
from app.ui.panels.trace_panel import TracePanel
from app.ui.panels.transform_panel import TransformPanel
from app.ui.toolbar import ToolRail
from app.ui.tools.draw_line_tool import DrawLineTool
from app.ui.tools.erase_tool import EraseTool
from app.ui.tools.select_tool import SelectTool

log = get_logger("ui")


def threshold_preview(rgb: np.ndarray, method: str, level: int) -> np.ndarray:
    """Pure, thread-safe RGB preview of the chosen threshold (runs off-thread)."""
    gray = preprocess(rgb)
    invert = should_invert(gray)
    if method == "global":
        binary = global_threshold(gray, level, invert=invert)
    elif method == "adaptive":
        binary = adaptive(gray, invert=invert)
    else:
        binary = otsu(gray, invert=invert)
    return cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME}  v{__version__}")
        self.resize(1240, 780)

        self._rgb: np.ndarray | None = None
        self._store = SessionStore(self)
        self._runner = TaskRunner()
        self._debouncer = Debouncer(interval_ms=120, parent=self)
        self._preview_token: CancellationToken | None = None
        self._trace_token: CancellationToken | None = None
        self._shading_token: CancellationToken | None = None
        self._shading_debouncer = Debouncer(interval_ms=200, parent=self)

        self._rail = ToolRail(
            [
                ("▶", SelectTool(), "Select"),
                ("✎", DrawLineTool(self._on_draw_segment), "Draw line"),
                ("⌫", EraseTool(self._on_erase), "Erase"),
            ]
        )
        self._canvas = Canvas()
        self._panel = self._build_panel()

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._rail)
        layout.addWidget(self._canvas, 1)
        layout.addWidget(self._panel)
        self.setCentralWidget(central)

        self._status = QLabel()
        self._status.setObjectName("muted")
        self.statusBar().addPermanentWidget(self._status)

        self._wire()
        self._update_status()

    # --- construction ----------------------------------------------------------

    def _build_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedWidth(theme.PANEL_WIDTH)
        outer = QVBoxLayout(panel)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Scrollable stack of control sections.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(16, 16, 16, 8)
        vbox.setSpacing(18)

        self._source = SourcePanel()
        self._trace = TracePanel()
        self._shading = ShadingPanel()
        self._transform = TransformPanel()
        for w in (self._source, self._trace, self._shading, self._transform):
            vbox.addWidget(w)
        vbox.addStretch(1)
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

        # Pinned export footer.
        self._export = ExportFooter()
        outer.addWidget(self._export)
        return panel

    def _wire(self) -> None:
        self._rail.toolSelected.connect(self._canvas.set_tool)
        self._source.importClicked.connect(self._on_import)
        self._source.settingsChanged.connect(self._on_settings_changed)
        self._trace.retraceRequested.connect(self._on_retrace)
        self._trace.cancelRequested.connect(self._on_cancel_trace)
        self._shading.changed.connect(self._on_shading_changed)
        self._transform.transformChanged.connect(self._on_transform_changed)
        self._export.exportRequested.connect(self._on_export)
        self._store.geometryChanged.connect(self._on_geometry_changed)
        self._canvas.viewChanged.connect(self._update_status)

        undo = QShortcut(QKeySequence.StandardKey.Undo, self)  # Ctrl+Z
        undo.activated.connect(self._store.undo)

    # --- source / preview ------------------------------------------------------

    def _on_import(self) -> None:
        start_dir = config.get_setting(config.KEY_LAST_IMPORT_DIR, "")
        path, _ = QFileDialog.getOpenFileName(
            self, "Import image", start_dir, "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if not path:
            return
        try:
            img = load_image(path)
        except ImageImportError as exc:
            QMessageBox.warning(self, "Import failed", str(exc))
            return
        config.set_setting(config.KEY_LAST_IMPORT_DIR, str(Path(path).parent))
        self._rgb = img.rgb
        self._store.set_source(path, (img.width, img.height))
        self._canvas.set_image(img.rgb)
        self._canvas.set_geometry((), ())
        self._update_status()

    def _on_settings_changed(self) -> None:
        if self._rgb is not None:
            self._debouncer.call(self._dispatch_preview)

    def _dispatch_preview(self) -> None:
        if self._rgb is None:
            return
        if self._preview_token is not None:
            self._preview_token.cancel()
        self._preview_token = self._runner.submit(
            threshold_preview,
            self._rgb,
            self._source.method(),
            self._source.threshold(),
            on_result=self._canvas.set_image,
            on_error=lambda msg: log.error("preview failed:\n%s", msg),
        )

    # --- tracing ---------------------------------------------------------------

    def _on_retrace(self) -> None:
        if self._rgb is None:
            QMessageBox.information(self, "No image", "Import an image first.")
            return
        self._trace.set_busy(True)
        self._trace_token = CancellationToken()
        settings = self._trace.settings()
        self._runner.submit(
            trace,
            self._rgb,
            settings,
            mode=TraceMode.EDGE,
            on_result=self._on_trace_done,
            on_error=self._on_trace_error,
            token=self._trace_token,
        )

    def _on_cancel_trace(self) -> None:
        if self._trace_token is not None:
            self._trace_token.cancel()
        self._trace.set_busy(False)

    def _on_trace_done(self, result) -> None:
        self._trace.set_busy(False)
        # Show the original artwork as the backdrop with the trace overlaid.
        if self._rgb is not None:
            self._canvas.set_image(self._rgb)
        # Replace only AUTO_TRACE lines — manual edits and shading survive re-trace.
        self._store.set_traced_lines(result.segments)
        for w in result.warnings:
            log.warning(w)

    def _on_trace_error(self, msg: str) -> None:
        self._trace.set_busy(False)
        log.error("trace failed:\n%s", msg)
        QMessageBox.warning(self, "Trace failed", "Tracing failed; see logs/app.log.")

    def _on_geometry_changed(self) -> None:
        self._canvas.set_geometry(self._store.lines, self._store.quads)
        self._update_status()

    # --- transform -------------------------------------------------------------

    def _on_transform_changed(self, transform: ArtworkTransform) -> None:
        self._store.set_transform(transform)
        self._canvas.set_artwork_transform(transform)

    # --- shading ---------------------------------------------------------------

    def _on_shading_changed(self) -> None:
        if self._rgb is not None:
            self._shading_debouncer.call(self._dispatch_shading)

    def _dispatch_shading(self) -> None:
        if self._rgb is None:
            return
        if self._shading_token is not None:
            self._shading_token.cancel()
        settings = self._shading.settings()
        self._shading_token = self._runner.submit(
            generate_shading_geometry,
            self._rgb,
            settings,
            on_result=self._on_shading_done,
            on_error=lambda msg: log.error("shading failed:\n%s", msg),
        )

    def _on_shading_done(self, payload) -> None:
        quads, hatch = payload
        self._store.set_shading(tuple(quads), tuple(hatch))

    # --- manual draw / erase ---------------------------------------------------

    def _on_draw_segment(self, a: Point, b: Point) -> None:
        self._store.add_segment(a, b)

    def _on_erase(self, x: float, y: float, radius: float) -> None:
        self._store.erase_near(x, y, radius)

    # --- export ----------------------------------------------------------------

    def _on_export(self) -> None:
        if not self._store.lines and not self._store.quads:
            QMessageBox.information(self, "Nothing to export", "Trace or draw something first.")
            return
        size = self._store.state.image_size or (self._canvas._img_w, self._canvas._img_h)
        if not size or not size[0]:
            QMessageBox.information(self, "No image", "Import an image first.")
            return

        start_dir = config.get_setting(config.KEY_LAST_EXPORT_DIR, "")
        default = str(Path(start_dir) / "sight_1.blk") if start_dir else "sight_1.blk"
        path, _ = QFileDialog.getSaveFileName(self, "Export sight", default, "Sight (*.blk)")
        if not path:
            return
        config.set_setting(config.KEY_LAST_EXPORT_DIR, str(Path(path).parent))

        mapper = CoordinateMapper(image_width=size[0], image_height=size[1])
        self._runner.submit(
            export_to_file,
            list(self._store.lines),
            list(self._store.quads),
            mapper,
            self._store.transform,
            path,
            on_result=self._on_export_done,
            on_error=self._on_export_error,
        )

    def _on_export_done(self, payload) -> None:
        result, path = payload
        box = QMessageBox(self)
        box.setWindowTitle("Exported")
        box.setText(f"Saved {result.element_count} elements to:\n{path}")
        open_btn = box.addButton("Open folder", QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Ok)
        box.exec()
        if box.clickedButton() is open_btn:
            try:
                os.startfile(Path(path).parent)  # noqa: S606 - Windows-only convenience
            except Exception:  # noqa: BLE001
                pass

    def _on_export_error(self, msg: str) -> None:
        log.error("export failed:\n%s", msg)
        QMessageBox.warning(self, "Export failed", "Export failed; see logs/app.log.")

    # --- status ----------------------------------------------------------------

    def _update_status(self) -> None:
        self._status.setText(
            f"lines {self._canvas.line_count} · quads {self._canvas.quad_count} "
            f"· zoom {self._canvas.zoom_percent}%"
        )

    def closeEvent(self, event) -> None:
        self._runner.shutdown()
        super().closeEvent(event)
