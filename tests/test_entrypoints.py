"""python -m calistirma ve dosya toplama davranislari."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from turkce_denetim.config import Config
from turkce_denetim.engine import analyze_paths, collect_target_files

SRC = Path(__file__).resolve().parents[1] / "src"


def test_python_dash_m_runs_cli() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "turkce_denetim", "--version"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(SRC)},
        check=False,
    )
    assert proc.returncode == 0
    assert "turkce-denetim" in proc.stdout


def test_parent_directory_named_build_is_not_excluded(tmp_path: Path) -> None:
    project = tmp_path / "build" / "proje"
    project.mkdir(parents=True)
    (project / "yazi.md").write_text("Sade bir cümle.", encoding="utf-8")
    assert [p.name for p in collect_target_files([str(project)])] == ["yazi.md"]


def test_excluded_directory_inside_target_is_skipped(tmp_path: Path) -> None:
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "a.md").write_text("x", encoding="utf-8")
    (tmp_path / "b.md").write_text("y", encoding="utf-8")
    assert [p.name for p in collect_target_files([str(tmp_path)])] == ["b.md"]


def test_cp1254_file_is_decoded_as_turkish(tmp_path: Path) -> None:
    f = tmp_path / "eski.txt"
    f.write_bytes("Herşey çok güzel, şöyle ğüşıö.".encode("cp1254"))
    result = analyze_paths([f], Config())[0]
    assert any(x.rule_id == "TD023" for x in result.findings)
