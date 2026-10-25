"""Golden tests for example files."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from turkce_denetim.cli import main
from turkce_denetim.config import load_config_from_file
from turkce_denetim.models import Severity


def test_examples_bad_matches_golden_output(capsys: pytest.CaptureFixture[str]) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    bad_md = repo_root / "examples" / "bad.md"
    expected_file = repo_root / "examples" / "bad.expected.txt"

    assert bad_md.exists(), "examples/bad.md must exist"
    assert expected_file.exists(), "examples/bad.expected.txt must exist"

    exit_code = main([str(bad_md), "--no-color"])
    assert exit_code == 1, "bad.md contains error-level finding (TD023) and must exit 1"

    captured = capsys.readouterr()
    actual = captured.out.replace("\r\n", "\n").strip()
    expected = expected_file.read_text(encoding="utf-8").replace("\r\n", "\n").strip()

    assert actual == expected, "CLI output on examples/bad.md must match examples/bad.expected.txt"


def test_examples_good_is_clean(capsys: pytest.CaptureFixture[str]) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    good_md = repo_root / "examples" / "good.md"

    assert good_md.exists(), "examples/good.md must exist"

    exit_code = main([str(good_md), "--no-color"])
    assert exit_code == 0, "good.md must exit 0"

    captured = capsys.readouterr()
    assert "0 hata, 0 uyarı, 0 bilgi (toplam 0)" in captured.out
    assert "100.0 / 100" in captured.out


def test_readme_contains_real_examples_output() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    expected = (
        (repo_root / "examples" / "bad.expected.txt")
        .read_text(encoding="utf-8")
        .replace("\r\n", "\n")
        .strip()
    )

    for readme_name in ("README.md", "README.tr.md"):
        content = (repo_root / readme_name).read_text(encoding="utf-8").replace("\r\n", "\n")
        assert expected in content, (
            f"{readme_name} must contain the real output from examples/bad.expected.txt"
        )


def test_examples_api_usage_runs_successfully() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    script = repo_root / "examples" / "api_usage.py"
    assert script.exists(), "examples/api_usage.py must exist"

    src_dir = repo_root / "src"
    proc = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONPATH": str(src_dir), "PYTHONIOENCODING": "utf-8"},
        timeout=15,
        check=False,
    )
    assert proc.returncode == 0, f"api_usage.py failed with: {proc.stderr}"
    assert "Toplam sözcük sayısı" in proc.stdout
    assert "Doğallık puanı" in proc.stdout
    assert "TD008" in proc.stdout
    assert "turkish_lower" in proc.stdout


def test_examples_custom_config_is_valid() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    cfg_file = repo_root / "examples" / "custom_config.toml"
    assert cfg_file.exists(), "examples/custom_config.toml must exist"

    cfg = load_config_from_file(cfg_file)
    assert cfg.min_severity == Severity.WARN
    assert "TD001" in cfg.disable
    assert "TD014" in cfg.disable
    assert cfg.max_sentence_words == 35
    assert cfg.max_paragraph_words == 120
    assert cfg.max_commas_per_sentence == 5
    assert cfg.max_passive_per_sentence == 3
    assert cfg.min_word_repetition == 3


def test_examples_readme_is_clean(capsys: pytest.CaptureFixture[str]) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    readme_md = repo_root / "examples" / "README.md"
    assert readme_md.exists(), "examples/README.md must exist"

    exit_code = main([str(readme_md), "--no-color"])
    assert exit_code == 0, "examples/README.md must exit 0"

    captured = capsys.readouterr()
    assert "0 hata, 0 uyarı, 0 bilgi (toplam 0)" in captured.out
    assert "100.0 / 100" in captured.out


def test_examples_pre_commit_config_exists() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    yaml_file = repo_root / "examples" / "pre-commit-config.yaml"
    assert yaml_file.exists(), "examples/pre-commit-config.yaml must exist"

    content = yaml_file.read_text(encoding="utf-8")
    assert "id: turkce-denetim" in content
    assert "YusufBeratZengin/turkce-denetim" in content
