"""Dogallik puani (Naturalness Score) hesaplama testleri."""

from __future__ import annotations

import pytest

from turkce_denetim.config import Config
from turkce_denetim.engine import analyze_text
from turkce_denetim.models import Finding, Severity
from turkce_denetim.scoring import calculate_naturalness_score, get_naturalness_rating


def test_naturalness_score_clean_text() -> None:
    # 0 bulgu -> 100 puan
    assert calculate_naturalness_score(150, []) == 100.0
    assert calculate_naturalness_score(0, []) == 100.0


def test_naturalness_score_formula() -> None:
    # 100 kelime, 1 error (8), 1 warn (3), 1 info (1) = 12 ceza puani
    # Normallestirilmis ceza: (12 * 100) / 100 = 12.0
    # Puan: 100.0 - 12.0 = 88.0
    dummy_findings = [
        Finding(
            rule_id="TD023",
            rule_name="bilesik-ayri-yazim",
            message="hata",
            severity=Severity.ERROR,
            line=1,
            column=1,
            end_line=1,
            end_column=5,
        ),
        Finding(
            rule_id="TD001",
            rule_name="ile-birlikte-asiri",
            message="uyari",
            severity=Severity.WARN,
            line=1,
            column=10,
            end_line=1,
            end_column=20,
        ),
        Finding(
            rule_id="TD014",
            rule_name="kapsamli-sekilde",
            message="bilgi",
            severity=Severity.INFO,
            line=1,
            column=25,
            end_line=1,
            end_column=40,
        ),
    ]

    score = calculate_naturalness_score(100, dummy_findings)
    assert score == 88.0
    rating = get_naturalness_rating(score)
    assert "İyi" in rating


def test_natural_turkish_text_scores_high() -> None:
    # Dogal, akici Turkce bir paragraf
    natural_text = (
        "Yaz mevsiminde yaylaya çıkmak ve serin suların başında dinlenmek insana huzur verir. "
        "Köydeki taş evler asırlık çınarların gölgesinde zamana meydan okuyor. "
        "Çocuklar derede yüzerken büyükler akşam sohbeti için çay demliyor. "
        "Buradaki sade yaşam şehrin karmaşasından uzaklaşmak isteyenler için eşsiz bir sığınaktır."
    )
    config = Config()
    result = analyze_text(natural_text, config)
    # Temiz dogal metinde bulgu olmamali veya cok az olmali; puan 90+ olmali
    assert result.error_count == 0
    assert result.warn_count == 0
    assert result.naturalness_score >= 90.0


def test_ai_synthetic_text_scores_lower() -> None:
    # Yapay zeka ve ceviri kokusuyla dolu sentetik metin
    ai_text = (
        "Elbette! Harika bir soru sordunuz. "
        "Yapay zekâ dünyasında bu noktada dijital dönüşüm yolculuğunda ilerlemek günün sonunda çok önemlidir ki "
        "hızlı, esnek ve dinamik bir yapıya sahip olmak için konuyu derinlemesine incelemek gerekir. "
        "Herşey çok güzel olacak ve kapsamlı bir şekilde analiz yapılacaktır. "
        "Sonuç olarak, bu adımlar başarımızı artıracaktır."
    )
    config = Config()
    result = analyze_text(ai_text, config)
    # Bircok kural ihlali olmali ve puan belirgin sekilde dusmeli
    assert len(result.findings) >= 5
    assert result.naturalness_score < 60.0


def test_severity_ordering_and_comparisons() -> None:
    assert Severity.INFO < Severity.WARN
    assert Severity.WARN < Severity.ERROR
    assert Severity.ERROR > Severity.WARN
    assert Severity.WARN <= Severity.WARN
    assert Severity.ERROR >= Severity.INFO

    # String inheritance and equality
    assert Severity.WARN.value == "warn"
    other_val: object = 10
    assert (Severity.WARN == other_val) is False

    # Rich comparisons with non-Severity return NotImplemented
    assert Severity.WARN.__ge__(other_val) is NotImplemented
    assert Severity.WARN.__gt__(other_val) is NotImplemented
    assert Severity.WARN.__le__(other_val) is NotImplemented
    assert Severity.WARN.__lt__(other_val) is NotImplemented

    with pytest.raises(TypeError):
        _ = Severity.WARN < other_val
    with pytest.raises(TypeError):
        _ = Severity.WARN <= other_val
    with pytest.raises(TypeError):
        _ = Severity.WARN > other_val
    with pytest.raises(TypeError):
        _ = Severity.WARN >= other_val
