"""Okunabilirlik ve metin akisi kurallari (TD017 - TD020, TD025)."""

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
    """TD017: Asiri uzun cumle esigi."""

    id = "TD017"
    name = "cumle-uzunlugu"
    description = "Cumlenin asiri uzun olmasi (varsayilan esik: 35 kelime)."
    severity = Severity.WARN
    suggestion = "Cumleyi iki veya daha fazla bagimsiz cumleye bolerek okunabilirligi artirin."

    def __init__(self, max_words: int = 35) -> None:
        self.max_words = max_words

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for sentence in document.sentences:
            if sentence.word_count > self.max_words:
                findings.append(
                    self.create_finding(
                        message=f"Cumle asiri uzun ({sentence.word_count} kelime; onerilen en fazla {self.max_words}).",
                        line=sentence.line,
                        column=sentence.column,
                        end_line=sentence.end_line,
                        end_column=sentence.end_column,
                        context=sentence.text[:80] + ("..." if len(sentence.text) > 80 else ""),
                    )
                )
        return findings


class ParagrafUzunluguRule(Rule):
    """TD018: Asiri uzun paragraf esigi."""

    id = "TD018"
    name = "paragraf-uzunlugu"
    description = "Paragrafin asiri uzun olmasi (varsayilan esik: 120 kelime)."
    severity = Severity.INFO
    suggestion = "Paragrafi alt dusunce bloklarina veya alt basliklara bolun."

    def __init__(self, max_words: int = 120) -> None:
        self.max_words = max_words

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for paragraph in document.paragraphs:
            if paragraph.word_count > self.max_words:
                findings.append(
                    self.create_finding(
                        message=f"Paragraf asiri uzun ({paragraph.word_count} kelime; onerilen en fazla {self.max_words}).",
                        line=paragraph.line,
                        column=paragraph.column,
                        end_line=paragraph.end_line,
                        end_column=paragraph.end_column,
                        context=paragraph.text[:80] + ("..." if len(paragraph.text) > 80 else ""),
                    )
                )
        return findings


class YakinKelimeTekrariRule(Rule):
    """TD019: Ayni koklu kelimenin kisa araliklarla tekrari."""

    id = "TD019"
    name = "yakin-kelime-tekrari"
    description = "Ayni cumlede ayni kokten tureyen kelimenin 3 veya daha fazla kez tekrarlanmasi."
    severity = Severity.WARN
    suggestion = "Tekrarlayan kelimeler yerine zamir veya esanlamli sozcukler kullanin."

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
                            message=f"'{root}' koku ayni cumle icinde {count} kez tekrarlandi.",
                            line=sentence.line,
                            column=sentence.column,
                            end_line=sentence.end_line,
                            end_column=sentence.end_column,
                            context=sentence.text,
                        )
                    )
        return findings


class VirgulZinciriRule(Rule):
    """TD020: Tek bir cumlede asiri virgul zincirlenmesi."""

    id = "TD020"
    name = "virgul-zinciri"
    description = "Tek cumlede 5 veya daha fazla virgul bulunmasi (virgul zinciri)."
    severity = Severity.INFO
    suggestion = "Cumleyi bolun ya da noktali virgul / maddeleme duzenini tercih edin."

    def __init__(self, max_commas: int = 5) -> None:
        self.max_commas = max_commas

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for sentence in document.sentences:
            comma_count = sentence.text.count(",")
            if comma_count >= self.max_commas:
                findings.append(
                    self.create_finding(
                        message=f"Cumlede {comma_count} virgul kullanilmis; takibi zorlastirabilir.",
                        line=sentence.line,
                        column=sentence.column,
                        end_line=sentence.end_line,
                        end_column=sentence.end_column,
                        context=sentence.text,
                    )
                )
        return findings


class VeyaBaglacTekrariRule(Rule):
    """TD025: Tek cumlede 've / veya' baglaclarinin asiri tekrari."""

    id = "TD025"
    name = "veya-baglac-tekrari"
    description = "Tek cumlede 3 veya daha fazla baglac ('ve', 'veya', 'ya da') yigilmasi."
    severity = Severity.INFO
    suggestion = "Baglac yigilmasi yerine virgullu siralama yapin veya cumleyi bolun."

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
                        message=f"Cumlede {conjunction_count} baglac ('ve/veya') yigilmasi tespit edildi.",
                        line=sentence.line,
                        column=sentence.column,
                        end_line=sentence.end_line,
                        end_column=sentence.end_column,
                        context=sentence.text,
                    )
                )
        return findings
