"""Pure screen<->image coordinate mapping for the canvas (no Qt dependency).

The image is drawn centred in the widget, scaled by ``zoom`` and shifted by a pan
offset. Keeping this math Qt-free makes it unit-testable and keeps the round-trip
(screen -> image -> sight and back) verifiable without a display.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ViewTransform:
    zoom: float
    pan_x: float
    pan_y: float
    widget_w: float
    widget_h: float
    img_w: float
    img_h: float

    def image_to_screen(self, ix: float, iy: float) -> tuple[float, float]:
        sx = (ix - self.img_w / 2.0) * self.zoom + self.widget_w / 2.0 + self.pan_x
        sy = (iy - self.img_h / 2.0) * self.zoom + self.widget_h / 2.0 + self.pan_y
        return sx, sy

    def screen_to_image(self, sx: float, sy: float) -> tuple[float, float]:
        if self.zoom == 0:
            raise ValueError("zoom is zero")
        ix = (sx - self.widget_w / 2.0 - self.pan_x) / self.zoom + self.img_w / 2.0
        iy = (sy - self.widget_h / 2.0 - self.pan_y) / self.zoom + self.img_h / 2.0
        return ix, iy


def fit_zoom(widget_w: float, widget_h: float, img_w: float, img_h: float, margin: float = 0.9) -> float:
    """Zoom that fits the image within the widget with a small margin."""
    if img_w <= 0 or img_h <= 0:
        return 1.0
    return min(widget_w / img_w, widget_h / img_h) * margin
