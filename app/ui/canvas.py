"""The drawing canvas: a custom QWidget painted with QPainter.

Not a QGraphicsView — with up to a few thousand segments repainting during a slider
drag, a single batched paint over prebuilt arrays plus a uniform-grid spatial hash
(for M7's erase) is faster and simpler than per-item QGraphicsItem overhead.

M5 wires the image/preview path; geometry rendering is built here so M6 only has to
feed it segments/quads.
"""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import QLineF, QPointF, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QImage,
    QMouseEvent,
    QPainter,
    QPen,
    QPolygonF,
    QWheelEvent,
)
from PySide6.QtWidgets import QWidget

from app.blk.coordinate_mapper import CoordinateMapper
from app.domain.geometry import LineSegment, Point, Quad
from app.domain.transform import ArtworkTransform
from app.ui import theme
from app.ui.spatial_hash import SpatialHash
from app.ui.tools.base import Tool, ToolEvent
from app.ui.tools.select_tool import SelectTool
from app.ui.view_transform import ViewTransform, fit_zoom


def ndarray_to_qimage(rgb: np.ndarray) -> QImage:
    """Convert an HxWx3 uint8 RGB array to a QImage (owns a copy of the data)."""
    h, w = rgb.shape[:2]
    contiguous = np.ascontiguousarray(rgb, dtype=np.uint8)
    img = QImage(contiguous.data, w, h, 3 * w, QImage.Format.Format_RGB888)
    return img.copy()  # detach from the numpy buffer


