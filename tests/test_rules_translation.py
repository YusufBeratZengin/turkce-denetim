"""Ceviri kokusu kurallari testleri (TD001 - TD007)."""

from __future__ import annotations

from turkce_denetim.document import parse_document
from turkce_denetim.rules.translation import (
    BuNoktadaRule,
    EdilgenYigilmasiRule,
    GununSonundaRule,
    IleBirlikteAsiriRule,
    KonusundaYigilmasiRule,
    OnemlidirKiRule,
    SahipOlmakRule,
)


def test_td001_ile_birlikte() -> None:
    rule = IleBirlikteAsiriRule()
    # Pozitif ornek: yakalamali
    doc_pos = parse_document("Teknolojinin gelişmesi ile birlikte hayatımız değişti.")
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD001"

    # Negatif ornek: yalin ek kullanilmis, yakalamamali
    doc_neg = parse_document("Teknolojinin gelişmesiyle hayatımız değişti.")
    assert len(rule.check(doc_neg)) == 0


def test_td002_bu_noktada() -> None:
    rule = BuNoktadaRule()
    doc_pos = parse_document("Bu noktada dikkat etmemiz gereken hususlar vardır.")
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD002"

    doc_neg = parse_document("Burada dikkat etmemiz gereken hususlar vardır.")
    assert len(rule.check(doc_neg)) == 0


def test_td003_gunun_sonunda() -> None:
    rule = GununSonundaRule()
    doc_pos = parse_document("Günün sonunda herkes kendi sorumluluğunu bilmelidir.")
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD003"

    doc_neg = parse_document("Sonuçta herkes kendi sorumluluğunu bilmelidir.")
    assert len(rule.check(doc_neg)) == 0


def test_td004_onemlidir_ki() -> None:
    rule = OnemlidirKiRule()
    doc_pos1 = parse_document("Şunu belirtmek önemlidir ki bu bir denemedir.")
    findings1 = rule.check(doc_pos1)
    assert len(findings1) == 1

    doc_pos2 = parse_document("Önemlidir ki kurallara uyulsun.")
    assert len(rule.check(doc_pos2)) == 1

    doc_neg = parse_document("Kurallara uyulması büyük bir önem taşır.")
    assert len(rule.check(doc_neg)) == 0


def test_td005_konusunda_yigilmasi() -> None:
    rule = KonusundaYigilmasiRule()
    # Pozitif: ayni cumlede birden fazla 'konusunda'
    doc_pos = parse_document(
        "Veri güvenliği konusunda ve sistem mimarisi konusundaki kararlar alındı."
    )
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD005"

    # Negatif: tek bir 'konusunda' veya farkli cumleler
    doc_neg = parse_document(
        "Veri güvenliği konusunda karar alındı. Sistem mimarisi ayrıca ele alındı."
    )
    assert len(rule.check(doc_neg)) == 0


def test_td006_sahip_olmak() -> None:
    rule = SahipOlmakRule()
    # Pozitif: gereksiz have cevirisi
    doc_pos = parse_document("Bu cihaz yüksek bir hıza sahiptir.")
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD006"

    # Negatif: gercek mulkiyet (hak sahibi, ev sahibi)
    doc_neg = parse_document("Telif hakkı sahibi toplantıya katıldı.")
    assert len(rule.check(doc_neg)) == 0


def test_td007_edilgen_yigilmasi() -> None:
    rule = EdilgenYigilmasiRule()
    # Pozitif: ayni cumlede 3+ edilgen fiil
    doc_pos = parse_document(
        "Toplantıda yeni planlar yapıldı, bütçe onaylandı ve görevler dağıtıldı."
    )
    findings = rule.check(doc_pos)
    assert len(findings) == 1
    assert findings[0].rule_id == "TD007"

    # Negatif: etken fiiller ve sadece 1 edilgen fiil
    doc_neg = parse_document("Müdür toplantıyı açtı, planları sundu ve yeni hedefler belirlendi.")
    assert len(rule.check(doc_neg)) == 0
