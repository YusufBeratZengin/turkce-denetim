"""Temel veri yapilari, enum'lar ve model tanimlari."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    """Bulgu onem derecesi."""

    INFO = "info"
    WARN = "warn"
    ERROR = "error"

    @property
    def level(self) -> int:
        """Karsilastirma icin numerik seviye."""
        return {
            Severity.INFO: 1,
            Severity.WARN: 2,
            Severity.ERROR: 3,
        }[self]

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Severity):
            return NotImplemented
        return self.level >= other.level

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Severity):
            return NotImplemented
        return self.level > other.level

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Severity):
            return NotImplemented
        return self.level <= other.level

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Severity):
            return NotImplemented
        return self.level < other.level

    @classmethod
    def from_str(cls, value: str) -> Severity:
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError(f"Bilinmeyen onem derecesi: {value}. Gecerli: info, warn, error")


@dataclass(frozen=True)
class Finding:
    """Kural denetimi sonucu uretilen tek bir bulgu."""

    rule_id: str
    rule_name: str
    message: str
    severity: Severity
    line: int
    column: int
    end_line: int
    end_column: int
    suggestion: str | None = None
    context: str | None = None


@dataclass
class Sentence:
    """Metin icindeki tek bir cumle ve konum bilgisi."""

    text: str
    line: int
    column: int
    end_line: int
    end_column: int
    words: list[str] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        return len(self.words)


@dataclass
class Paragraph:
    """Metin icindeki tek bir paragraf ve icerdigi cumleler."""

    text: str
    line: int
    column: int
    end_line: int
    end_column: int
    sentences: list[Sentence] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        return sum(s.word_count for s in self.sentences)


@dataclass
class Document:
    """Denetlenecek metin belgesi ve yapisal parcalari."""

    raw_content: str
    clean_content: str
    path: str | None = None
    lines: list[str] = field(default_factory=list)
    clean_lines: list[str] = field(default_factory=list)
    paragraphs: list[Paragraph] = field(default_factory=list)
    sentences: list[Sentence] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        return sum(s.word_count for s in self.sentences)


@dataclass
class AnalysisResult:
    """Tek bir belgenin ya da tum taramanin denetim sonucu."""

    path: str | None
    findings: list[Finding]
    naturalness_score: float
    word_count: int
    sentence_count: int
    paragraph_count: int

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.ERROR)

    @property
    def warn_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.WARN)

    @property
    def info_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.INFO)
