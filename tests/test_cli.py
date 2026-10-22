"""CLI komut satiri arayuzu testleri."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from turkce_denetim.cli import main


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "0.1.0" in captured.out


def test_cli_clean_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    clean_file = tmp_path / "dogal.md"
    clean_file.write_text("Sade ve temiz bir Türkçe metin yazdık.", encoding="utf-8")

    exit_code = main([str(clean_file), "--no-color"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Denetim Özeti" in captured.out
    assert "0 hata" in captured.out


def test_cli_error_file_exits_one(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    error_file = tmp_path / "hatali.md"
    # 'herşey' TD023 hata seviyesi (Severity.ERROR)
    error_file.write_text("Herşey burada yer alıyor.", encoding="utf-8")

    exit_code = main([str(error_file), "--no-color"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "TD023" in captured.out


def test_cli_format_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    file = tmp_path / "deneme.md"
    file.write_text("Bu noktada açıklama yapalım.", encoding="utf-8")

    exit_code = main([str(file), "--format", "json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "summary" in data
    assert "files" in data
    assert data["files"][0]["findings"][0]["rule_id"] == "TD002"


def test_cli_format_sarif(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    file = tmp_path / "deneme.md"
    file.write_text("Bu noktada açıklama yapalım.", encoding="utf-8")

    exit_code = main([str(file), "--format", "sarif"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["version"] == "2.1.0"
    assert len(data["runs"][0]["results"]) >= 1


def test_cli_disable_rule(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    file = tmp_path / "deneme.md"
    file.write_text("Bu noktada açıklama yapalım.", encoding="utf-8")

    # TD002 kuralini kapat
    exit_code = main([str(file), "--disable", "TD002", "--format", "json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data["files"][0]["findings"]) == 0


def test_cli_min_severity_filter(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    file = tmp_path / "deneme.md"
    # TD002 warn seviyesindedir. min-severity=error verildiginde raporlanmamali
    file.write_text("Bu noktada açıklama yapalım.", encoding="utf-8")

    exit_code = main([str(file), "--min-severity", "error", "--format", "json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data["files"][0]["findings"]) == 0


def test_cli_stdin_input(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO("Günün sonunda, karar verildi."))

    exit_code = main(["-", "--format", "json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["files"][0]["findings"][0]["rule_id"] == "TD003"


def test_cli_score_only(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    file = tmp_path / "temiz.md"
    file.write_text("Doğal ve akıcı bir cümle yazdık.", encoding="utf-8")

    exit_code = main([str(file), "--score-only"])
    assert exit_code == 0
    captured = capsys.readouterr()
    score = float(captured.out.strip())
    assert 90.0 <= score <= 100.0
