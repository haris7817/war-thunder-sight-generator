"""Headless CLI: image -> threshold/trace preview + .blk (no GUI).

M1: argparse stub. M3 adds thresholding previews; M4 adds tracing, overlay PNG, and
.blk emission.

Usage (M4):
    python scripts/prototype.py --in input.png --preset balanced --detail 60 \
        --out artifacts/out.blk --overlay artifacts/out_trace.png
"""

from __future__ import annotations

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Prototype image tracing pipeline (headless).")
    p.add_argument("--in", dest="input", required=True, help="Input image (PNG/JPG).")
    p.add_argument(
        "--method",
        choices=["otsu", "global", "adaptive"],
        default="otsu",
        help="Threshold method (M3).",
    )
    p.add_argument(
        "--preset",
        choices=["fast", "balanced", "high"],
        default="balanced",
        help="Trace preset (M4).",
    )
    p.add_argument("--detail", type=int, default=60, help="Detail 0-100 (M4).")
    p.add_argument("--out", help="Output .blk path (M4).")
    p.add_argument("--overlay", help="Output overlay PNG path (M4).")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(f"[prototype] not yet implemented (M3/M4). Input: {args.input}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
