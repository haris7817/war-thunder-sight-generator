"""Report structure of a War Thunder .blk sight file.

Run this FIRST (before writing/trusting the exporter) against the client reference
sights to validate the coordinate assumptions against real data:

    python scripts/analyze_blk.py client_samples/Remielle/reference.blk
    python scripts/analyze_blk.py "E:/Downloads/Faye_Spike_left.txt"

Reports: file size, drawLines/drawQuads block presence, line:p4 count, quad count,
and the min/max X/Y bounding box across all drawn geometry. The bounding box tells
us the coordinate range the game actually uses (expected: within roughly +/-1.0 for
units_per_image_height = 1.0, positive Y downward, no Y-flip).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# line:p4=x1,y1,x2,y2   (optionally with spaces around '=' and commas)
_LINE_RE = re.compile(r"line\s*:\s*p4\s*=\s*([-\d.eE,\s]+?)\s*;")
# a p2 tuple: <name>:p2 = x,y
_P2_RE = re.compile(r"p2\s*=\s*(-?[\d.eE]+)\s*,\s*(-?[\d.eE]+)")
_QUAD_RE = re.compile(r"\bquad\s*\{")


def _floats(text: str) -> list[float]:
    out: list[float] = []
    for tok in text.split(","):
        tok = tok.strip()
        if tok:
            out.append(float(tok))
    return out


def extract_block_body(text: str, keyword: str) -> str:
    """Return the body inside a top-level ``keyword{ ... }`` block via brace scan.

    Header fields like ``crosshairHorVertSize:p2=3,2`` live OUTSIDE the draw blocks
    and must not pollute the geometry bounding box, so we scope extraction to the
    matched braces. Returns "" if the block is absent.
    """
    idx = text.find(keyword)
    if idx == -1:
        return ""
    brace = text.find("{", idx)
    if brace == -1:
        return ""
    depth = 0
    for i in range(brace, len(text)):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[brace + 1 : i]
    return text[brace + 1 :]  # unbalanced; return remainder


def analyze(text: str) -> dict:
    """Extract structural stats and the coordinate bounding box from BLK text.

    Geometry is read only from within the drawLines/drawQuads blocks so header p2
    fields do not skew the bounding box.
    """
    xs: list[float] = []
    ys: list[float] = []

    lines_body = extract_block_body(text, "drawLines")
    quads_body = extract_block_body(text, "drawQuads")

    line_count = 0
    for m in _LINE_RE.finditer(lines_body):
        vals = _floats(m.group(1))
        if len(vals) == 4:
            line_count += 1
            xs.extend([vals[0], vals[2]])
            ys.extend([vals[1], vals[3]])

    quad_count = len(_QUAD_RE.findall(quads_body))
    for mx, my in _P2_RE.findall(quads_body):
        xs.append(float(mx))
        ys.append(float(my))

    bbox = None
    if xs and ys:
        bbox = {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_y": min(ys),
            "max_y": max(ys),
        }

    return {
        "has_draw_lines": "drawLines{" in text.replace(" ", ""),
        "has_draw_quads": "drawQuads{" in text.replace(" ", ""),
        "line_count": line_count,
        "quad_count": quad_count,
        "coord_points": len(xs),
        "bbox": bbox,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Analyze a War Thunder .blk sight file.")
    p.add_argument("blk", help="Path to a .blk (or .txt) sight file.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.blk)
    if not path.is_file():
        print(f"[analyze_blk] not a file: {path}", file=sys.stderr)
        return 1

    data = path.read_text(encoding="utf-8", errors="replace")
    stats = analyze(data)

    size_kb = path.stat().st_size / 1024
    print(f"File:        {path}")
    print(f"Size:        {size_kb:,.1f} KB")
    print(f"drawLines:   {'yes' if stats['has_draw_lines'] else 'NO'}")
    print(f"drawQuads:   {'yes' if stats['has_draw_quads'] else 'NO'}")
    print(f"line:p4:     {stats['line_count']:,}")
    print(f"quad:        {stats['quad_count']:,}")
    print(f"elements:    {stats['line_count'] + stats['quad_count']:,}")
    bbox = stats["bbox"]
    if bbox:
        print(
            "bbox X:      "
            f"[{bbox['min_x']:.4f}, {bbox['max_x']:.4f}]  "
            f"(width {bbox['max_x'] - bbox['min_x']:.4f})"
        )
        print(
            "bbox Y:      "
            f"[{bbox['min_y']:.4f}, {bbox['max_y']:.4f}]  "
            f"(height {bbox['max_y'] - bbox['min_y']:.4f})"
        )
    else:
        print("bbox:        (no coordinates found)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
