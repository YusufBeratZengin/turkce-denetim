"""Kural kayit defteri ve secim mekanizmasi."""

from __future__ import annotations

from typing import TYPE_CHECKING

from turkce_denetim.models import Severity
from turkce_denetim.rules.ai_patterns import (
    DerinlemesineRule,
    DunyasiMetaforuRule,
    ElbetteAcilisRule,
    HarikaSoruRule,
    KapsamliSekildeRule,
    ParagrafAcilisTekrariRule,
    SonucOlarakKapanisRule,
    UcluSifatDizisiRule,
    YolculukMetaforuRule,
)
from turkce_denetim.rules.base import Rule
from turkce_denetim.rules.readability import (
    CumleUzunluguRule,
    ParagrafUzunluguRule,
    VeyaBaglacTekrariRule,
    VirgulZinciriRule,
    YakinKelimeTekrariRule,
)
from turkce_denetim.rules.spelling import (
    BilesikAyriYazimRule,
    DeDaBaglaciRule,
    KiBaglaciRule,
    TirnakTutarsizligiRule,
)
from turkce_denetim.rules.translation import (
    BuNoktadaRule,
    EdilgenYigilmasiRule,
    GununSonundaRule,
    IleBirlikteAsiriRule,
    KonusundaYigilmasiRule,
    OnemlidirKiRule,
    SahipOlmakRule,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

ALL_RULES: list[type[Rule]] = [
    # Ceviri kaliplari (TD001 - TD007)
    IleBirlikteAsiriRule,
    BuNoktadaRule,
    GununSonundaRule,
    OnemlidirKiRule,
    KonusundaYigilmasiRule,
    SahipOlmakRule,
    EdilgenYigilmasiRule,
    # Yapay zeka kaliplari (TD008 - TD016)
    ElbetteAcilisRule,
    HarikaSoruRule,
    SonucOlarakKapanisRule,
    DunyasiMetaforuRule,
    YolculukMetaforuRule,
    DerinlemesineRule,
    KapsamliSekildeRule,
    UcluSifatDizisiRule,
    ParagrafAcilisTekrariRule,
    # Okunabilirlik kaliplari (TD017 - TD020, TD025)
    CumleUzunluguRule,
    ParagrafUzunluguRule,
    YakinKelimeTekrariRule,
    VirgulZinciriRule,
    VeyaBaglacTekrariRule,
    # Yazim ve tipografi (TD021 - TD024)
    DeDaBaglaciRule,
    KiBaglaciRule,
    BilesikAyriYazimRule,
    TirnakTutarsizligiRule,
]

RULE_MAP: dict[str, type[Rule]] = {cls.id: cls for cls in ALL_RULES}


def get_rule_by_id(rule_id: str) -> type[Rule] | None:
    """Kural kimligine (orn: TD001) gore kural sinifini getirir."""
    return RULE_MAP.get(rule_id.upper())


def create_rules(
    disabled: Iterable[str] | None = None,
    min_severity: Severity | None = None,
    max_sentence_words: int = 35,
    max_paragraph_words: int = 120,
    max_commas: int = 5,
    min_word_repetition: int = 3,
) -> list[Rule]:
    """Yapilandirmaya gore aktif kural nesnelerini olusturur."""
    disabled_set = {d.strip().upper() for d in disabled} if disabled else set()
    active_rules: list[Rule] = []

    for rule_cls in ALL_RULES:
        if rule_cls.id.upper() in disabled_set or rule_cls.name.lower() in disabled_set:
            continue

        if min_severity is not None and rule_cls.severity < min_severity:
            continue

        # Parametre alan kurallari baslat
        instance: Rule
        if rule_cls is CumleUzunluguRule:
            instance = CumleUzunluguRule(max_words=max_sentence_words)
        elif rule_cls is ParagrafUzunluguRule:
            instance = ParagrafUzunluguRule(max_words=max_paragraph_words)
        elif rule_cls is VirgulZinciriRule:
            instance = VirgulZinciriRule(max_commas=max_commas)
        elif rule_cls is YakinKelimeTekrariRule:
            instance = YakinKelimeTekrariRule(min_repetition=min_word_repetition)
        else:
            instance = rule_cls()

        active_rules.append(instance)

    return active_rules
