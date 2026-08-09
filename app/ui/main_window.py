"""Main window: tool rail | canvas | control panel, with a status line.

M5 wires the SOURCE panel end to end: importing an image and dragging the threshold
slider recomputes a preview on a background thread (debounced + cancellable) so the
UI never blocks. Trace/transform/export panels are added in M6.
"""

from __future__ import annotations

import cv2
import numpy as np
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QWidget,
)

from app import __version__
from app.infrastructure.config import APP_NAME
from app.infrastructure.logging_config import get_logger
from app.infrastructure.workers import CancellationToken, Debouncer, TaskRunner
from app.processing.import_service import ImageImportError, load_image
from app.processing.preprocess import preprocess
from app.processing.threshold import adaptive, global_threshold, otsu, should_invert
from app.ui import theme
from app.ui.canvas import Canvas
from app.ui.panels.source_panel import SourcePanel
from app.ui.toolbar import ToolRail

log = get_logger("ui")


def threshold_preview(rgb: np.ndarray, method: str, level: int) -> np.ndarray:
    """Pure, thread-safe: produce an RGB preview of the chosen threshold.

    Runs on a worker thread, so it must not touch Qt.
    """
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
        self.resize(1200, 760)

        self._rgb: np.ndarray | None = None
        self._runner = TaskRunner()
        self._debouncer = Debouncer(interval_ms=120, parent=self)
        self._preview_token: CancellationToken | None = None

        self._rail = ToolRail()
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

        self._status = QLabel("lines 0 · quads 0 · zoom 100%")
        self._status.setObjectName("muted")
        self.statusBar().addPermanentWidget(self._status)

        # Wiring
        self._rail.toolSelected.connect(self._canvas.set_tool)
        self._source.importClicked.connect(self._on_import)
        self._source.settingsChanged.connect(self._on_settings_changed)
        self._canvas.viewChanged.connect(self._update_status)
        self._update_status()

    def _build_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedWidth(theme.PANEL_WIDTH)
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        self._source = SourcePanel()
        layout.addWidget(self._source)
        return panel

    # --- actions ---------------------------------------------------------------

    def _on_import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Import image", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if not path:
            return
        try:
            img = load_image(path)
        except ImageImportError as exc:
            QMessageBox.warning(self, "Import failed", str(exc))
            return
        self._rgb = img.rgb
        self._canvas.set_image(img.rgb)
        self._update_status()
        self._on_settings_changed()  # show an initial threshold preview

    def _on_settings_changed(self) -> None:
        if self._rgb is None:
            return
        # Debounce the flurry of slider events into one dispatch.
        self._debouncer.call(self._dispatch_preview)

    def _dispatch_preview(self) -> None:
        if self._rgb is None:
            return
        if self._preview_token is not None:
            self._preview_token.cancel()  # drop the superseded job
        method = self._source.method()
        level = self._source.threshold()
        self._preview_token = self._runner.submit(
            threshold_preview,
            self._rgb,
            method,
            level,
            on_result=self._canvas.set_image,
            on_error=lambda msg: log.error("preview failed:\n%s", msg),
        )

    def _update_status(self) -> None:
        self._status.setText(
            f"lines {self._canvas.line_count} · quads {self._canvas.quad_count} "
            f"· zoom {self._canvas.zoom_percent}%"
        )

    def closeEvent(self, event) -> None:
        self._runner.shutdown()
        super().closeEvent(event)
