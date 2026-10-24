"""Unit tests for configuration parsing and validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from turkce_denetim.config import ConfigError, load_config_from_file


def test_load_valid_config(tmp_path: Path) -> None:
    cfg_file = tmp_path / "valid.toml"
    cfg_file.write_text(
        """
[tool.turkce-denetim]
min_severity = "warn"
disable = ["TD001", "TD002"]
max_sentence_words = 40
max_paragraph_words = 150
max_commas_per_sentence = 6
max_passive_per_sentence = 4
min_word_repetition = 4
""",
        encoding="utf-8",
    )
    config = load_config_from_file(cfg_file)
    assert config.min_severity.value == "warn"
    assert config.disable == ["TD001", "TD002"]
    assert config.max_sentence_words == 40
    assert config.max_paragraph_words == 150
    assert config.max_commas_per_sentence == 6
    assert config.max_passive_per_sentence == 4
    assert config.min_word_repetition == 4


def test_missing_config_file_raises_config_error() -> None:
    with pytest.raises(ConfigError) as exc_info:
        load_config_from_file("non_existent_file_abc.toml")
    assert "bulunamadı" in str(exc_info.value)


def test_unknown_key_raises_config_error(tmp_path: Path) -> None:
    cfg_file = tmp_path / "invalid_key.toml"
    cfg_file.write_text(
        """
[tool.turkce-denetim]
invalid_option = true
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError) as exc_info:
        load_config_from_file(cfg_file)
    assert "Bilinmeyen yapılandırma anahtarı" in str(exc_info.value)
    assert "invalid_option" in str(exc_info.value)


def test_wrong_type_min_severity_raises_config_error(tmp_path: Path) -> None:
    cfg_file = tmp_path / "bad_severity.toml"
    cfg_file.write_text(
        """
[tool.turkce-denetim]
min_severity = 123
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError) as exc_info:
        load_config_from_file(cfg_file)
    assert "min_severity" in str(exc_info.value)


def test_invalid_severity_value_raises_config_error(tmp_path: Path) -> None:
    cfg_file = tmp_path / "unknown_severity.toml"
    cfg_file.write_text(
        """
[tool.turkce-denetim]
min_severity = "critical"
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError) as exc_info:
        load_config_from_file(cfg_file)
    assert "critical" in str(exc_info.value)


def test_unknown_rule_id_in_disable_raises_config_error(tmp_path: Path) -> None:
    cfg_file = tmp_path / "unknown_rule.toml"
    cfg_file.write_text(
        """
[tool.turkce-denetim]
disable = ["TD001", "TD999"]
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError) as exc_info:
        load_config_from_file(cfg_file)
    assert "TD999" in str(exc_info.value)


def test_threshold_not_int_raises_config_error(tmp_path: Path) -> None:
    cfg_file = tmp_path / "bad_int.toml"
    cfg_file.write_text(
        """
[tool.turkce-denetim]
max_sentence_words = "fifty"
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError) as exc_info:
        load_config_from_file(cfg_file)
    assert "tam sayı" in str(exc_info.value)


def test_threshold_non_positive_raises_config_error(tmp_path: Path) -> None:
    cfg_file = tmp_path / "negative_int.toml"
    cfg_file.write_text(
        """
[tool.turkce-denetim]
max_sentence_words = -5
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError) as exc_info:
        load_config_from_file(cfg_file)
    assert "pozitif" in str(exc_info.value)


def test_malformed_toml_syntax_raises_config_error(tmp_path: Path) -> None:
    cfg_file = tmp_path / "malformed.toml"
    cfg_file.write_text("tool = { turkce-denetim = [unclosed", encoding="utf-8")
    with pytest.raises(ConfigError) as exc_info:
        load_config_from_file(cfg_file)
    assert "Geçersiz TOML sözdizimi" in str(exc_info.value)


def test_section_not_dict_raises_config_error(tmp_path: Path) -> None:
    cfg_file = tmp_path / "not_dict.toml"
    cfg_file.write_text(
        """
[tool]
turkce-denetim = "not-a-table"
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError) as exc_info:
        load_config_from_file(cfg_file)
    assert "bir tablo (dict) olmalıdır" in str(exc_info.value)


def test_disable_as_comma_separated_string(tmp_path: Path) -> None:
    cfg_file = tmp_path / "string_disable.toml"
    cfg_file.write_text(
        """
[tool.turkce-denetim]
disable = "TD001, TD002"
""",
        encoding="utf-8",
    )
    config = load_config_from_file(cfg_file)
    assert set(config.disable) == {"TD001", "TD002"}


def test_disable_with_non_string_items_raises_config_error(tmp_path: Path) -> None:
    cfg_file = tmp_path / "bad_items.toml"
    cfg_file.write_text(
        """
[tool.turkce-denetim]
disable = [123, 456]
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError) as exc_info:
        load_config_from_file(cfg_file)
    assert "metin olmalıdır" in str(exc_info.value)


def test_disable_with_wrong_type_raises_config_error(tmp_path: Path) -> None:
    cfg_file = tmp_path / "bad_type.toml"
    cfg_file.write_text(
        """
[tool.turkce-denetim]
disable = 123
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError) as exc_info:
        load_config_from_file(cfg_file)
    assert "liste veya virgülle ayrılmış" in str(exc_info.value)


def test_load_toml_multiline_and_comments(tmp_path: Path) -> None:
    cfg_file = tmp_path / "multiline.toml"
    cfg_file.write_text(
        """
# Baştaki yorum
[other.table]
ignored = 1

[tool.turkce-denetim]
min_severity = 'warn' # Satır sonu yorumu
disable = [
    "TD001",
    'TD002',
]
""",
        encoding="utf-8",
    )
    config = load_config_from_file(cfg_file)
    assert config.min_severity.value == "warn"
    assert config.disable == ["TD001", "TD002"]


@pytest.mark.parametrize("content", ["", "[tool.turkce-denetim]\n", "[other]\nx = 1\n"])
def test_missing_or_empty_table_uses_defaults(tmp_path: Path, content: str) -> None:
    from turkce_denetim.config import Config

    cfg_file = tmp_path / "empty.toml"
    cfg_file.write_text(content, encoding="utf-8")
    assert load_config_from_file(cfg_file) == Config()


def test_tool_section_not_dict_raises_config_error(tmp_path: Path) -> None:
    cfg_file = tmp_path / "bad_tool.toml"
    cfg_file.write_text('tool = "not-a-table"', encoding="utf-8")
    with pytest.raises(ConfigError, match=r"\[tool\].*bir tablo"):
        load_config_from_file(cfg_file)


def test_find_and_load_config_fallback(tmp_path: Path) -> None:
    from turkce_denetim.config import find_and_load_config

    empty_dir = tmp_path / "isolated"
    empty_dir.mkdir()
    # Mocking cwd/parent walk where no pyproject.toml exists
    cfg = find_and_load_config(start_dir=empty_dir)
    assert cfg is not None
    assert cfg.min_severity.value in ("info", "warn", "error")
