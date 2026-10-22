"""Dogal yazilmis Turkce cumlelerde yanlis pozitif uretmemesi gereken kurallar."""

from __future__ import annotations

import pytest

from turkce_denetim.config import Config
from turkce_denetim.document import parse_document
from turkce_denetim.engine import analyze_text
from turkce_denetim.models import Severity
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


NATURAL_PARAGRAPHS = [
    # 1. News: günün sonunda eve döndük, de/da
    (
        "Yoğun geçen festivalin ardından günün sonunda eve döndük ve dinlendik. "
        "Şehirdeki etkinliklerin yarın da devam edeceği açıklandı."
    ),
    # 2. News / Public statement: bu noktada mid-sentence
    (
        "Bakanlık heyeti sahadaki çalışmaları yerinde incelerken ulaşılan bu noktada "
        "yeni tedbirlerin alınacağını bildirdi."
    ),
    # 3. Dialogue: proper de/da with names and pronouns
    (
        "Ali de geldi mi diye sordu Mehmet. Ayşe gülümseyerek, evet o da salonda "
        "bizi bekliyor cevabını verdi."
    ),
    # 4. Narrative / News: sanki, oysaki
    (
        "Hava aniden soğumuştu; sanki kış erkenden gelmişti. Oysaki meteoroloji "
        "uzmanları sıcaklığın mevsim normallerinde kalacağını öngörmüştü."
    ),
    # 5. Technical: çünkü, de/da
    (
        "Sunucu yapılandırmasında bellek sınırını artırdık çünkü veri tabanı sorguları "
        "yoğun yük altında yavaşlıyordu. Önbellek de devreye alınınca yanıt süreleri kısaldı."
    ),
    # 6. Technical / Architecture
    (
        "Mikroservis mimarisine geçiş sürecinde ekipler bağımsız dağıtım hatları kurdu. "
        "Bu sayede hata payı azaldı ve sistem kararlılığı yükseldi."
    ),
    # 7. Dialogue: mademki, proper de/da
    (
        "Mademki herkes hazır, toplantıya başlayabiliriz dedi yönetici. Selin de sunum "
        "dosyasını ekrana yansıttı."
    ),
    # 8. News / Economics
    (
        "Merkez Bankası faiz kararını kamuoyuyla paylaştı. Piyasalarda işlem hacmi "
        "yükselirken yatırımcılar döviz kurlarındaki hareketliliği yakından izliyor."
    ),
    # 9. Narrative: belki, halbuki
    (
        "Pencerenin kenarında saatlerce oturdu. Belki bir mektup gelir diye umut "
        "ediyordu; halbuki postacı çoktan sokağın sonuna ulaşmıştı."
    ),
    # 10. Technical / DevOps: gelinen bu noktada mid-sentence, de/da
    (
        "Konteyner kayıt defterinde imaj boyutlarını optimize ettik. Gelinen bu noktada "
        "ağ trafiğinde belirgin bir tasarruf sağlandı ve güvenlik testleri de başarıyla tamamlandı."
    ),
]


@pytest.mark.parametrize("paragraph", NATURAL_PARAGRAPHS)
def test_natural_paragraphs_zero_errors(paragraph: str) -> None:
    """Natural Turkish paragraphs must produce zero error-severity findings."""
    result = analyze_text(paragraph, Config())
    error_findings = [f for f in result.findings if f.severity == Severity.ERROR]
    assert error_findings == [], (
        f"Found unexpected error findings in natural text: {error_findings}"
    )
