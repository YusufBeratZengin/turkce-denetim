"""turkce-denetim kütüphanesinin Python API kullanım örneği.

Bu betik, metin analizini, özel yapılandırmaları ve kural motoru çıktılarını
programatik olarak nasıl işleyeceğinizi gösterir.
"""

from __future__ import annotations

from turkce_denetim import (
    Config,
    Severity,
    analyze_text,
    get_naturalness_rating,
    stem,
    stem_words,
    turkish_lower,
    turkish_upper,
)


def main() -> None:
    # 1. Örnek metin: Hem doğal anlatım hem de bazı yapay zekâ kalıpları içerir
    sample_text = (
        "Elbette! Size bu konuda yardımcı olmaktan memnuniyet duyarım.\n\n"
        "Bu noktada dijital dönüşüm yolculuğumuz hız kesmeden devam ediyor. "
        "Konuyu derinlemesine incelemek çok önemlidir ki doğru adımları atalım.\n\n"
        "Sonuç olarak, hazırlanan rapor tüm ayrıntılarıyla paylaşıldı."
    )

    print("=== 1. Varsayılan Yapılandırma ile Metin Analizi ===")
    config = Config(min_severity=Severity.INFO)
    result = analyze_text(sample_text, config)

    print(f"Toplam sözcük sayısı  : {result.word_count}")
    print(f"Toplam cümle sayısı   : {result.sentence_count}")
    print(f"Toplam paragraf sayısı: {result.paragraph_count}")
    print(f"Doğallık puanı        : {result.naturalness_score:.1f} / 100")
    print(f"Derecelendirme        : {get_naturalness_rating(result.naturalness_score)}")
    print(
        f"Bulgu sayıları        : {result.error_count} hata, "
        f"{result.warn_count} uyarı, {result.info_count} bilgi"
    )
    print("\nTespit Edilen Bulgular:")
    for finding in result.findings:
        print(
            f"  [{finding.severity.value.upper()}] {finding.rule_id} ({finding.rule_name}) "
            f"Satır {finding.line}:{finding.column} -> {finding.message}"
        )
        if finding.suggestion:
            print(f"    Öneri: {finding.suggestion}")

    print("\n=== 2. Özel Yapılandırma ile Filtreleme ===")
    # Belirli kuralları devre dışı bırak ve yalnızca uyarı/hata düzeyini raporla
    filtered_config = Config(
        min_severity=Severity.WARN,
        disable=["TD008"],  # 'elbette-acilis' kuralını kapat
    )
    filtered_result = analyze_text(sample_text, filtered_config)
    print(f"Filtrelenmiş bulgu sayısı: {len(filtered_result.findings)}")
    for finding in filtered_result.findings:
        print(f"  [{finding.rule_id}] {finding.message}")

    print("\n=== 3. Türkçe Büyük/Küçük Harf ve Gövdeleme Yardımcıları ===")
    word = "İSTANBUL"
    lowered = turkish_lower(word)
    uppered = turkish_upper("ışık")
    print(f"turkish_lower('{word}') -> '{lowered}'")
    print(f"turkish_upper('ışık')     -> '{uppered}'")

    sample_sentence = "Yazarlarımız yazılarında yazma eylemini tartıştılar."
    stems = stem_words(sample_sentence)
    print(f"Cümle: '{sample_sentence}'")
    print(f"Kökler: {stems}")
    print(f"'yazarlarımız' kökü: '{stem('yazarlarımız')}'")


if __name__ == "__main__":
    main()
