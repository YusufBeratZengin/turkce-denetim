"""Turkce buyuk/kucuk harf ve casefold testleri."""

from __future__ import annotations

from turkce_denetim.casing import (
    turkish_casefold,
    turkish_lower,
    turkish_title,
    turkish_upper,
)


def test_turkish_lower_i_and_dotless_i() -> None:
    # Standart str.lower() 'I' -> 'i' yaparken, turkce_lower 'I' -> 'ı' yapmali
    assert turkish_lower("IŞIK") == "ışık"
    assert turkish_lower("İSTANBUL") == "istanbul"
    assert turkish_lower("Irmak") == "ırmak"
    assert turkish_lower("İğne") == "iğne"
    assert turkish_lower("ÇIĞLIK") == "çığlık"


def test_turkish_upper_i_and_dotless_i() -> None:
    # Standart str.upper() 'ı' -> 'I', 'i' -> 'I' yapabiliyorken, turkce_upper 'i' -> 'İ' yapmali
    assert turkish_upper("ışık") == "IŞIK"
    assert turkish_upper("istanbul") == "İSTANBUL"
    assert turkish_upper("kitap") == "KİTAP"
    assert turkish_upper("ırmak") == "IRMAK"


def test_turkish_casefold() -> None:
    assert turkish_casefold("IŞIK") == "ışık"
    assert turkish_casefold("İSTANBUL") == "istanbul"
    assert turkish_casefold("Elbette!") == "elbette!"
    assert turkish_casefold("I") == "ı"
    assert turkish_casefold("İ") == "i"
    assert turkish_casefold("ı") == "ı"
    assert turkish_casefold("i") == "i"


def test_turkish_title() -> None:
    assert turkish_title("istanbul ve ışık") == "İstanbul Ve Işık"
    assert turkish_title("türkçe denetim aracı") == "Türkçe Denetim Aracı"
