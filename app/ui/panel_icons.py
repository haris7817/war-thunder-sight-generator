"""Small line icons for panel section headers and buttons (drawn, no asset files)."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap

from app.ui import theme

_SIZE = 20


def _make(draw: Callable[[QPainter], None], color: str = theme.TEXT_MUTED, width: float = 1.6) -> QIcon:
    pm = QPixmap(_SIZE, _SIZE)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pen = QPen(QColor(color))
    pen.setWidthF(width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    draw(p)
    p.end()
    return QIcon(pm)


# --- section icons -------------------------------------------------------------


def source_icon() -> QIcon:
    def d(p: QPainter) -> None:
        p.drawRoundedRect(QRectF(3, 4, 14, 12), 2, 2)
        p.drawEllipse(QPointF(7, 8), 1.4, 1.4)
        p.drawPolyline([QPointF(4, 15), QPointF(9, 10), QPointF(12, 13), QPointF(16, 8)])

    return _make(d)


def tracing_icon() -> QIcon:
    def d(p: QPainter) -> None:
        p.drawPolyline(
            [QPointF(4, 15), QPointF(8, 15), QPointF(8, 6), QPointF(14, 6), QPointF(16, 6)]
        )
        p.drawEllipse(QPointF(4, 15), 1.3, 1.3)
        p.drawEllipse(QPointF(16, 6), 1.3, 1.3)

    return _make(d)


def shading_icon() -> QIcon:
    def d(p: QPainter) -> None:
        p.drawRoundedRect(QRectF(4, 4, 12, 12), 2, 2)
        p.drawLine(QPointF(6, 13), QPointF(13, 6))
        p.drawLine(QPointF(9, 14), QPointF(14, 9))

    return _make(d)


def transform_icon() -> QIcon:
    def d(p: QPainter) -> None:
        p.drawLine(QPointF(10, 3), QPointF(10, 17))
        p.drawLine(QPointF(3, 10), QPointF(17, 10))
        p.drawPolyline([QPointF(7, 6), QPointF(10, 3), QPointF(13, 6)])
        p.drawPolyline([QPointF(14, 7), QPointF(17, 10), QPointF(14, 13)])

    return _make(d)


def export_icon() -> QIcon:
    def d(p: QPainter) -> None:
        p.drawLine(QPointF(10, 3), QPointF(10, 12))
        p.drawPolyline([QPointF(6, 8), QPointF(10, 12), QPointF(14, 8)])
        p.drawPolyline([QPointF(4, 14), QPointF(4, 17), QPointF(16, 17), QPointF(16, 14)])

    return _make(d)


# --- button icons (brighter so they read on buttons) --------------------------


def upload_icon() -> QIcon:
    def d(p: QPainter) -> None:
        p.drawLine(QPointF(10, 4), QPointF(10, 13))
        p.drawPolyline([QPointF(6, 8), QPointF(10, 4), QPointF(14, 8)])
        p.drawPolyline([QPointF(4, 14), QPointF(4, 17), QPointF(16, 17), QPointF(16, 14)])

    return _make(d, color=theme.TEXT)


def refresh_icon() -> QIcon:
    def d(p: QPainter) -> None:
        p.drawArc(QRectF(4, 4, 12, 12), 60 * 16, 250 * 16)
        p.drawPolyline([QPointF(14, 3), QPointF(15, 7), QPointF(11, 7)])

    return _make(d, color=theme.TEXT)


def download_icon() -> QIcon:
    def d(p: QPainter) -> None:
        p.drawLine(QPointF(10, 3), QPointF(10, 12))
        p.drawPolyline([QPointF(6, 8), QPointF(10, 12), QPointF(14, 8)])
        p.drawPolyline([QPointF(4, 14), QPointF(4, 17), QPointF(16, 17), QPointF(16, 14)])

    return _make(d, color="#0b0d10", width=1.8)  # dark, for the blue Export button
