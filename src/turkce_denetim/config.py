"""Yapılandırma modeli ve pyproject.toml / özel dosya yükleyicisi."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from turkce_denetim.models import Severity


@dataclass
class Config:
    """turkce-denetim çalışma yapılandırması."""

    min_severity: Severity = Severity.INFO
    disable: list[str] = field(default_factory=list)
    max_sentence_words: int = 35
    max_paragraph_words: int = 120
    max_commas_per_sentence: int = 5
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
        return Config()

    content = p.read_text(encoding="utf-8")
    table_data: dict[str, Any] = {}

    if sys.version_info >= (3, 11):
        import tomllib

        try:
            raw_data = tomllib.loads(content)
            tool_section = raw_data.get("tool", {})
            table_data = tool_section.get("turkce-denetim", {})
        except Exception:
            table_data = _parse_simple_toml_table(content, "tool.turkce-denetim")
    else:
        table_data = _parse_simple_toml_table(content, "tool.turkce-denetim")

    min_sev = Severity.INFO
    if "min_severity" in table_data:
        try:
            min_sev = Severity.from_str(str(table_data["min_severity"]))
        except ValueError:
            min_sev = Severity.INFO

    disable_list: list[str] = []
    if "disable" in table_data:
        val = table_data["disable"]
        if isinstance(val, list):
            disable_list = [str(x).strip().upper() for x in val]
        elif isinstance(val, str):
            disable_list = [x.strip().upper() for x in val.split(",") if x.strip()]

    return Config(
        min_severity=min_sev,
        disable=disable_list,
        max_sentence_words=int(table_data.get("max_sentence_words", 35)),
        max_paragraph_words=int(table_data.get("max_paragraph_words", 120)),
        max_commas_per_sentence=int(table_data.get("max_commas_per_sentence", 5)),
        min_word_repetition=int(table_data.get("min_word_repetition", 3)),
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
