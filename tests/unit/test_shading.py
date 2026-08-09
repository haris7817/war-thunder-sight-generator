"""Tests for shading generation and its invariants (M7)."""

from __future__ import annotations

from app.application.export_service import build_export
from app.blk.coordinate_mapper import CoordinateMapper
from app.blk.exporter import is_convex_quad
from app.domain.settings import ShadingSettings
from app.domain.transform import ArtworkTransform
from app.processing.shading import generate_shading

from tests.fixtures import synthetic


def test_intensity_zero_returns_nothing():
    quads, hatch = generate_shading(synthetic.filled_circle(200), ShadingSettings(intensity=0))
    assert quads == []
    assert hatch == []


def test_intensity_zero_export_has_no_quads():
    quads, _ = generate_shading(synthetic.filled_circle(200), ShadingSettings(intensity=0))
    mapper = CoordinateMapper(200, 200)
    export = build_export([], list(quads), mapper, ArtworkTransform.identity())
    assert "quad {" not in export.text  # drawQuads block is empty


def test_interior_dark_region_produces_fill():
    # A black circle on white (interior, not touching border) should fill.
    quads, _ = generate_shading(
        synthetic.filled_circle(300), ShadingSettings(intensity=80, hatch=False)
    )
    assert len(quads) >= 1


def test_generated_quads_are_convex_and_nondegenerate():
    quads, _ = generate_shading(
        synthetic.filled_circle(300), ShadingSettings(intensity=80, hatch=False)
    )
    for q in quads:
        assert is_convex_quad(q.tl, q.tr, q.br, q.bl)
        # non-degenerate: the four corners are not all identical
        xs = {round(p.x, 3) for p in q.vertices}
        ys = {round(p.y, 3) for p in q.vertices}
        assert len(xs) > 1 and len(ys) > 1


def test_dark_background_not_flooded():
    # Light circle on black background: the black bg touches the border and must be
    # excluded, so we don't get one giant fill covering the whole image.
    quads, _ = generate_shading(
        synthetic.light_on_dark(300), ShadingSettings(intensity=90, hatch=False)
    )
    # Any fill must be far smaller than the whole frame.
    for q in quads:
        w = max(p.x for p in q.vertices) - min(p.x for p in q.vertices)
        h = max(p.y for p in q.vertices) - min(p.y for p in q.vertices)
        assert w < 290 or h < 290


def test_hatch_density_increases_with_intensity():
    img = synthetic.gradient(256)
    low = generate_shading(img, ShadingSettings(intensity=25, hatch=True))[1]
    high = generate_shading(img, ShadingSettings(intensity=85, hatch=True))[1]
    assert len(high) > len(low)
