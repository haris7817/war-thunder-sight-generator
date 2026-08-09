"""Build the standalone Windows executable (PyInstaller onedir) from app.spec.

Usage (from the project root, inside the venv):
    python scripts/build_windows.py

Output: dist/WarThunderSightGenerator/WarThunderSightGenerator.exe (+ its runtime
files). Zip that folder for delivery. Requires the dev extras (`pip install -e .[dev]`).
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPEC = PROJECT_ROOT / "app.spec"


def main() -> int:
    try:
        import PyInstaller.__main__ as pyi
    except ImportError:
        print("PyInstaller is not installed. Run: pip install -e .[dev]", file=sys.stderr)
        return 1

    # Clean previous outputs for a reproducible build.
    for d in ("build", "dist"):
        target = PROJECT_ROOT / d
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)

    print(f"Building from {SPEC} ...")
    pyi.run(["--noconfirm", "--clean", str(SPEC)])

    exe = PROJECT_ROOT / "dist" / "WarThunderSightGenerator" / "WarThunderSightGenerator.exe"
    if exe.exists():
        print(f"\nBuild complete: {exe}")
        print("Zip the folder dist/WarThunderSightGenerator for delivery.")
        return 0
    print("\nBuild finished but the expected .exe was not found.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
