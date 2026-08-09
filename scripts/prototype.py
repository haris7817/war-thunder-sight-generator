"""Headless CLI for the processing pipeline.

M3: load an image, preprocess, and write a thresholded binary preview (with
auto-detected background polarity). M4 will extend this with tracing, an overlay
PNG, and .blk emission.

Usage (M3):
    python scripts/prototype.py --in input.png --method otsu --preview artifacts/thr.png
    python scripts/prototype.py --in input.png --method global --threshold 140 --preview out.png
    python scripts/prototype.py --in input.png --method adaptive --preview out.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
from app.processing.import_service import ImageImportError, load_image
from app.processing.preprocess import preprocess
from app.processing.threshold import adaptive, global_threshold, otsu, should_invert


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Prototype image processing pipeline (headless).")
    p.add_argument("--in", dest="input", required=True, help="Input image (PNG/JPG).")
    p.add_argument(
        "--method",
        choices=["otsu", "global", "adaptive"],
        default="otsu",
        help="Threshold method.",
    )
    p.add_argument("--threshold", type=int, default=128, help="Level for --method global (0-255).")
    p.add_argument("--blur", type=int, default=0, help="Gaussian blur kernel (odd, 0 = off).")
    p.add_argument(
        "--invert",
        choices=["auto", "on", "off"],
        default="auto",
        help="Background polarity: auto-detect, force on (light subject/dark bg), or off.",
    )
    p.add_argument("--preview", default="artifacts/preview.png", help="Output binary PNG path.")
    # Reserved for M4 (tracing); accepted now so the interface is stable.
    p.add_argument("--preset", choices=["fast", "balanced", "high"], default="balanced")
    p.add_argument("--detail", type=int, default=60)
    p.add_argument("--out", help="Output .blk path (M4).")
    p.add_argument("--overlay", help="Output overlay PNG path (M4).")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        img = load_image(args.input)
    except ImageImportError as exc:
        print(f"[prototype] {exc}", file=sys.stderr)
        return 1

    gray = preprocess(img.rgb, blur_ksize=args.blur)

    if args.invert == "auto":
        invert = should_invert(gray)
    else:
        invert = args.invert == "on"

    if args.method == "otsu":
        binary = otsu(gray, invert=invert)
    elif args.method == "global":
        binary = global_threshold(gray, args.threshold, invert=invert)
    else:
        binary = adaptive(gray, invert=invert)

    preview_path = Path(args.preview)
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(preview_path), binary)

    fg = int((binary > 0).sum())
    total = binary.size
    print(f"[prototype] {img.width}x{img.height}  method={args.method}  invert={invert}")
    print(f"  foreground: {fg:,}/{total:,} px ({100 * fg / total:.1f}%)")
    print(f"  wrote preview: {preview_path}")
    if args.out or args.overlay:
        print("  note: tracing/.blk/overlay output arrives in M4", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
