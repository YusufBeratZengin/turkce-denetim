"""Okunabilirlik ve metin akışı kuralları (TD017 - TD020, TD025)."""

from __future__ import annotations

from collections import Counter

from turkce_denetim.casing import turkish_casefold
from turkce_denetim.models import Document, Finding, Severity
from turkce_denetim.rules.base import Rule
from turkce_denetim.stemmer import stem

_STOP_WORDS = frozenset(
    [
        "ve",
        "ile",
        "de",
        "da",
        "te",
        "ta",
        "ki",
        "bir",
        "bu",
        "şu",
        "o",
        "için",
        "daha",
        "en",
        "çok",
        "kadar",
        "gibi",
        "ile",
        "veya",
        "ya",
        "hem",
        "ne",
        "ise",
        "diye",
        "olarak",
        "olan",
        "olanlar",
        "böyle",
        "şöyle",
        "nasıl",
        "neden",
        "her",
        "tüm",
        "bütün",
        "bazı",
        "ise",
    ]
)


class CumleUzunluguRule(Rule):
    """TD017: Aşırı uzun cümle eşiği."""

    id = "TD017"
    name = "cümle-uzunluğu"
    description = "Cümlenin aşırı uzun olması (varsayılan eşik: 35 kelime)."
    severity = Severity.WARN
    suggestion = "Cümleyi iki veya daha fazla bağımsız cümleye bölerek okunabilirliği artırın."

    def __init__(self, max_words: int = 35) -> None:
        self.max_words = max_words

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for sentence in document.sentences:
            if sentence.word_count > self.max_words:
                findings.append(
                    self.create_finding(
                        message=f"Cümle aşırı uzun ({sentence.word_count} kelime; önerilen en fazla {self.max_words}).",
                        line=sentence.line,
                        column=sentence.column,
                        end_line=sentence.end_line,
                        end_column=sentence.end_column,
                        context=sentence.text[:80] + ("..." if len(sentence.text) > 80 else ""),
                    )
                )
        return findings


class ParagrafUzunluguRule(Rule):
    """TD018: Aşırı uzun paragraf eşiği."""

    id = "TD018"
    name = "paragraf-uzunluğu"
    description = "Paragrafın aşırı uzun olması (varsayılan eşik: 120 kelime)."
    severity = Severity.INFO
    suggestion = "Paragrafı alt düşünce bloklarına veya alt başlıklara bölün."

    def __init__(self, max_words: int = 120) -> None:
        self.max_words = max_words

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for paragraph in document.paragraphs:
            if paragraph.word_count > self.max_words:
                findings.append(
                    self.create_finding(
                        message=f"Paragraf aşırı uzun ({paragraph.word_count} kelime; önerilen en fazla {self.max_words}).",
                        line=paragraph.line,
                        column=paragraph.column,
                        end_line=paragraph.end_line,
                        end_column=paragraph.end_column,
                        context=paragraph.text[:80] + ("..." if len(paragraph.text) > 80 else ""),
                    )
                )
        return findings


class YakinKelimeTekrariRule(Rule):
    """TD019: Aynı köklü kelimenin kısa aralıklarla tekrarı."""

    id = "TD019"
    name = "yakın-kelime-tekrarı"
    description = "Aynı cümlede aynı kökten türeyen kelimenin 3 veya daha fazla kez tekrarlanması."
    severity = Severity.WARN
    suggestion = "Tekrarlayan kelimeler yerine zamir veya eşanlamlı sözcükler kullanın."

    def __init__(self, min_repetition: int = 3) -> None:
        self.min_repetition = min_repetition

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for sentence in document.sentences:
            stems: list[str] = []
            for w in sentence.words:
                cf = turkish_casefold(w)
                if cf in _STOP_WORDS or len(cf) < 3:
                    continue
                st = stem(w)
                if st and st not in _STOP_WORDS and len(st) >= 3:
                    stems.append(st)

            counts = Counter(stems)
            for root, count in counts.items():
                if count >= self.min_repetition:
                    findings.append(
                        self.create_finding(
                            message=f"'{root}' kökü aynı cümle içinde {count} kez tekrarlandı.",
                            line=sentence.line,
                            column=sentence.column,
                            end_line=sentence.end_line,
                            end_column=sentence.end_column,
                            context=sentence.text,
                        )
                    )
        return findings


class VirgulZinciriRule(Rule):
    """TD020: Tek bir cümlede aşırı virgül zincirlenmesi."""

    id = "TD020"
    name = "virgül-zinciri"
    description = "Tek cümlede 5 veya daha fazla virgül bulunması (virgül zinciri)."
    severity = Severity.INFO
    suggestion = "Cümleyi bölün ya da noktalı virgül / maddeleme düzenini tercih edin."

    def __init__(self, max_commas: int = 5) -> None:
        self.max_commas = max_commas

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for sentence in document.sentences:
            comma_count = sentence.text.count(",")
            if comma_count >= self.max_commas:
                findings.append(
                    self.create_finding(
                        message=f"Cümlede {comma_count} virgül kullanılmış; takibi zorlaştırabilir.",
                        line=sentence.line,
                        column=sentence.column,
                        end_line=sentence.end_line,
                        end_column=sentence.end_column,
                        context=sentence.text,
                    )
                )
        return findings


class VeyaBaglacTekrariRule(Rule):
    """TD025: Tek cümlede 've / veya' bağlaçlarının aşırı tekrarı."""

    id = "TD025"
    name = "veya-bağlaç-tekrarı"
    description = "Tek cümlede 3 veya daha fazla bağlaç ('ve', 'veya', 'ya da') yığılması."
    severity = Severity.INFO
    suggestion = "Bağlaç yığılması yerine virgüllü sıralama yapın veya cümleyi bölün."

    def __init__(self, max_conjunctions: int = 3) -> None:
        self.max_conjunctions = max_conjunctions

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for sentence in document.sentences:
            lower_words = [turkish_casefold(w) for w in sentence.words]
            conjunction_count = sum(1 for w in lower_words if w in ("ve", "veya", "yahut"))
            if conjunction_count >= self.max_conjunctions:
                findings.append(
                    self.create_finding(
                        message=f"Cümlede {conjunction_count} bağlaç ('ve/veya') yığılması tespit edildi.",
                        line=sentence.line,
                        column=sentence.column,
                        end_line=sentence.end_line,
                        end_column=sentence.end_column,
                        context=sentence.text,
                    )
                )
        return findings
