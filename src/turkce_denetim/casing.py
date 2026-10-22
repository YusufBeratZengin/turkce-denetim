"""Türkçe büyük/küçük harf dönüşümleri (I/ı, İ/i) ve casefold yardımcıları."""

from __future__ import annotations

import unicodedata

# Turkce harf eslesmeleri
_LOWER_MAP = {
    ord("I"): "ı",
    ord("İ"): "i",
}

_UPPER_MAP = {
    ord("ı"): "I",
    ord("i"): "İ",
}


def turkish_lower(text: str) -> str:
    """Türkçe kurallarına uygun küçük harfe dönüştürme.

    'I' harfini 'ı' yapar, 'İ' harfini 'i' yapar. Standart str.lower() 'I' harfini
    'i' yaptığı için Türkçede hatalı karşılaştırmalara yol acar.
    """
    normalized = unicodedata.normalize("NFC", text)
    # Translate I and İ first
    translated = normalized.translate(_LOWER_MAP)
    return translated.lower()


def turkish_upper(text: str) -> str:
    """Türkçe kurallarına uygun büyük harfe dönüştürme.

    'ı' harfini 'I' yapar, 'i' harfini 'İ' yapar.
    """
    normalized = unicodedata.normalize("NFC", text)
    translated = normalized.translate(_UPPER_MAP)
    return translated.upper()


def turkish_casefold(text: str) -> str:
    """Türkçe harf duyarsız karşılaştırma (casefold).

    Türkçe 'I'/'ı' ve 'İ'/'i' ayrımını koruyarak metni küçük harfe ve casefold biçimine çevirir.
    """
    normalized = unicodedata.normalize("NFC", text)
    # Once Turkce buyuk I ve İ'yi kucuk karsiliklarina cevir
    translated = normalized.translate(_LOWER_MAP)
    return translated.casefold()


def turkish_title(text: str) -> str:
    """Türkçe kurallarına uygun başlık düzeni (Title Case)."""
    words = text.split(" ")
    titled_words: list[str] = []
    for word in words:
        if not word:
            titled_words.append("")
            continue
        first_char = word[0]
        rest = word[1:]
        titled_words.append(turkish_upper(first_char) + turkish_lower(rest))
    return " ".join(titled_words)
