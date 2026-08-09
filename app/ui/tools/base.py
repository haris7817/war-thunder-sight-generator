"""Tool strategy interface.

A tool receives canvas mouse events already translated into image-space points, plus
a reference to the canvas for anything else it needs. Building this seam in M5 (while
only Select exists) is what keeps M7's draw/erase tools additive rather than a canvas
rewrite.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.geometry import Point


@dataclass(frozen=True, slots=True)
class ToolEvent:
    """A mouse event in both screen and image coordinate spaces."""

    image_pos: Point  # position in image pixels
    screen_x: float  # position in widget pixels
    screen_y: float
    left_button: bool = False


class Tool:
    """Base class for canvas tools. Subclasses override the handlers they need."""

    name: str = "tool"

    def on_press(self, canvas, event: ToolEvent) -> None:  # noqa: D401
        """Mouse press."""

    def on_move(self, canvas, event: ToolEvent) -> None:
        """Mouse move (with or without a button held)."""

    def on_release(self, canvas, event: ToolEvent) -> None:
        """Mouse release."""

    def cancel(self, canvas) -> None:
        """Abort any in-progress action (Esc / right-click)."""

    def deactivate(self, canvas) -> None:
        """Called when switching away from this tool; clear any transient canvas state."""
