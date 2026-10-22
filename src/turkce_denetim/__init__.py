"""turkce-denetim: Türkçe metinlerde yapay zekâ ve çeviri kokusu kalıplarını tespit eden kurallı linter."""

from __future__ import annotations

from turkce_denetim.casing import (
    turkish_casefold,
    turkish_lower,
    turkish_title,
    turkish_upper,
)
from turkce_denetim.config import Config, ConfigError
from turkce_denetim.document import parse_document
from turkce_denetim.engine import analyze_paths, analyze_text, run_linter
from turkce_denetim.models import AnalysisResult, Document, Finding, Paragraph, Sentence, Severity
from turkce_denetim.scoring import calculate_naturalness_score, get_naturalness_rating
from turkce_denetim.stemmer import stem, stem_words

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "turkish_lower",
    "turkish_upper",
    "turkish_casefold",
    "turkish_title",
    "stem",
    "stem_words",
    "Document",
    "Sentence",
    "Paragraph",
    "Finding",
    "Severity",
    "AnalysisResult",
    "Config",
    "ConfigError",
    "parse_document",
    "run_linter",
    "analyze_text",
    "analyze_paths",
    "calculate_naturalness_score",
    "get_naturalness_rating",
]
