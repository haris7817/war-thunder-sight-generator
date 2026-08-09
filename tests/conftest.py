"""Shared test config: force Qt's offscreen platform so GUI tests run headless."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
