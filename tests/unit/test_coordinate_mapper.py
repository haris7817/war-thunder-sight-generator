"""Unit tests for image-pixel -> sight-unit mapping (M2)."""

from __future__ import annotations

import pytest
from app.blk.coordinate_mapper import CoordinateMapper, MappingConfig
from app.domain.transform import ArtworkTransform

# 100 wide x 200 tall, units_per_image_height = 1.0 -> scale = 1/200 = 0.005.
MAPPER = CoordinateMapper(image_width=100, image_height=200)


def test_centre_maps_to_origin():
    assert MAPPER.to_sight(50, 100) == pytest.approx((0.0, 0.0))


def test_top_row_maps_to_negative_y():
    # Y-direction regression: the image TOP (py=0) must map to NEGATIVE Y (up).
    _, sy = MAPPER.to_sight(50, 0)
    assert sy < 0
    assert sy == pytest.approx(-0.5)


def test_bottom_row_maps_to_positive_y():
    _, sy = MAPPER.to_sight(50, 200)
    assert sy == pytest.approx(0.5)


def test_four_corners():
    assert MAPPER.to_sight(0, 0) == pytest.approx((-0.25, -0.5))
    assert MAPPER.to_sight(100, 0) == pytest.approx((0.25, -0.5))
    assert MAPPER.to_sight(100, 200) == pytest.approx((0.25, 0.5))
    assert MAPPER.to_sight(0, 200) == pytest.approx((-0.25, 0.5))


def test_isotropic_uses_height_for_both_axes():
    # Full image width spans 100 px -> 100 * (1/200) = 0.5 units, i.e. -0.25..0.25.
    left_x, _ = MAPPER.to_sight(0, 100)
    right_x, _ = MAPPER.to_sight(100, 100)
    assert right_x - left_x == pytest.approx(0.5)


def test_from_sight_inverts_to_sight():
    for px, py in [(0, 0), (50, 100), (100, 200), (37, 189)]:
        sx, sy = MAPPER.to_sight(px, py)
        rx, ry = MAPPER.from_sight(sx, sy)
        assert (rx, ry) == pytest.approx((px, py))


def test_flip_y_config_inverts_direction():
    flipped = CoordinateMapper(
        image_width=100, image_height=200, config=MappingConfig(flip_y=True)
    )
    _, sy = flipped.to_sight(50, 0)
    assert sy > 0  # with flip, the top row now maps to positive Y


def test_units_per_image_height_scales_output():
    m2 = CoordinateMapper(
        image_width=100, image_height=200, config=MappingConfig(units_per_image_height=2.0)
    )
    # Doubling units_per_image_height doubles the sight extent.
    assert m2.to_sight(0, 0) == pytest.approx((-0.5, -1.0))


def test_to_sight_transformed_applies_offset():
    t = ArtworkTransform(offset_x=1.0, offset_y=2.0)
    # Centre maps to origin, then offset shifts it.
    assert MAPPER.to_sight_transformed(50, 100, t) == pytest.approx((1.0, 2.0))
