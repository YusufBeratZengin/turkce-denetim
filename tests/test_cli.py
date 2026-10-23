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


def test_cli_fixtures() -> None:
    fixtures_dir = Path(__file__).parent / "fixtures"
    clean_path = fixtures_dir / "clean.md"
    dirty_path = fixtures_dir / "dirty.md"

    assert clean_path.exists(), "clean.md fixture must exist"
    assert dirty_path.exists(), "dirty.md fixture must exist"

    # clean.md has 0 findings and must exit with 0
    assert main([str(clean_path), "--no-color"]) == 0

    # dirty.md has error-level findings and must exit with 1
    assert main([str(dirty_path), "--no-color"]) == 1


def test_cli_list_rules(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["--list-rules"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "TD001" in captured.out
    assert "ile-birlikte-asiri" in captured.out
    assert "TD025" in captured.out
    lines = [ln for ln in captured.out.strip().splitlines() if ln.startswith("TD")]
    assert len(lines) == 25


def test_cli_malformed_config_unknown_key(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cfg = tmp_path / "bad.toml"
    cfg.write_text('[tool.turkce-denetim]\nunknown_key = "invalid"\n', encoding="utf-8")

    exit_code = main(["--config", str(cfg)])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Yapılandırma hatası" in captured.err
    assert "unknown_key" in captured.err
    assert "Traceback" not in captured.err


def test_cli_malformed_config_wrong_type(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cfg = tmp_path / "bad_type.toml"
    cfg.write_text('[tool.turkce-denetim]\nmax_sentence_words = "thirty"\n', encoding="utf-8")

    exit_code = main(["--config", str(cfg)])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Yapılandırma hatası" in captured.err
    assert "tam sayı" in captured.err
    assert "Traceback" not in captured.err


def test_cli_malformed_config_unknown_rule_id_in_disable(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cfg = tmp_path / "bad_rule.toml"
    cfg.write_text('[tool.turkce-denetim]\ndisable = ["TD999"]\n', encoding="utf-8")

    exit_code = main(["--config", str(cfg)])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Yapılandırma hatası" in captured.err
    assert "TD999" in captured.err
    assert "Traceback" not in captured.err


def test_cli_unknown_rule_id_in_cli_disable(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["--disable", "TD999"])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Yapılandırma hatası" in captured.err
    assert "TD999" in captured.err
    assert "Traceback" not in captured.err


def test_cli_missing_config_file(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["--config", "non_existent_path_xyz.toml"])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Yapılandırma hatası" in captured.err
    assert "bulunamadı" in captured.err
    assert "Traceback" not in captured.err


def test_cli_no_targets_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    exit_code = main([str(empty_dir), "--format", "json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["files"] == []


def test_cli_no_targets_sarif(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    exit_code = main([str(empty_dir), "--format", "sarif"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["version"] == "2.1.0"


def test_cli_no_targets_text(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    exit_code = main([str(empty_dir)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Uyarı: Denetlenecek geçerli" in captured.err
