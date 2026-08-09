"""Select tool — the default. In M5 it is a no-op placeholder that establishes the
tool interface; canvas panning/zoom is handled by the canvas itself. M7 adds real
selection behaviour alongside draw/erase tools.
"""

from __future__ import annotations

from app.ui.tools.base import Tool


class SelectTool(Tool):
    name = "select"
