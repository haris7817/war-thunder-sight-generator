"""The 56px vertical tool rail.

Holds tool buttons wired to :class:`Tool` strategy instances. M5 ships Select active;
Draw/Erase appear as disabled placeholders until M7, when they become live without a
rail rewrite (the strategy seam already exists).
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QToolButton, QVBoxLayout

from app.ui import theme
from app.ui.tools.base import Tool
from app.ui.tools.select_tool import SelectTool


class ToolRail(QFrame):
    """Vertical icon rail. Emits ``toolSelected(Tool)`` when the active tool changes."""

    toolSelected = Signal(object)

    def __init__(self, parent=None) -> None:
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

        self._add_tool("▶", SelectTool(), "Select", enabled=True, checked=True)
        self._add_placeholder("✎", "Draw line (M7)")
        self._add_placeholder("⌫", "Erase (M7)")

        layout.addStretch(1)
        self._group.buttonClicked.connect(self._on_clicked)

    def _add_tool(self, glyph: str, tool: Tool, tip: str, *, enabled: bool, checked: bool) -> None:
        btn = QToolButton()
        btn.setText(glyph)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setEnabled(enabled)
        btn.setToolTip(tip)
        btn.setFixedSize(40, 40)
        self._tools[btn] = tool
        self._group.addButton(btn)
        self.layout().addWidget(btn)

    def _add_placeholder(self, glyph: str, tip: str) -> None:
        btn = QToolButton()
        btn.setText(glyph)
        btn.setEnabled(False)
        btn.setToolTip(tip)
        btn.setFixedSize(40, 40)
        self.layout().addWidget(btn)

    def _on_clicked(self, btn: QToolButton) -> None:
        tool = self._tools.get(btn)
        if tool is not None:
            self.toolSelected.emit(tool)
