"""Dark theme: palette constants and a global stylesheet.

Colours match the approved design: near-black app chrome, slightly lighter panels,
a distinct canvas backdrop, one accent, and light text.
"""

from __future__ import annotations

# Palette
APP_BG = "#15181c"
PANEL_BG = "#1a1e23"
CANVAS_BG = "#22262b"
ACCENT = "#2f9ee6"
TEXT = "#dfe3e8"
TEXT_MUTED = "#8b9299"
BORDER = "#2b3037"
CONTROL_BG = "#262b31"
CONTROL_HOVER = "#2f363d"

# Layout metrics
RAIL_WIDTH = 56
PANEL_WIDTH = 296

STYLESHEET = f"""
QWidget {{
    background-color: {APP_BG};
    color: {TEXT};
    font-size: 13px;
}}
QLabel {{ background: transparent; }}
QLabel#muted {{ color: {TEXT_MUTED}; }}
QLabel#fieldLabel {{ color: {TEXT_MUTED}; font-size: 12px; }}
QLabel#value {{ color: {TEXT_MUTED}; }}

/* Secondary (default) buttons: Import, Re-trace, Reset */
QPushButton {{
    background-color: {CONTROL_BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    color: {TEXT};
}}
QPushButton:hover {{ background-color: {CONTROL_HOVER}; }}
QPushButton:pressed {{ background-color: {BORDER}; }}

/* Primary button: Export */
QPushButton#accent {{ background-color: {ACCENT}; color: #0b0d10; border: none; font-weight: 600; }}
QPushButton#accent:hover {{ background-color: #47abe9; }}

/* Chip toggle buttons */
QPushButton#chip {{
    background-color: {CONTROL_BG};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 5px 14px;
}}
QPushButton#chip:checked {{
    background-color: {ACCENT};
    color: #0b0d10;
    border: 1px solid {ACCENT};
}}

/* On/Off pill (Shading) */
QPushButton#pill {{ border: none; border-radius: 10px; padding: 2px 12px; font-size: 11px; font-weight: 700; }}
QPushButton#pill[on="true"] {{ background-color: {ACCENT}; color: #0b0d10; }}
QPushButton#pill[on="false"] {{ background-color: {CONTROL_BG}; color: {TEXT_MUTED}; }}

/* Clean section header (icon + title) — NOT the accent-blue of the tool rail */
QToolButton#sectionHeader {{
    background: transparent; border: none; color: {TEXT};
    font-weight: 600; font-size: 13px; padding: 2px 0;
}}
QToolButton#sectionHeader:hover {{ color: {TEXT}; background: transparent; }}
QToolButton#sectionHeader:checked {{ color: {TEXT}; background: transparent; }}

/* Combo box (template dropdown) */
QComboBox {{
    background-color: {CONTROL_BG}; border: 1px solid {BORDER};
    border-radius: 6px; padding: 6px 10px; color: {TEXT};
}}
QComboBox:hover {{ background-color: {CONTROL_HOVER}; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{
    background-color: {PANEL_BG}; color: {TEXT};
    selection-background-color: {ACCENT}; selection-color: #0b0d10;
}}

QDoubleSpinBox {{
    background-color: {CONTROL_BG}; border: 1px solid {BORDER};
    border-radius: 6px; padding: 4px 6px; color: {TEXT};
}}

QFrame#panel {{ background-color: {PANEL_BG}; border-left: 1px solid {BORDER}; }}
QFrame#rail {{ background-color: {PANEL_BG}; border-right: 1px solid {BORDER}; }}
QFrame#footer {{ background-color: {PANEL_BG}; border-top: 1px solid {BORDER}; }}
QFrame#hline {{ background-color: {BORDER}; max-height: 1px; }}

/* Tool-rail icon buttons — ONLY these get the accent-checked treatment */
QFrame#rail QToolButton {{
    background-color: transparent; border: none; border-radius: 8px;
    padding: 8px; color: {TEXT_MUTED};
}}
QFrame#rail QToolButton:hover {{ background-color: {CONTROL_HOVER}; color: {TEXT}; }}
QFrame#rail QToolButton:checked {{ background-color: {CONTROL_BG}; color: {ACCENT}; }}

QSlider::groove:horizontal {{
    height: 4px; background: {BORDER}; border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT}; width: 14px; margin: -6px 0; border-radius: 7px;
}}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }}

QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {TEXT_MUTED}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QStatusBar {{ background-color: {PANEL_BG}; color: {TEXT_MUTED}; border-top: 1px solid {BORDER}; }}
QStatusBar::item {{ border: none; }}
"""


def apply_theme(app) -> None:
    """Apply the global stylesheet to a QApplication."""
    app.setStyleSheet(STYLESHEET)
