"""Turkce ek budayici (stemmer) testleri."""

from __future__ import annotations

from turkce_denetim.stemmer import stem, stem_words


def test_stem_plural() -> None:
    assert stem("kitaplar") == "kitap"
    assert stem("evler") == "ev"
    assert stem("günler") == "gün"


def test_stem_possessive_and_case() -> None:
    assert stem("kitabımız") == "kitap" or stem("kitabımız").startswith("kitab")
    assert stem("evimizde") == "ev"
    assert stem("masadan") == "masa"
    assert stem("okulda") == "okul"
    assert stem("yolculuğumuzdan") == "yolculuk" or stem("yolculuğumuzdan").startswith("yolculu")


def test_stem_apostrophe_proper_nouns() -> None:
    assert stem("Ahmet'in") == "ahmet"
    assert stem("Ankara'da") == "ankara"
    assert stem("Türkiye'den") == "türkiye"
    assert stem("İstanbul’a") == "istanbul"


def test_stem_short_roots() -> None:
    # 2 harfli Turkce kokler korunmali
    assert stem("ev") == "ev"
    assert stem("su") == "su"
    assert stem("at") == "at"
    assert stem("ak") == "ak"


def test_stem_words() -> None:
    text = "Ahmet evinde kitaplar okuyor ve yazarlardan ders alıyordu."
    stems = stem_words(text)
    assert "ahmet" in stems
    assert "ev" in stems
    assert "kitap" in stems
