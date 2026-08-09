"""Erase tool: removes the single nearest line segment under the cursor.

* Hover highlights the exact segment that would be deleted.
* Click deletes that one segment (never the whole connected contour).
* Click-drag continuously deletes segments the cursor passes over (one stroke = one undo).
* Shading quads are never affected.

The erase radius is a fixed screen distance converted to image space via the current
zoom, so the reach is constant on screen.
"""

from __future__ import annotations

from collections.abc import Callable

from app.ui.tools.base import Tool, ToolEvent

SCREEN_RADIUS = 10.0  # pixels on screen


class EraseTool(Tool):
    name = "erase"

    def __init__(self, on_erase: Callable[[float, float, float, bool], None]) -> None:
        # on_erase(x, y, radius, record_undo)
        self._on_erase = on_erase

    def _image_radius(self, canvas) -> float:
        zoom = canvas.view_transform().zoom
        return SCREEN_RADIUS / zoom if zoom else SCREEN_RADIUS

    def on_press(self, canvas, event: ToolEvent) -> None:
        r = self._image_radius(canvas)
        self._on_erase(event.image_pos.x, event.image_pos.y, r, True)  # start of stroke
        canvas.set_erase_highlight(event.image_pos.x, event.image_pos.y, r)

    def on_move(self, canvas, event: ToolEvent) -> None:
        r = self._image_radius(canvas)
        if event.left_button:
            self._on_erase(event.image_pos.x, event.image_pos.y, r, False)  # continue stroke
        canvas.set_erase_highlight(event.image_pos.x, event.image_pos.y, r)

    def deactivate(self, canvas) -> None:
        canvas.clear_erase_highlight()
