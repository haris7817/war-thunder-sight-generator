"""A row of mutually-exclusive 'chip' toggle buttons."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QPushButton,
    QWidget,
)


class ChipGroup(QWidget):
    """Exclusive toggle chips. Emits ``selectionChanged(key)`` with the chosen key.

    Constructed from ``[(key, label), ...]``; the first chip is selected by default.
    """

    selectionChanged = Signal(str)

    def __init__(self, options: list[tuple[str, str]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._keys: dict[QPushButton, str] = {}

        for i, (key, label) in enumerate(options):
            btn = QPushButton(label)
            btn.setObjectName("chip")
            btn.setCheckable(True)
            if i == 0:
                btn.setChecked(True)
            self._keys[btn] = key
            self._group.addButton(btn)
            layout.addWidget(btn)
        layout.addStretch(1)

        self._group.buttonClicked.connect(self._on_clicked)

    def _on_clicked(self, btn: QPushButton) -> None:
        self.selectionChanged.emit(self._keys[btn])

    def selected(self) -> str:
        btn = self._group.checkedButton()
        return self._keys.get(btn, "")
