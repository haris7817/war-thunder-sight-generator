"""pytest-qt tests for the M5 UI shell (offscreen)."""

from __future__ import annotations

from app.infrastructure.config import APP_NAME
from app.ui import theme
from app.ui.canvas import Canvas
from app.ui.main_window import MainWindow, threshold_preview

from tests.fixtures import synthetic


def test_main_window_constructs(qtbot):
    w = MainWindow()
    qtbot.addWidget(w)
    assert APP_NAME in w.windowTitle()
    # Rail, canvas, and source panel are present.
    assert w._rail is not None
    assert isinstance(w._canvas, Canvas)
    assert w._source is not None


def test_status_line_default(qtbot):
    w = MainWindow()
    qtbot.addWidget(w)
    assert "lines 0" in w._status.text()
    assert "zoom" in w._status.text()


def test_theme_applies(qtbot):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    theme.apply_theme(app)
    assert theme.ACCENT in app.styleSheet()


def test_canvas_set_image_updates_dimensions(qtbot):
    c = Canvas()
    qtbot.addWidget(c)
    c.set_image(synthetic.line_art(120))
    assert (c._img_w, c._img_h) == (120, 120)
    assert c.zoom_percent > 0


def test_canvas_center_guides_do_not_crash_on_paint(qtbot):
    c = Canvas()
    qtbot.addWidget(c)
    c.resize(400, 300)
    c.set_image(synthetic.crosshair(100))
    c.grab()  # forces a paintEvent offscreen


def test_source_panel_defaults(qtbot):
    w = MainWindow()
    qtbot.addWidget(w)
    assert w._source.method() == "otsu"
    assert 0 <= w._source.threshold() <= 255


def test_threshold_preview_is_rgb():
    preview = threshold_preview(synthetic.line_art(80), "otsu", 128)
    assert preview.ndim == 3 and preview.shape[2] == 3


def test_import_settings_change_triggers_preview(qtbot):
    w = MainWindow()
    qtbot.addWidget(w)
    # Simulate a loaded image, then a settings change -> debounced preview dispatch.
    w._rgb = synthetic.line_art(100)
    w._on_settings_changed()
    w._debouncer.flush()
    w._runner.wait_for_done(3000)
    qtbot.wait(50)
    # Preview delivered to the canvas as an image.
    assert w._canvas._image is not None
