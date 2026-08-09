"""Headless CLI for the processing pipeline (M3 threshold preview + M4 tracing).

Threshold preview only:
    python scripts/prototype.py --in input.png --method otsu --preview artifacts/thr.png

Full trace to overlay + .blk:
    python scripts/prototype.py --in input.png --preset balanced --detail 60 \
        --out artifacts/out.blk --overlay artifacts/out_trace.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from app.application.export_service import build_export
from app.application.tracing_service import TraceMode, trace
from app.blk.coordinate_mapper import CoordinateMapper
from app.domain.settings import TracePreset, TraceSettings
from app.domain.transform import ArtworkTransform
from app.processing.import_service import ImageImportError, load_image
from app.processing.preprocess import preprocess
from app.processing.threshold import adaptive, global_threshold, otsu, should_invert


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Prototype image processing pipeline (headless).")
    p.add_argument("--in", dest="input", required=True, help="Input image (PNG/JPG).")
    p.add_argument("--method", choices=["otsu", "global", "adaptive"], default="otsu")
    p.add_argument("--threshold", type=int, default=128, help="Level for --method global (0-255).")
    p.add_argument("--blur", type=int, default=0, help="Gaussian blur kernel (odd, 0 = off).")
    p.add_argument("--invert", choices=["auto", "on", "off"], default="auto")
    p.add_argument("--preview", help="Write a binary threshold preview PNG here.")
    p.add_argument("--mode", choices=["edge", "fill"], default="edge", help="Trace input map.")
    p.add_argument("--preset", choices=["fast", "balanced", "high"], default="balanced")
    p.add_argument("--detail", type=int, default=None, help="Override preset detail (0-100).")
    p.add_argument("--out", help="Output .blk path (triggers tracing).")
    p.add_argument("--overlay", help="Output trace-overlay PNG path (triggers tracing).")
    return p


def _resolve_invert(gray: np.ndarray, choice: str) -> bool:
    if choice == "auto":
        return should_invert(gray)
    return choice == "on"


def _write_preview(gray: np.ndarray, args, invert: bool) -> None:
    if args.method == "otsu":
        binary = otsu(gray, invert=invert)
    elif args.method == "global":
        binary = global_threshold(gray, args.threshold, invert=invert)
    else:
        binary = adaptive(gray, invert=invert)
    path = Path(args.preview)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), binary)
    print(f"  wrote preview: {path}")


def _write_overlay(rgb: np.ndarray, segments, path: str) -> None:
    """Draw traced segments (bright green) over a dimmed copy of the artwork."""
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    canvas = (bgr * 0.35).astype(np.uint8)  # dim the original so the trace pops
    for s in segments:
        cv2.line(
            canvas,
            (int(round(s.a.x)), int(round(s.a.y))),
            (int(round(s.b.x)), int(round(s.b.y))),
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), canvas)
    print(f"  wrote overlay: {out}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        img = load_image(args.input)
    except ImageImportError as exc:
        print(f"[prototype] {exc}", file=sys.stderr)
        return 1

    gray = preprocess(img.rgb, blur_ksize=args.blur)
    invert = _resolve_invert(gray, args.invert)
    print(f"[prototype] {img.width}x{img.height}  invert={invert}")

    if args.preview:
        _write_preview(gray, args, invert)

    if args.out or args.overlay:
        settings = TraceSettings.from_preset(TracePreset(args.preset))
        if args.detail is not None:
            settings = settings.with_detail(args.detail)
        inv = None if args.invert == "auto" else invert
        result = trace(img.rgb, settings, mode=TraceMode(args.mode), invert=inv)
        print(
            f"  trace: {result.contour_count} contours -> {result.segment_count} segments"
            f"  (mode={args.mode}, detail={settings.detail})"
        )
        for w in result.warnings:
            print(f"  warning: {w}")

        if args.overlay:
            _write_overlay(img.rgb, result.segments, args.overlay)

        if args.out:
            mapper = CoordinateMapper(image_width=img.width, image_height=img.height)
            export = build_export(
                list(result.segments), [], mapper, ArtworkTransform.identity()
            )
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(export.text, encoding="utf-8", newline="")
            print(f"  wrote .blk: {out}  ({export.line_count} lines)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
