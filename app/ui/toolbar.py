"""The 56px vertical tool rail.

Built from a list of (glyph, tool, tooltip) so the owner (main window) supplies the
live tools. The strategy seam was created in M5; M7 simply passes real Draw/Erase
tools here — no rail rewrite.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QToolButton, QVBoxLayout

from app.ui import theme
from app.ui.tools.base import Tool


class ToolRail(QFrame):
    """Vertical icon rail. Emits ``toolSelected(Tool)`` when the active tool changes."""

    toolSelected = Signal(object)

    def __init__(self, tools: list[tuple[str, Tool, str]], parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("rail")
        self.setFixedWidth(theme.RAIL_WIDTH)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._tools: dict[QToolButton, Tool] = {}

        for i, (glyph, tool, tip) in enumerate(tools):
            btn = QToolButton()
            btn.setText(glyph)
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.setToolTip(tip)
            btn.setFixedSize(40, 40)
            self._tools[btn] = tool
            self._group.addButton(btn)
            layout.addWidget(btn)

        layout.addStretch(1)
        self._group.buttonClicked.connect(self._on_clicked)

    def _on_clicked(self, btn: QToolButton) -> None:
        tool = self._tools.get(btn)
        if tool is not None:
            self.toolSelected.emit(tool)
