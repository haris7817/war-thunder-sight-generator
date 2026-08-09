"""M6 integration: trace -> transform -> export, and GUI panel wiring."""

from __future__ import annotations

from app.application.export_service import build_export, export_to_file
from app.application.tracing_service import trace
from app.blk.coordinate_mapper import CoordinateMapper
from app.domain.settings import TraceSettings
from app.domain.transform import ArtworkTransform
from app.ui.main_window import MainWindow

from tests.fixtures import synthetic

# --- headless integration ------------------------------------------------------


def test_trace_transform_export_round_trip(tmp_path):
    img = synthetic.filled_circle(240)
    result = trace(img, TraceSettings(detail=60))
    assert result.segment_count > 0

    mapper = CoordinateMapper(image_width=result.width, image_height=result.height)
    transform = ArtworkTransform(offset_x=0.1, offset_y=-0.05, scale=1.2)
    export, path = export_to_file(
        list(result.segments), [], mapper, transform, tmp_path / "out.blk"
    )
    text = path.read_text(encoding="utf-8")
    assert "drawLines{" in text
    assert text.count("{") == text.count("}")
    assert export.line_count == result.segment_count


def test_transform_offset_shifts_exported_coordinates():
    img = synthetic.filled_circle(240)
    result = trace(img, TraceSettings(detail=60))
    mapper = CoordinateMapper(image_width=result.width, image_height=result.height)

    base = build_export(list(result.segments), [], mapper, ArtworkTransform.identity())
    shifted = build_export(
        list(result.segments), [], mapper, ArtworkTransform(offset_x=0.25)
    )
    # The x-shift of 0.25 must appear in the coordinates (files differ).
    assert base.text != shifted.text


# --- GUI wiring (pytest-qt, offscreen) -----------------------------------------


def test_retrace_populates_geometry(qtbot):
    w = MainWindow()
    qtbot.addWidget(w)
    w._rgb = synthetic.filled_circle(240)
    w._store.set_source("mem", (240, 240))

    w._on_retrace()
    w._runner.wait_for_done(8000)
    qtbot.wait(150)

    assert w._canvas.line_count > 0
    assert "lines 0" not in w._status.text()


def test_transform_change_propagates_to_canvas_and_store(qtbot):
    w = MainWindow()
    qtbot.addWidget(w)
    t = ArtworkTransform(offset_x=0.2, scale=2.0, rotation_deg=15.0)
    w._on_transform_changed(t)
    assert w._canvas._artwork.scale == 2.0
    assert w._store.transform.offset_x == 0.2


def test_panels_present(qtbot):
    w = MainWindow()
    qtbot.addWidget(w)
    assert w._trace is not None
    assert w._transform is not None
    assert w._export is not None
    # Trace panel yields a valid settings object.
    assert 0 <= w._trace.settings().detail <= 100
