"""Format geometry into the exact War Thunder drawLines/drawQuads syntax.

The exporter operates on geometry that is already in **sight units** (mapping and
the artwork transform happen upstream in the export service). Output is written
verbatim, matching the WTDraw form exactly::

    line {line:p4=x1,y1,x2,y2;move:b=false;}
    quad {tl:p2=x1,y1;tr:p2=x2,y2;br:p2=x3,y3;bl:p2=x4,y4;}

Hard rules from the format research (a single violation makes the game silently
fail to load the whole file):

* fixed-decimal floats only — never scientific notation (``1e-05`` is fatal);
* no ``NaN``/``Infinity``;
* every quad must be convex (a triangle is a quad with two duplicated corners).
"""

from __future__ import annotations

import math

from app.domain.geometry import LineSegment, Point, Quad

FLOAT_DP = 6
LINE_INDENT = "  "


def format_number(value: float, dp: int = FLOAT_DP) -> str:
    """Fixed-decimal string with ``dp`` places, no scientific notation, no ``-0``.

    Raises on non-finite values, which would corrupt the whole sight file.
    """
    v = float(value)
    if not math.isfinite(v):
        raise ValueError(f"non-finite coordinate cannot be exported: {value!r}")
    r = round(v, dp)
    if r == 0.0:
        r = 0.0  # normalise -0.0 -> 0.0
    return f"{r:.{dp}f}"


def _fmt_point(p: Point) -> str:
    return f"{format_number(p.x)},{format_number(p.y)}"


def is_convex_quad(tl: Point, tr: Point, br: Point, bl: Point) -> bool:
    """True if the quad (order tl->tr->br->bl) is convex or a degenerate triangle.

    Convex means the cross products of successive edges never change sign. Zero
    cross products (collinear vertices, e.g. a triangle formed by duplicating two
    corners) are permitted; a mix of positive and negative signs is not.
    """
    pts = [tl, tr, br, bl]
    got_pos = False
    got_neg = False
    for i in range(4):
        ax, ay = pts[i].x, pts[i].y
        bx, by = pts[(i + 1) % 4].x, pts[(i + 1) % 4].y
        cx, cy = pts[(i + 2) % 4].x, pts[(i + 2) % 4].y
        cross = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        if cross > 0:
            got_pos = True
        elif cross < 0:
            got_neg = True
    return not (got_pos and got_neg)


def line_to_blk(seg: LineSegment) -> str:
    """Render one line element (coordinates already in sight units)."""
    a = _fmt_point(seg.a)
    b = _fmt_point(seg.b)
    return f"{LINE_INDENT}line {{line:p4={a},{b};move:b=false;}}"


def quad_to_blk(quad: Quad) -> str:
    """Render one quad element, asserting convexity first."""
    if not is_convex_quad(quad.tl, quad.tr, quad.br, quad.bl):
        raise ValueError(
            "refusing to export a non-convex quad "
            f"(tl={tuple(quad.tl)}, tr={tuple(quad.tr)}, "
            f"br={tuple(quad.br)}, bl={tuple(quad.bl)})"
        )
    return (
        f"{LINE_INDENT}quad {{"
        f"tl:p2={_fmt_point(quad.tl)};"
        f"tr:p2={_fmt_point(quad.tr)};"
        f"br:p2={_fmt_point(quad.br)};"
        f"bl:p2={_fmt_point(quad.bl)};}}"
    )


def build_lines_body(segments: list[LineSegment]) -> str:
    """Inner text for a drawLines block (leading + trailing newline included).

    Empty geometry yields ``"\\n"`` so the block renders as ``drawLines{\\n}``.
    """
    if not segments:
        return "\n"
    return "\n" + "\n".join(line_to_blk(s) for s in segments) + "\n"


def build_quads_body(quads: list[Quad]) -> str:
    """Inner text for a drawQuads block (leading + trailing newline included)."""
    if not quads:
        return "\n"
    return "\n" + "\n".join(quad_to_blk(q) for q in quads) + "\n"
