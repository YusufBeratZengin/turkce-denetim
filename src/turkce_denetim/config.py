"""Yapılandırma modeli ve pyproject.toml / özel dosya yükleyicisi."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from turkce_denetim.models import Severity


class ConfigError(ValueError):
    """Yapılandırma hatası (geçersiz tür, bilinmeyen anahtar veya kural)."""

    pass


_VALID_CONFIG_KEYS = frozenset(
    [
        "min_severity",
        "disable",
        "max_sentence_words",
        "max_paragraph_words",
        "max_commas_per_sentence",
        "max_passive_per_sentence",
        "min_word_repetition",
    ]
)


def _get_valid_rule_ids() -> frozenset[str]:
    from turkce_denetim.rules.registry import ALL_RULES

    return frozenset(rule_cls.id for rule_cls in ALL_RULES)


@dataclass
class Config:
    """turkce-denetim çalışma yapılandırması."""

    min_severity: Severity = Severity.INFO
    disable: list[str] = field(default_factory=list)
    max_sentence_words: int = 35
    max_paragraph_words: int = 120
    max_commas_per_sentence: int = 5
    max_passive_per_sentence: int = 3
    min_word_repetition: int = 3

    def __post_init__(self) -> None:
        # Kutuphane kullanicisi Config(min_severity="warn") yazabilir; metni Severity'ye cevir.
        if not isinstance(self.min_severity, Severity):
            self.min_severity = Severity.from_str(str(self.min_severity))


def _parse_simple_toml_table(content: str, table_name: str) -> dict[str, Any]:
    """Python 3.10 için stdlib harici bağımlılık olmadan basit toml tablosu ayrıştırıcı."""
    data: dict[str, Any] = {}
    lines = content.splitlines()
    in_target = False

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("[") and stripped.endswith("]"):
            header = stripped[1:-1].strip()
            in_target = header == table_name
            continue

        if not in_target:
            continue

        if "=" in stripped:
            key, val = stripped.split("=", 1)
            key = key.strip()
            val = val.strip()

            # Array
            if val.startswith("[") and val.endswith("]"):
                items_str = val[1:-1].strip()
                if not items_str:
                    data[key] = []
                else:
                    raw_items = [i.strip().strip("\"'") for i in items_str.split(",") if i.strip()]
                    data[key] = raw_items
            elif val.startswith('"') and val.endswith('"'):
                data[key] = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                data[key] = val[1:-1]
            elif val.lower() in ("true", "false"):
                data[key] = val.lower() == "true"
            elif re.match(r"^-?\d+$", val):
                data[key] = int(val)
            elif re.match(r"^-?\d+\.\d+$", val):
                data[key] = float(val)
            else:
                data[key] = val

    return data


def load_config_from_file(config_path: Path | str) -> Config:
    """Belirtilen TOML dosyasından [tool.turkce-denetim] ayarlarını yükler."""
    p = Path(config_path)
    if not p.is_file():
        raise ConfigError(f"Yapılandırma dosyası bulunamadı: {config_path}")

    content = p.read_text(encoding="utf-8")
    table_data: dict[str, Any] = {}

    if sys.version_info >= (3, 11):
        import tomllib

        try:
            raw_data = tomllib.loads(content)
        except Exception as err:
            raise ConfigError(f"Geçersiz TOML sözdizimi: {err}") from err

        tool_section = raw_data.get("tool", {})
        if "turkce-denetim" in tool_section:
            table_data = tool_section["turkce-denetim"]
            if not isinstance(table_data, dict):
                raise ConfigError("[tool.turkce-denetim] bir tablo (dict) olmalıdır.")
    else:
        table_data = _parse_simple_toml_table(content, "tool.turkce-denetim")

    min_sev = Severity.INFO
    disable_list: list[str] = []
    max_sentence_words = 35
    max_paragraph_words = 120
    max_commas_per_sentence = 5
    min_word_repetition = 3

    if table_data:
        # 1. Bilinmeyen anahtarlar
        unknown_keys = sorted(set(table_data.keys()) - _VALID_CONFIG_KEYS)
        if unknown_keys:
            raise ConfigError(
                f"Bilinmeyen yapılandırma anahtarı: {', '.join(unknown_keys)}. "
                f"Geçerli anahtarlar: {', '.join(sorted(_VALID_CONFIG_KEYS))}"
            )

        # 2. min_severity
        if "min_severity" in table_data:
            val = table_data["min_severity"]
            if not isinstance(val, str):
                raise ConfigError(
                    f"'min_severity' metin (string) olmalıdır, {type(val).__name__} verildi."
                )
            try:
                min_sev = Severity.from_str(val)
            except ValueError as err:
                raise ConfigError(str(err)) from err

        # 3. disable
        if "disable" in table_data:
            val = table_data["disable"]
            if isinstance(val, list):
                for item in val:
                    if not isinstance(item, str):
                        raise ConfigError(
                            f"'disable' listesindeki öğeler metin olmalıdır, {type(item).__name__} verildi."
                        )
                disable_list = [str(x).strip().upper() for x in val]
            elif isinstance(val, str):
                disable_list = [x.strip().upper() for x in val.split(",") if x.strip()]
            else:
                raise ConfigError(
                    f"'disable' liste veya virgülle ayrılmış metin olmalıdır, {type(val).__name__} verildi."
                )

            valid_ids = _get_valid_rule_ids()
            unknown_rules = sorted(set(disable_list) - valid_ids)
            if unknown_rules:
                raise ConfigError(f"Bilinmeyen kural kimliği: {', '.join(unknown_rules)}")

        # 4. Tam sayı eşik değerleri
        threshold_map = {
            "max_sentence_words": 35,
            "max_paragraph_words": 120,
            "max_commas_per_sentence": 5,
            "max_passive_per_sentence": 3,
            "min_word_repetition": 3,
        }
        for key in threshold_map:
            if key in table_data:
                v = table_data[key]
                if isinstance(v, bool) or not isinstance(v, int):
                    raise ConfigError(
                        f"'{key}' bir tam sayı (integer) olmalıdır, {type(v).__name__} verildi."
                    )
                if v <= 0:
                    raise ConfigError(f"'{key}' pozitif bir tam sayı olmalıdır: {v}")

        max_sentence_words = int(table_data.get("max_sentence_words", 35))
        max_paragraph_words = int(table_data.get("max_paragraph_words", 120))
        max_commas_per_sentence = int(table_data.get("max_commas_per_sentence", 5))
        max_passive_per_sentence = int(table_data.get("max_passive_per_sentence", 3))
        min_word_repetition = int(table_data.get("min_word_repetition", 3))

    return Config(
        min_severity=min_sev,
        disable=disable_list,
        max_sentence_words=max_sentence_words,
        max_paragraph_words=max_paragraph_words,
        max_commas_per_sentence=max_commas_per_sentence,
        max_passive_per_sentence=max_passive_per_sentence,
        min_word_repetition=min_word_repetition,
    )


def find_and_load_config(start_dir: Path | str | None = None) -> Config:
    """Çalışma dizininden başlayarak pyproject.toml dosyasını arar ve yapılandırmayı yükler."""
    current = Path(start_dir or Path.cwd()).resolve()

    # Mevcut veya ust dizinlerde pyproject.toml ara
    for parent in [current, *current.parents]:
        pyproject = parent / "pyproject.toml"
        if pyproject.is_file():
            return load_config_from_file(pyproject)

    return Config()
