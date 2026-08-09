"""Resource-path resolution for source and frozen (PyInstaller) runs (M8).

Getting sys._MEIPASS handling right is the #1 cause of "works in dev, crashes in the
.exe", so both modes are covered here.
"""

from __future__ import annotations

import sys

from app.blk.parser import load_default_template
from app.infrastructure import filesystem


def test_unfrozen_resource_root_is_project_root():
    root = filesystem.resource_root()
    assert (root / "app" / "blk" / "template.blk").is_file()


def test_unfrozen_template_loads():
    tmpl = load_default_template()
    assert "drawLines{" in tmpl.text and "drawQuads{" in tmpl.text


def test_frozen_resource_root_uses_meipass(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert filesystem.is_frozen() is True
    assert filesystem.resource_root() == tmp_path
    assert (
        filesystem.resource_path("app", "blk", "template.blk")
        == tmp_path / "app" / "blk" / "template.blk"
    )


def test_frozen_user_data_dir_is_beside_exe(monkeypatch, tmp_path):
    exe = tmp_path / "WarThunderSightGenerator.exe"
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(exe), raising=False)
    assert filesystem.user_data_dir() == exe.resolve().parent


def test_export_demo_cli_writes_valid_blk(tmp_path):
    from scripts.export_demo import main

    out = tmp_path / "cal.blk"
    rc = main(["--out", str(out)])
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert "drawLines{" in text
    assert text.count("{") == text.count("}")
    assert "e-" not in text and "nan" not in text.lower()
