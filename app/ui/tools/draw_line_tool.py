"""Draw-line tool: press to start, release to commit a manual line segment."""

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

    def on_release(self, canvas, event: ToolEvent) -> None:
        start, self._start = self._start, None
        if start is None:
            return
        end = event.image_pos
        if start.x != end.x or start.y != end.y:
            self._on_draw(start, end)
