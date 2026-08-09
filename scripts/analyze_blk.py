"""Report structure of a War Thunder .blk sight file.

M1: argparse stub. M2 implements the real analysis (file size, line:p4 count, quad
count, min/max X/Y bounding box) — run FIRST against the client reference sights to
validate the coordinate assumptions against real data.

Usage:
    python scripts/analyze_blk.py client_samples/Remielle/reference.blk
"""

from __future__ import annotations

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Analyze a War Thunder .blk sight file.")
    p.add_argument("blk", help="Path to a .blk (or .txt) sight file.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(f"[analyze_blk] not yet implemented (M2). Target: {args.blk}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
