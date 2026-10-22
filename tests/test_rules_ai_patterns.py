"""Yapay zeka kalip kurallari testleri (TD008 - TD016)."""

from __future__ import annotations

from turkce_denetim.document import parse_document
from turkce_denetim.rules.ai_patterns import (
    DunyasiMetaforuRule,
    DerinlemesineRule,
    ElbetteAcilisRule,
    HarikaSoruRule,
    KapsamliSekildeRule,
    ParagrafAcilisTekrariRule,
    SonucOlarakKapanisRule,
    UcluSifatDizisiRule,
    YolculukMetaforuRule,
)


def test_td008_elbette_acilis() -> None:
    rule = ElbetteAcilisRule()
    doc_pos = parse_document("Elbette! Size bu konuda yardımcı olmaktan mutluluk duyarım.")
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD008"

    doc_neg = parse_document("Bu konuda size doğrudan yardımcı olabilirim.")
    assert len(rule.check(doc_neg)) == 0


def test_td009_harika_soru() -> None:
    rule = HarikaSoruRule()
    doc_pos = parse_document("Harika bir soru sordunuz, hemen yanıtlayalım.")
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD009"

    doc_neg = parse_document("Sorduğunuz konuyu inceleyelim.")
    assert len(rule.check(doc_neg)) == 0


def test_td010_sonuc_olarak_kapanis() -> None:
    rule = SonucOlarakKapanisRule()
    doc_pos = parse_document(
        "Giriş paragrafında konuyu açıkladık.\n\n"
        "Sonuç olarak, bu yöntemlerin tümü etkilidir."
    )
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD010"

    doc_neg = parse_document(
        "Giriş paragrafında konuyu açıkladık.\n\n"
        "Tüm bu adımlar sistemin güvenliğini sağlar."
    )
    assert len(rule.check(doc_neg)) == 0


def test_td011_dunyasi_metaforu() -> None:
    rule = DunyasiMetaforuRule()
    doc_pos = parse_document("Yapay zekâ dünyasında her gün yeni bir gelişme yaşanıyor.")
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD011"

    # Negatif: yerlesik deyim veya somut dunya
    doc_neg = parse_document("İş dünyasında başarı için disiplin şarttır.")
    assert len(rule.check(doc_neg)) == 0


def test_td012_yolculuk_metaforu() -> None:
    rule = YolculukMetaforuRule()
    doc_pos = parse_document("Şirketimiz dijital dönüşüm yolculuğunda önemli adımlar attı.")
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD012"

    # Negatif: gercek fiziksel yolculuk
    doc_neg = parse_document("Trenle Ankara'ya yaptığımız yolculuk üç saat sürdü.")
    assert len(rule.check(doc_neg)) == 0


def test_td013_derinlemesine() -> None:
    rule = DerinlemesineRule()
    doc_pos = parse_document("Bu konuyu derinlemesine incelemek gerekir.")
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD013"

    doc_neg = parse_document("Bu konuyu ayrıntılarıyla incelemek gerekir.")
    assert len(rule.check(doc_neg)) == 0


def test_td014_kapsamli_sekilde() -> None:
    rule = KapsamliSekildeRule()
    doc_pos = parse_document("Raporu kapsamlı bir şekilde hazırladık.")
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD014"

    doc_neg = parse_document("Raporu kapsamlıca hazırladık.")
    assert len(rule.check(doc_neg)) == 0


def test_td015_uclu_sifat_dizisi() -> None:
    rule = UcluSifatDizisiRule()
    doc_pos = parse_document("Hızlı, güvenli ve esnek bir yapı kurmalıyız.")
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD015"

    doc_neg = parse_document("Yapı hem hızlı hem de güvenli olmalıdır.")
    assert len(rule.check(doc_neg)) == 0


def test_td016_paragraf_acilis_tekrari() -> None:
    rule = ParagrafAcilisTekrariRule()
    doc_pos = parse_document(
        "Ayrıca yeni sistem kuralları açıklandı.\n\n"
        "Ayrıca eski yöntemler terk edildi."
    )
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD016"

    doc_neg = parse_document(
        "İlk olarak kurallar açıklandı.\n\n"
        "Bunun yanında eski yöntemler terk edildi."
    )
    assert len(rule.check(doc_neg)) == 0
