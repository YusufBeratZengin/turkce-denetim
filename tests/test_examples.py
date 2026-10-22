"""Golden tests for example files."""

from __future__ import annotations

from pathlib import Path

import pytest

from turkce_denetim.cli import main


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
