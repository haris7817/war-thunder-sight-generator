"""Pure screen<->image<->sight coordinate round-trip tests (M5, no Qt)."""

from __future__ import annotations

import pytest
from app.blk.coordinate_mapper import CoordinateMapper
from app.ui.view_transform import ViewTransform, fit_zoom

VT = ViewTransform(
    zoom=1.5, pan_x=10.0, pan_y=-5.0, widget_w=800.0, widget_h=600.0, img_w=400.0, img_h=300.0
)


@pytest.mark.parametrize("pt", [(0.0, 0.0), (400.0, 300.0), (123.0, 45.0), (399.0, 1.0)])
def test_screen_image_round_trip(pt):
    sx, sy = VT.image_to_screen(*pt)
    rx, ry = VT.screen_to_image(sx, sy)
    assert (rx, ry) == pytest.approx(pt)


def test_image_centre_maps_to_widget_centre_at_zero_pan():
    vt = ViewTransform(1.0, 0.0, 0.0, 800.0, 600.0, 400.0, 300.0)
    sx, sy = vt.image_to_screen(200.0, 150.0)  # image centre
    assert (sx, sy) == pytest.approx((400.0, 300.0))  # widget centre


def test_screen_to_image_to_sight_round_trip():
    # screen -> image (view) -> sight (mapper) -> image -> screen should return start.
    mapper = CoordinateMapper(image_width=400, image_height=300)
    screen = (321.0, 210.0)
    ix, iy = VT.screen_to_image(*screen)
    sight = mapper.to_sight(ix, iy)
    back_ix, back_iy = mapper.from_sight(*sight)
    back_screen = VT.image_to_screen(back_ix, back_iy)
    assert back_screen == pytest.approx(screen)


def test_fit_zoom_fits_within_widget():
    z = fit_zoom(800, 600, 400, 300, margin=1.0)
    assert 400 * z <= 800 + 1e-6
    assert 300 * z <= 600 + 1e-6
