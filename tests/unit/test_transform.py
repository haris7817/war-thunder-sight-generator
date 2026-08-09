"""Unit tests for the affine ArtworkTransform (M2)."""

from __future__ import annotations

import math

import pytest
from app.domain.transform import ArtworkTransform


def test_identity_apply():
    t = ArtworkTransform.identity()
    assert t.apply(3.0, 4.0) == (3.0, 4.0)


def test_offset_only():
    t = ArtworkTransform(offset_x=2.0, offset_y=-1.0)
    assert t.apply(3.0, 4.0) == pytest.approx((5.0, 3.0))


def test_uniform_scale():
    t = ArtworkTransform(scale=2.0)
    assert t.apply(3.0, 4.0) == pytest.approx((6.0, 8.0))


def test_rotation_90_degrees():
    t = ArtworkTransform(rotation_deg=90.0)
    # (1,0) -> (0,1) under +90 (CCW in the y-up sense).
    assert t.apply(1.0, 0.0) == pytest.approx((0.0, 1.0), abs=1e-9)
    assert t.apply(0.0, 1.0) == pytest.approx((-1.0, 0.0), abs=1e-9)


def test_rotation_45_degrees():
    t = ArtworkTransform(rotation_deg=45.0)
    r = math.sqrt(2) / 2
    assert t.apply(1.0, 0.0) == pytest.approx((r, r))


def test_composition_order_scale_rotate_translate():
    # scale x2, rotate 90, translate (10, 0): (1,0) -> scale (2,0) -> rot (0,2) -> +off (10,2)
    t = ArtworkTransform(offset_x=10.0, offset_y=0.0, scale=2.0, rotation_deg=90.0)
    assert t.apply(1.0, 0.0) == pytest.approx((10.0, 2.0), abs=1e-9)


def test_to_matrix_coefficients():
    t = ArtworkTransform(offset_x=5.0, offset_y=-3.0, scale=2.0, rotation_deg=0.0)
    a, b, c, d, tx, ty = t.to_matrix()
    assert (a, b, c, d, tx, ty) == pytest.approx((2.0, 0.0, 0.0, 2.0, 5.0, -3.0))


@pytest.mark.parametrize(
    "t",
    [
        ArtworkTransform.identity(),
        ArtworkTransform(offset_x=1.5, offset_y=-2.5),
        ArtworkTransform(scale=3.0),
        ArtworkTransform(rotation_deg=30.0),
        ArtworkTransform(offset_x=-0.4, offset_y=0.7, scale=1.8, rotation_deg=57.0),
    ],
)
@pytest.mark.parametrize("point", [(0.0, 0.0), (1.0, 0.0), (-0.3, 0.9), (2.5, -4.1)])
def test_inverse_round_trips(t, point):
    x, y = point
    fx, fy = t.apply(x, y)
    rx, ry = t.apply_inverse(fx, fy)
    assert (rx, ry) == pytest.approx((x, y), abs=1e-9)


def test_inverse_of_zero_scale_raises():
    with pytest.raises(ValueError):
        ArtworkTransform(scale=0.0).inverse()
