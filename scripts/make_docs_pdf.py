"""Render the Markdown docs to PDF using Qt (no extra dependencies).

Usage (inside the venv):
    python scripts/make_docs_pdf.py

Produces docs/USER_GUIDE.pdf and docs/TROUBLESHOOTING.pdf.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QMarginsF
from PySide6.QtGui import (
    QFont,
    QGuiApplication,
    QPageLayout,
    QPageSize,
    QPdfWriter,
    QTextDocument,
)

ROOT = Path(__file__).resolve().parents[1]

_STYLE = """
h1 { font-size: 20pt; }
h2 { font-size: 14pt; }
h3 { font-size: 12pt; }
code, pre { font-family: 'Consolas', monospace; background-color: #f2f2f2; }
table, th, td { border: 1px solid #cccccc; padding: 4px; }
"""


def convert(md_path: Path, pdf_path: Path) -> None:
    md = md_path.read_text(encoding="utf-8")
    doc = QTextDocument()
    doc.setDefaultFont(QFont("Segoe UI", 10))
    doc.setDefaultStyleSheet(_STYLE)
    doc.setMarkdown(md)

    writer = QPdfWriter(str(pdf_path))
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(QMarginsF(16, 15, 16, 15), QPageLayout.Unit.Millimeter)
    doc.print_(writer)
    print(f"wrote {pdf_path}")


def main() -> int:
    QGuiApplication(sys.argv)
    docs = ROOT / "docs"
    convert(docs / "USER_GUIDE.md", docs / "USER_GUIDE.pdf")
    convert(docs / "TROUBLESHOOTING.md", docs / "TROUBLESHOOTING.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
