"""Denetim motoru (Linter Engine) ve dosya tarayici."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from turkce_denetim.config import Config
from turkce_denetim.document import parse_document
from turkce_denetim.models import AnalysisResult, Document, Finding
from turkce_denetim.rules.registry import create_rules
from turkce_denetim.scoring import calculate_naturalness_score

if TYPE_CHECKING:
    from turkce_denetim.rules.base import Rule

_EXCLUDED_DIRS = frozenset(
    [
        ".git",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "dist",
        "build",
        "__pycache__",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
    ]
)

_VALID_EXTENSIONS = frozenset([".md", ".txt", ".markdown"])


def run_linter(document: Document, rules: list[Rule]) -> AnalysisResult:
    """Tek bir belge uzerinde belirtilen kurallari calistirir ve bulgulari dondurur."""
    all_findings: list[Finding] = []

    for rule in rules:
        try:
            findings = rule.check(document)
            all_findings.extend(findings)
        except Exception:
            # Tek bir kuralin calismasi tum motoru durdurmamali
            continue

    # Bulgulari satir ve sutuna gore sirala
    all_findings.sort(key=lambda f: (f.line, f.column, f.rule_id))

    score = calculate_naturalness_score(document.word_count, all_findings)

    return AnalysisResult(
        path=document.path,
        findings=all_findings,
        naturalness_score=score,
        word_count=document.word_count,
        sentence_count=len(document.sentences),
        paragraph_count=len(document.paragraphs),
    )


def collect_target_files(targets: list[str | Path]) -> list[Path]:
    """Verilen dosya ve dizin hedeflerinden .md ve .txt dosyalarini toplar."""
    collected: list[Path] = []
    seen: set[Path] = set()

    for target in targets:
        p = Path(target).resolve()
        if not p.exists():
            continue

        if p.is_file():
            if p.suffix.lower() in _VALID_EXTENSIONS or p not in seen:
                collected.append(p)
                seen.add(p)
        elif p.is_dir():
            for item in p.rglob("*"):
                # Dislanan dizinleri atla
                if any(part in _EXCLUDED_DIRS for part in item.parts):
                    continue
                if item.is_file() and item.suffix.lower() in _VALID_EXTENSIONS:
                    if item not in seen:
                        collected.append(item)
                        seen.add(item)

    collected.sort()
    return collected


def analyze_paths(paths: list[Path], config: Config) -> list[AnalysisResult]:
    """Belirtilen dosyalari yapilandirma kurallarina gore denetler."""
    rules = create_rules(
        disabled=config.disable,
        min_severity=config.min_severity,
        max_sentence_words=config.max_sentence_words,
        max_paragraph_words=config.max_paragraph_words,
        max_commas=config.max_commas_per_sentence,
        min_word_repetition=config.min_word_repetition,
    )

    results: list[AnalysisResult] = []
    for file_path in paths:
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding="latin-1")
            except Exception:
                continue
        except Exception:
            continue

        doc = parse_document(content, path=str(file_path))
        result = run_linter(doc, rules)
        results.append(result)

    return results


def analyze_text(text: str, config: Config, path: str | None = None) -> AnalysisResult:
    """Dizge icerigini (orn: stdin) yapilandirma kurallarina gore denetler."""
    rules = create_rules(
        disabled=config.disable,
        min_severity=config.min_severity,
        max_sentence_words=config.max_sentence_words,
        max_paragraph_words=config.max_paragraph_words,
        max_commas=config.max_commas_per_sentence,
        min_word_repetition=config.min_word_repetition,
    )
    doc = parse_document(text, path=path)
    return run_linter(doc, rules)
