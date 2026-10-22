"""Dogallik puani (Naturalness Score) hesaplama modulu."""

from __future__ import annotations

from typing import TYPE_CHECKING

from turkce_denetim.models import Severity

if TYPE_CHECKING:
    from turkce_denetim.models import Finding

# Bulgu agirlik katsayilari
_SEVERITY_WEIGHTS = {
    Severity.ERROR: 8.0,
    Severity.WARN: 3.0,
    Severity.INFO: 1.0,
}


def calculate_naturalness_score(word_count: int, findings: list[Finding]) -> float:
    """Metnin 0 - 100 arasi dogallik puanini hesaplar.

    Formul:
    1. Her bulgu onem derecesine gore agirliklandirilir:
       - Error (Yazim/Hata): 8.0 puan
       - Warn (Ceviri/Yapay zeka kokusu): 3.0 puan
       - Info (Uslup/Okunabilirlik onerisi): 1.0 puan
    2. Toplam ceza puani metin uzunluguna gore 100 kelime basina normallestirilir:
       Normallestirilmis Ceza = (Toplam Ceza * 100) / max(Kelime Sayisi, 50)
    3. Dogallik Puani = max(0.0, min(100.0, 100.0 - Normallestirilmis Ceza))

    Temiz ve dogal yazilmis metinler 90-100 puan alir.
    """
    if word_count <= 0:
        return 100.0

    total_penalty = sum(_SEVERITY_WEIGHTS.get(f.severity, 1.0) for f in findings)
    effective_words = max(word_count, 50)
    normalized_penalty = (total_penalty * 100.0) / effective_words

    score = 100.0 - normalized_penalty
    return round(max(0.0, min(100.0, score)), 1)


def get_naturalness_rating(score: float) -> str:
    """Puanin metinsel seviye aciklamasi."""
    if score >= 90.0:
        return "Yüksek Doğallık (Temiz ve akıcı)"
    if score >= 75.0:
        return "İyi (Birkaç kalıp içeriyor)"
    if score >= 50.0:
        return "Orta (Belirgin yapay zekâ veya çeviri kokusu)"
    return "Düşük (Yoğun sentetik / basmakalıp üslup)"
