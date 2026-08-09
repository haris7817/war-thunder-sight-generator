"""Draw-line tool: straight segments only (MVP).

Press sets the start point; dragging shows a live preview line; release commits one
LineSegment. Esc or right-click cancels the in-progress line. No freehand drawing.
"""

from __future__ import annotations

from collections.abc import Callable

from app.domain.geometry import Point
from app.ui.tools.base import Tool, ToolEvent


class DrawLineTool(Tool):
    name = "draw_line"

    def __init__(self, on_draw: Callable[[Point, Point], None]) -> None:
        self._on_draw = on_draw
        self._start: Point | None = None

    def on_press(self, canvas, event: ToolEvent) -> None:
        self._start = event.image_pos
        canvas.set_preview_line(self._start, self._start)

    def on_move(self, canvas, event: ToolEvent) -> None:
        if self._start is not None:
            canvas.set_preview_line(self._start, event.image_pos)

    def on_release(self, canvas, event: ToolEvent) -> None:
        start, self._start = self._start, None
        canvas.clear_preview_line()
        if start is None:
            return
        end = event.image_pos
        if start.x != end.x or start.y != end.y:
            self._on_draw(start, end)

    def cancel(self, canvas) -> None:
        self._start = None
        canvas.clear_preview_line()

    def deactivate(self, canvas) -> None:
        self.cancel(canvas)
