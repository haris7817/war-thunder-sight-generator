# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: onedir, windowed Windows build of the sight generator.

Bundles template.blk (resolved at runtime via sys._MEIPASS) and the app icon, and
excludes heavy modules we never import (notably PySide6 WebEngine, which alone adds
hundreds of MB).
"""

datas = [
    ("app/blk/template.blk", "app/blk"),
    ("assets/icon.ico", "assets"),
]

excludes = [
    "matplotlib",
    "scipy",
    "tkinter",
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebEngineQuick",
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",
    "PySide6.QtQuick",
    "PySide6.QtQuick3D",
    "PySide6.QtQml",
    "PySide6.Qt3DCore",
    "PySide6.QtCharts",
    "PySide6.QtDataVisualization",
    "PySide6.QtPdf",
    "PySide6.QtNetwork",
    "PySide6.QtSql",
]

a = Analysis(
    ["app/main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="WarThunderSightGenerator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # windowed (no console window)
    icon="assets/icon.ico",
    version="version_info.txt",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="WarThunderSightGenerator",
)
