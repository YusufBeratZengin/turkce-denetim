"""Dogal yazilmis Turkce cumlelerde yanlis pozitif uretmemesi gereken kurallar."""

from __future__ import annotations

import pytest

from turkce_denetim.config import Config
from turkce_denetim.document import parse_document
from turkce_denetim.engine import analyze_text
from turkce_denetim.rules.registry import ALL_RULES

# (kural kimligi, dogal cumle) - hicbirinde bulgu cikmamali
NATURAL_CASES = [
    ("TD001", "Dün akşam arkadaşlarımla birlikte çarşıya gittik."),
    ("TD001", "Bununla birlikte, plan yine de değişmedi."),
    ("TD001", "Ayşe ile birlikte çay içtik."),
    ("TD002", "Geldiğimiz bu noktada durup biraz düşündük."),
    ("TD003", "Günün sonunda eve döndük ve hemen uyuduk."),
    ("TD006", "Mirasa sahip çıktı ve kimseye devretmedi."),
    ("TD006", "Sokaktaki kediye sahip çıkan bir adam gördük."),
    ("TD006", "Sahip olmak istediğim tek şey biraz huzur."),
    ("TD007", "Çocuk gülüyor, sunucu bunu kullanıyor ve herkes sevindi."),
    ("TD007", "Müdür bunu bildi, sunuyor ve kullanıyor."),
    ("TD008", "Elbette, kapıyı ben açarım."),
    ("TD008", "Kesinlikle. Ben de aynısını düşünüyordum."),
    ("TD011", "Onun dünyasında her şey farklıydı."),
    ("TD011", "Çocukların dünyasında zaman başka akar."),
    ("TD011", "Harry Potter dünyasında geçen bir roman okudum."),
    ("TD012", "Sabah erkenden uzun bir yolculuğa çıktık."),
    ("TD012", "Hayat yolculuğu dedikleri şey buymuş."),
    ("TD015", "Ayşe, Ali ve Veli bir araya geldi."),
    ("TD015", "Elma, armut ve muz bir sepete konuldu."),
    ("TD021", "Kulüpte yeni bir makine kuruldu."),
    ("TD021", "Grupta kimse konuşmuyordu."),
    ("TD021", "Bu tipte cihazlar pahalıdır."),
    ("TD021", "Bende bir sorun var, dedi Ali."),
    ("TD021", "Ev de kalabalıktı, araba da çalışmıyordu."),
    ("TD021", "Sende bir gariplik var."),
]


@pytest.mark.parametrize(("rule_id", "text"), NATURAL_CASES)
def test_natural_sentence_not_flagged(rule_id: str, text: str) -> None:
    rule = next(r() for r in ALL_RULES if r.id == rule_id)
    assert rule.check(parse_document(text)) == []


def test_td016_common_pronoun_openers_not_flagged() -> None:
    rule = next(r() for r in ALL_RULES if r.id == "TD016")
    doc = parse_document("Bu kitap iyi yazılmış.\n\nBu konuyu uzun uzun konuştuk.")
    assert rule.check(doc) == []


def test_td016_two_word_repeat_still_flagged() -> None:
    rule = next(r() for r in ALL_RULES if r.id == "TD016")
    doc = parse_document("Bu yüzden erken çıktık.\n\nBu yüzden yağmura yakalandık.")
    assert len(rule.check(doc)) == 1


def test_natural_multi_paragraph_text_is_clean() -> None:
    text = (
        "Dün akşam arkadaşlarımla birlikte eski çarşıya gittik. Bununla birlikte, kimsenin canı "
        "yemek istemiyordu; sadece dolaşıp vitrinlere baktık.\n\n"
        "Bu hafta kulüpte herkes çok heyecanlıydı. Çocuk gülüyor, sunucu ise bir şeyler "
        "anlatıyordu. Bende bir sorun var, dedi Ali, ama kimse ciddiye almadı.\n\n"
        "Bu yüzden erken çıktık. Günün sonunda eve döndük, herkes yorgundu.\n\n"
        "Bu kitap iyi yazılmış. Sabah uzun bir yolculuğa çıktık ve yolda kediye sahip çıkan "
        "bir adam gördük."
    )
    result = analyze_text(text, Config())
    assert [f.rule_id for f in result.findings] == []
    assert result.naturalness_score >= 95.0


def test_td021_still_catches_real_errors() -> None:
    rule = next(r() for r in ALL_RULES if r.id == "TD021")
    assert len(rule.check(parse_document("Bütün gün ev de kaldım."))) == 1
    assert len(rule.check(parse_document("Bende geldim ve bekliyorum."))) == 1
    assert len(rule.check(parse_document("Bunu yapıpta pişman olma."))) == 1


def test_td007_real_passives_still_flagged() -> None:
    rule = next(r() for r in ALL_RULES if r.id == "TD007")
    doc = parse_document("Kararlar alındı, raporlar yazıldı ve bütçe onaylandı.")
    assert len(rule.check(doc)) == 1


def test_td007_kullan_is_not_passive() -> None:
    rule = next(r() for r in ALL_RULES if r.id == "TD007")
    doc = parse_document("Ekip aracı kullandı, rapor yazdı ve sonucu kullanıyor.")
    assert rule.check(doc) == []


def test_paragraphs_are_split_around_masked_code_fence() -> None:
    doc = parse_document("Birinci paragraf.\n```\nkod\n```\nİkinci paragraf.\n")
    assert [p.text for p in doc.paragraphs] == ["Birinci paragraf.", "İkinci paragraf."]


def test_td001_sentence_initial_abstract_noun_still_flagged() -> None:
    rule = next(r() for r in ALL_RULES if r.id == "TD001")
    assert len(rule.check(parse_document("Gelişmeler ile birlikte yeni imkânlar doğdu."))) == 1


def test_td012_possessive_form_flagged() -> None:
    rule = next(r() for r in ALL_RULES if r.id == "TD012")
    assert len(rule.check(parse_document("Dijital dönüşüm yolculuğumuz başladı."))) == 1


def test_config_accepts_string_severity() -> None:
    config = Config(min_severity="warn")  # type: ignore[arg-type]
    result = analyze_text("Gördümki her şey yolunda. Bu noktada durduk.", config)
    ids = {f.rule_id for f in result.findings}
    assert "TD022" in ids  # error korunur
    assert "TD002" not in ids  # info elenir
