"""Filesystem and bundled-resource path resolution.

The ``resource_path`` helper is ``sys._MEIPASS``-aware so that bundled assets
(``template.blk``, QSS, icon) load both when running from source and from a frozen
PyInstaller build. Getting this wrong is the #1 cause of "works in dev, crashes in
the .exe" — it is implemented once, here, in M1.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    """True when running inside a PyInstaller (or similar) bundle."""
    return getattr(sys, "frozen", False)


def resource_root() -> Path:
    """Base directory for read-only bundled resources.

    - Frozen: PyInstaller extracts data files under ``sys._MEIPASS``.
    - Source: the project root (parent of the ``app`` package).
    """
    if is_frozen():
        base = getattr(sys, "_MEIPASS", None)
        if base:
            return Path(base)
    # app/infrastructure/filesystem.py -> project root is two parents up from app/.
    return Path(__file__).resolve().parents[2]


def resource_path(*parts: str) -> Path:
    """Resolve a path to a bundled resource, relative to :func:`resource_root`."""
    return resource_root().joinpath(*parts)


def user_data_dir() -> Path:
    """Writable per-user directory for logs and settings.

    Beside the executable when frozen (portable), else the project root in dev.
    """
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def ensure_dir(path: Path) -> Path:
    """Create ``path`` (and parents) if missing; return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Write text to ``path`` atomically via a temp file + ``os.replace``.

    Avoids leaving a half-written .blk if the process dies mid-write. Newlines are
    written verbatim (``newline=""``) so the strict LF-terminated BLK format is
    preserved regardless of platform.
    """
    ensure_dir(path.parent)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding=encoding, newline="") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
