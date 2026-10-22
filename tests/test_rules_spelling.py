"""Yazim ve imla kurallari testleri (TD021 - TD024)."""

from __future__ import annotations

from turkce_denetim.document import parse_document
from turkce_denetim.rules.spelling import (
    BilesikAyriYazimRule,
    DeDaBaglaciRule,
    KiBaglaciRule,
    TirnakTutarsizligiRule,
)


def test_td021_de_da_baglaci() -> None:
    rule = DeDaBaglaciRule()

    # Pozitif: fiilden sonra bitisen baglac
    doc_pos1 = parse_document("Dün akşam sinemaya gittide bize haber vermedi.")
    findings1 = rule.check(doc_pos1)
    assert len(findings1) >= 1
    assert any(f.rule_id == "TD021" for f in findings1)

    # Pozitif: zarf-fiilden sonra bitisen baglac
    doc_pos2 = parse_document("Bunu yapıpta pişman olma.")
    findings2 = rule.check(doc_pos2)
    assert len(findings2) >= 1

    # Pozitif: zamir ardindan bitisen baglac
    doc_pos3 = parse_document("Bende geldim ve bekliyorum.")
    findings3 = rule.check(doc_pos3)
    assert len(findings3) >= 1

    # Pozitif: yanlis ayrilmis bulunma hali
    doc_pos4 = parse_document("Bütün gün ev de kaldım.")
    findings4 = rule.check(doc_pos4)
    assert len(findings4) >= 1

    # Negatif: dogru bulunma hali ve istisna isimler
    doc_neg = parse_document("Toplantıda kararlar alındı ve evde dinlendim.")
    assert len(rule.check(doc_neg)) == 0


def test_td022_ki_baglaci() -> None:
    rule = KiBaglaciRule()

    # Pozitif: fiilden sonra gelen bitisik ki
    doc_pos1 = parse_document("Gördümki her şey yolunda.")
    findings1 = rule.check(doc_pos1)
    assert len(findings1) == 1
    assert findings1[0].rule_id == "TD022"

    doc_pos2 = parse_document("Demekki haklıymışsın.")
    assert len(rule.check(doc_pos2)) == 1

    doc_pos3 = parse_document("Yeterki çalışmaya devam et.")
    assert len(rule.check(doc_pos3)) == 1

    # Negatif: SOMBAHCEMI istisnalari (bitisik yazilmali)
    doc_neg_sombahcemi = parse_document("Belki gelir, çünkü söz verdi ve sanki biliyordu.")
    assert len(rule.check(doc_neg_sombahcemi)) == 0

    # Negatif: sifat yapan -ki eki (evdeki, dünkü, bizimki)
    doc_neg_sifat = parse_document("Evdeki hesap çarşıya uymadı. Dünkü maç güzeldi.")
    assert len(rule.check(doc_neg_sifat)) == 0


def test_td023_bilesik_ayri_yazim() -> None:
    rule = BilesikAyriYazimRule()

    # Pozitif: herşey -> her şey
    doc_pos1 = parse_document("Herşey çok güzel olacak.")
    findings1 = rule.check(doc_pos1)
    assert len(findings1) == 1
    assert findings1[0].rule_id == "TD023"
    assert findings1[0].suggestion == "her şey"

    # Pozitif: hiçbirşey, bir çok
    doc_pos2 = parse_document("Hiçbirşey bilmeden bir çok fikir öne sürdü.")
    findings2 = rule.check(doc_pos2)
    assert len(findings2) == 2

    # Pozitif: yalnış, farketmek
    doc_pos3 = parse_document("Yalnış bir adım attığını farketti.")
    findings3 = rule.check(doc_pos3)
    assert len(findings3) == 2

    # Negatif: dogru yazimlar
    doc_neg = parse_document("Her şey yolunda, birçok kişi doğru olanı fark etti.")
    assert len(rule.check(doc_neg)) == 0


def test_td024_tirnak_tutarsizligi() -> None:
    rule = TirnakTutarsizligiRule()

    # Pozitif: hem duz hem tipografik tirnak karisik
    doc_pos = parse_document('Bu "düz" ve bu “tipografik” bir tırnak kullanımıdır.')
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD024"

    # Negatif: yalnizca tipografik tirnak
    doc_neg = parse_document("Bu “tamamen” tipografik bir “örnektir”.")
    assert len(rule.check(doc_neg)) == 0
