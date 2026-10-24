"""CLI output remains usable when Python starts with a legacy encoding."""

from __future__ import annotations

import os
import subprocess
import sysconfig
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("args", "returncode", "stream", "expected"),
    [
        (["--help"], 0, "stdout", "Türkçe"),
        (["--config", "missing.toml"], 2, "stderr", "Yapılandırma hatası"),
    ],
)
def test_cli_output_with_cp1252(
    tmp_path: Path, args: list[str], returncode: int, stream: str, expected: str
) -> None:
    executable = Path(sysconfig.get_path("scripts")) / (
        "turkce-denetim.exe" if os.name == "nt" else "turkce-denetim"
    )
    proc = subprocess.run(
        [str(executable), *args],
        cwd=tmp_path,
        env={**os.environ, "PYTHONUTF8": "0", "PYTHONIOENCODING": "cp1252"},
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )

    assert proc.returncode == returncode, proc.stderr
    assert expected in getattr(proc, stream)
    assert "Traceback" not in proc.stderr
