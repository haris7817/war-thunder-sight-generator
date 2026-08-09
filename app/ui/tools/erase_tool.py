"""Erase tool: click or drag to remove lines near the cursor.

The erase radius is a fixed screen distance converted to image space via the current
zoom, so the effective reach stays constant on screen regardless of zoom level.
"""

from __future__ import annotations

from collections.abc import Callable

from app.ui.tools.base import Tool, ToolEvent

SCREEN_RADIUS = 12.0  # pixels on screen


class EraseTool(Tool):
    name = "erase"

    def __init__(self, on_erase: Callable[[float, float, float], None]) -> None:
        self._on_erase = on_erase

    def _image_radius(self, canvas) -> float:
        zoom = canvas.view_transform().zoom
        return SCREEN_RADIUS / zoom if zoom else SCREEN_RADIUS

    def on_press(self, canvas, event: ToolEvent) -> None:
        self._on_erase(event.image_pos.x, event.image_pos.y, self._image_radius(canvas))

    def on_move(self, canvas, event: ToolEvent) -> None:
        if event.left_button:
            self._on_erase(event.image_pos.x, event.image_pos.y, self._image_radius(canvas))
