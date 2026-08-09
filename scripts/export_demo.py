"""Emit a calibration .blk (crosshair + known-coordinate square + one filled quad).

M1: argparse stub. M2 implements the real emission to ``artifacts/calibration.blk``
— the file sent to the client to confirm coordinates land where predicted and to
resolve the aspect-ratio unknown.

Usage (M2):
    python scripts/export_demo.py --out artifacts/calibration.blk
"""

from __future__ import annotations

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Emit a calibration sight .blk.")
    p.add_argument(
        "--out",
        default="artifacts/calibration.blk",
        help="Output .blk path.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(f"[export_demo] not yet implemented (M2). Would write: {args.out}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
