"""Okunabilirlik kurallari testleri (TD017 - TD020, TD025)."""

from __future__ import annotations

from turkce_denetim.document import parse_document
from turkce_denetim.rules.readability import (
    CumleUzunluguRule,
    ParagrafUzunluguRule,
    VeyaBaglacTekrariRule,
    VirgulZinciriRule,
    YakinKelimeTekrariRule,
)


def test_td017_cumle_uzunlugu() -> None:
    rule = CumleUzunluguRule(max_words=10)
    # 12 kelimelik cumle -> yakalamali
    doc_pos = parse_document(
        "Bu birinci ikinci üçüncü dördüncü beşinci altıncı yedinci sekizinci dokuzuncu onuncu onbirinci cümledir."
    )
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD017"

    # Kisa cumle -> yakalamamali
    doc_neg = parse_document("Kısa ve net bir cümle kurduk.")
    assert len(rule.check(doc_neg)) == 0


def test_td018_paragraf_uzunlugu() -> None:
    rule = ParagrafUzunluguRule(max_words=15)
    doc_pos = parse_document(
        "Bu paragraf bilerek çok uzun tutuldu çünkü test kapsamında belirli bir eşiği aşması ve kuralın çalışması hedeflendi."
    )
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD018"

    doc_neg = parse_document("Bu kısa bir paragraftır.")
    assert len(rule.check(doc_neg)) == 0


def test_td019_yakin_kelime_tekrari() -> None:
    rule = YakinKelimeTekrariRule(min_repetition=3)
    # 'yaz' koku: yazarlar, yazıda, yazdılar (3 kez)
    doc_pos = parse_document("Yazarlar son yazıda konuyu etraflıca yazdılar.")
    findings = rule.check(doc_pos)
    assert len(findings) >= 1
    assert findings[0].rule_id == "TD019"

    doc_neg = parse_document("Farklı kelimelerle kurulmuş dengeli bir cümle örneğidir.")
    assert len(rule.check(doc_neg)) == 0


def test_td020_virgul_zinciri() -> None:
    rule = VirgulZinciriRule(max_commas=4)
    doc_pos = parse_document("Elma, armut, kiraz, vişne, çilek ve kavun aldık.")
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD020"

    doc_neg = parse_document("Elma ve armut aldık.")
    assert len(rule.check(doc_neg)) == 0


def test_td025_veya_baglac_tekrari() -> None:
    rule = VeyaBaglacTekrariRule()
    doc_pos = parse_document("Ahmet ve Mehmet ve Ali veya Ayşe toplantıya katılacak.")
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD025"

    doc_neg = parse_document("Ahmet ve Mehmet toplantıya katıldı.")
    assert len(rule.check(doc_neg)) == 0