class Canvas(QWidget):
    """Displays the source/preview image, traced geometry, and centre guides."""

    viewChanged = Signal()  # emitted when zoom/pan changes (for status line)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(320, 240)
        self.setMouseTracking(True)

        self._image: QImage | None = None
        self._img_w = 0
        self._img_h = 0
        self._lines: tuple[LineSegment, ...] = ()
        self._quads: tuple[Quad, ...] = ()
        self._hash = SpatialHash()
        self._mapper: CoordinateMapper | None = None
        self._artwork = ArtworkTransform.identity()

        self._zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._panning = False
        self._last_mouse = QPointF()

        self._tool: Tool = SelectTool()

    # --- public API ------------------------------------------------------------

    def set_image(self, rgb: np.ndarray | None) -> None:
        if rgb is None:
            self._image = None
        else:
            self._image = ndarray_to_qimage(rgb)
            self._img_h, self._img_w = rgb.shape[:2]
            self._mapper = CoordinateMapper(image_width=self._img_w, image_height=self._img_h)
            self.fit_to_view()
        self.update()

    def set_artwork_transform(self, transform: ArtworkTransform) -> None:
        self._artwork = transform
        self.update()

    def _transform_point(self, px: float, py: float) -> tuple[float, float]:
        """Apply the artwork transform in pixel space, matching the exporter exactly.

        Goes pixel -> sight (with transform) -> pixel, so the on-canvas preview lands
        where the exported .blk will (both use the same CoordinateMapper + transform).
        """
        if self._mapper is None or self._artwork.is_identity:
            return px, py
        sx, sy = self._mapper.to_sight_transformed(px, py, self._artwork)
        return self._mapper.from_sight(sx, sy)

    def set_geometry(self, lines: tuple[LineSegment, ...], quads: tuple[Quad, ...] = ()) -> None:
        self._lines = tuple(lines)
        self._quads = tuple(quads)
        self._hash.build(self._lines)
        self.update()

    def set_tool(self, tool: Tool) -> None:
        self._tool = tool

    @property
    def zoom_percent(self) -> int:
        return int(round(self._zoom * 100))

    @property
    def line_count(self) -> int:
        return len(self._lines)

    @property
    def quad_count(self) -> int:
        return len(self._quads)

    def view_transform(self) -> ViewTransform:
        return ViewTransform(
            zoom=self._zoom,
            pan_x=self._pan_x,
            pan_y=self._pan_y,
            widget_w=float(self.width()),
            widget_h=float(self.height()),
            img_w=float(self._img_w),
            img_h=float(self._img_h),
        )

    def fit_to_view(self) -> None:
        if self._img_w and self._img_h:
            self._zoom = fit_zoom(self.width(), self.height(), self._img_w, self._img_h)
        self._pan_x = 0.0
        self._pan_y = 0.0
        self.viewChanged.emit()

    # --- painting --------------------------------------------------------------

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillRect(self.rect(), QColor(theme.CANVAS_BG))

        vt = self.view_transform()

        if self._image is not None:
            top_left = vt.image_to_screen(0, 0)
            bottom_right = vt.image_to_screen(self._img_w, self._img_h)
            target = self._qrectf(top_left, bottom_right)
            painter.drawImage(target, self._image)

        self._paint_geometry(painter, vt)
        self._paint_center_guides(painter)

    def _screen_pt(self, vt: ViewTransform, px: float, py: float) -> tuple[float, float]:
        tx, ty = self._transform_point(px, py)
        return vt.image_to_screen(tx, ty)

    def _paint_geometry(self, painter: QPainter, vt: ViewTransform) -> None:
        if self._quads:
            painter.setPen(Qt.PenStyle.NoPen)
            fill = QColor(theme.ACCENT)
            fill.setAlpha(110)
            painter.setBrush(QBrush(fill))
            for q in self._quads:
                poly = QPolygonF(
                    [QPointF(*self._screen_pt(vt, p.x, p.y)) for p in q.vertices]
                )
                painter.drawPolygon(poly)
            painter.setBrush(Qt.BrushStyle.NoBrush)

        if self._lines:
            pen = QPen(QColor(theme.ACCENT))
            pen.setCosmetic(True)
            pen.setWidthF(1.4)
            painter.setPen(pen)
            batch = [
                QLineF(*self._screen_pt(vt, s.a.x, s.a.y), *self._screen_pt(vt, s.b.x, s.b.y))
                for s in self._lines
            ]
            painter.drawLines(batch)

    def _paint_center_guides(self, painter: QPainter) -> None:
        cx = self.width() / 2.0
        cy = self.height() / 2.0
        pen = QPen(QColor(theme.TEXT_MUTED))
        pen.setCosmetic(True)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(QPointF(cx, 0), QPointF(cx, self.height()))
        painter.drawLine(QPointF(0, cy), QPointF(self.width(), cy))

    @staticmethod
    def _qrectf(tl: tuple[float, float], br: tuple[float, float]):
        from PySide6.QtCore import QRectF

        return QRectF(QPointF(*tl), QPointF(*br))

    # --- interaction -----------------------------------------------------------

    def wheelEvent(self, event: QWheelEvent) -> None:
        # Zoom around the cursor position.
        delta = event.angleDelta().y()
        if delta == 0:
            return
        factor = 1.0015**delta
        pos = event.position()
        before = self.view_transform().screen_to_image(pos.x(), pos.y())
        self._zoom = max(0.02, min(50.0, self._zoom * factor))
        after_vt = self.view_transform()
        after_screen = after_vt.image_to_screen(*before)
        # Adjust pan so the point under the cursor stays put.
        self._pan_x += pos.x() - after_screen[0]
        self._pan_y += pos.y() - after_screen[1]
        self.viewChanged.emit()
        self.update()

    def _tool_event(self, event: QMouseEvent) -> ToolEvent:
        pos = event.position()
        ix, iy = self.view_transform().screen_to_image(pos.x(), pos.y())
        return ToolEvent(
            image_pos=Point(ix, iy),
            screen_x=pos.x(),
            screen_y=pos.y(),
            left_button=bool(event.buttons() & Qt.MouseButton.LeftButton),
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._last_mouse = event.position()
            return
        self._tool.on_press(self, self._tool_event(event))

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._panning:
            pos = event.position()
            self._pan_x += pos.x() - self._last_mouse.x()
            self._pan_y += pos.y() - self._last_mouse.y()
            self._last_mouse = pos
            self.viewChanged.emit()
            self.update()
            return
        self._tool.on_move(self, self._tool_event(event))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            return
        self._tool.on_release(self, self._tool_event(event))
