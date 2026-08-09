"""Emit a calibration .blk to validate coordinates/orientation in-game.

The geometry is authored directly in SIGHT UNITS (no image mapping) so the client's
feedback validates the coordinate convention itself. The layout is intentionally
asymmetric so a flip or mirror is obvious:

    * an "up" marker line from the origin toward NEGATIVE Y  -> should point UP
    * a "right" marker line from the origin toward POSITIVE X -> should point RIGHT
    * a 0.2 x 0.2 outline square centred on the origin (corners at +/-0.1)
    * one filled quad in the TOP-RIGHT quadrant (x>0, y<0)

Usage:
    python scripts/export_demo.py --out artifacts/calibration.blk
"""

from __future__ import annotations

import argparse

from app.application.export_service import render_and_write_sight
from app.domain.geometry import GeometrySource, LineSegment, Point, Quad


def calibration_geometry() -> tuple[list[LineSegment], list[Quad]]:
    def seg(x1: float, y1: float, x2: float, y2: float) -> LineSegment:
        return LineSegment(Point(x1, y1), Point(x2, y2), source=GeometrySource.MANUAL)

    lines = [
        # Origin markers (asymmetric: up + right only).
        seg(0.0, 0.0, 0.0, -0.30),  # up (negative Y)
        seg(0.0, 0.0, 0.30, 0.0),  # right (positive X)
        # Outline square centred on origin, corners at +/-0.1.
        seg(-0.10, -0.10, 0.10, -0.10),  # top edge
        seg(0.10, -0.10, 0.10, 0.10),  # right edge
        seg(0.10, 0.10, -0.10, 0.10),  # bottom edge
        seg(-0.10, 0.10, -0.10, -0.10),  # left edge
    ]
    quads = [
        # Filled square in the TOP-RIGHT quadrant (x>0 = right, y<0 = up).
        Quad(
            Point(0.14, -0.20),
            Point(0.20, -0.20),
            Point(0.20, -0.14),
            Point(0.14, -0.14),
            source=GeometrySource.MANUAL_FILL,
        )
    ]
    return lines, quads


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Emit a calibration sight .blk.")
    p.add_argument("--out", default="artifacts/calibration.blk", help="Output .blk path.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    lines, quads = calibration_geometry()
    result, path = render_and_write_sight(lines, quads, args.out)
    print(f"[export_demo] wrote {path}")
    print(f"  lines: {result.line_count}  quads: {result.quad_count}")
    for w in result.warnings:
        print(f"  warning: {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
