"""Small tool-rail icons drawn with QPainter (no external asset files).

Icons are stroked in the light text colour so they read on both the idle (dark) and
active (accent) button backgrounds.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QIcon, QPainter, QPen, QPixmap, QPolygonF

from app.ui import theme

_SIZE = 24


def _make(draw: Callable[[QPainter], None]) -> QIcon:
    pm = QPixmap(_SIZE, _SIZE)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pen = QPen(QColor(theme.TEXT))
    pen.setWidthF(1.8)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    draw(p)
    p.end()
    return QIcon(pm)


def select_icon() -> QIcon:
    """A cursor arrow."""

    def draw(p: QPainter) -> None:
        p.setBrush(QBrush(QColor(theme.TEXT)))
        arrow = QPolygonF(
            [
                QPointF(6, 4),
                QPointF(6, 18),
                QPointF(10, 14),
                QPointF(13, 20),
                QPointF(15, 19),
                QPointF(12, 13),
                QPointF(17, 13),
            ]
        )
        p.drawPolygon(arrow)

    return _make(draw)


def draw_icon() -> QIcon:
    """A pencil (diagonal body + tip)."""

    def draw(p: QPainter) -> None:
        p.drawLine(QPointF(6, 18), QPointF(16, 8))  # body
        p.drawLine(QPointF(16, 8), QPointF(18, 6))  # top
        p.drawLine(QPointF(6, 18), QPointF(5, 19))  # tip
        p.drawLine(QPointF(14, 6), QPointF(18, 10))  # ferrule cross

    return _make(draw)


def erase_icon() -> QIcon:
    """An eraser / rubber block (tilted rounded rectangle with a band)."""

    def draw(p: QPainter) -> None:
        body = QPolygonF(
            [
                QPointF(4, 15),
                QPointF(13, 6),
                QPointF(20, 9),
                QPointF(11, 18),
            ]
        )
        p.setBrush(QBrush(QColor(theme.TEXT_MUTED)))
        p.drawPolygon(body)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(QPointF(8.5, 10.5), QPointF(15.5, 13.5))  # band

    return _make(draw)
