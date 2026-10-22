"""Turkce basit ek budayici (stemmer / suffix stripper).

Kelime tekrarlarini ve benzer kaliplari tespit etmek icin yaygin Turkce cekim ve yapim eklerini
kok duzeyine budar. Dis kutuphane bagimliligi yoktur.
"""

from __future__ import annotations

import re

from turkce_denetim.casing import turkish_casefold

TURKISH_VOWELS = frozenset("aeıioöuü")

# Ek gruplari sirali olarak denenir:
# 1. Ek-fiil ve kisi ekleri (copula & person)
# 2. Bilesik durum ve iyelik ekleri
# 3. Yalin durum (ismin halleri) ekleri
# 4. Yalin iyelik ekleri
# 5. Cogul ekleri
# 6. Yaygin turetim ekleri (-lik, -ci, -siz, -li)
_SUFFIX_STAGES: list[list[str]] = [
    # Asama 1: Ek-fiil ve kisi ekleri
    [
        "cesine", "casına",
        "dirler", "dırlar", "dürler", "durlar", "tirler", "tırlar", "türler", "turlar",
        "siniz", "sınız", "sünüz", "sunuz",
        "yken", "ken",
        "ymiş", "ymış", "ymüş", "ymuş", "miş", "mış", "müş", "muş",
        "ydi", "ydı", "ydü", "ydu", "di", "dı", "dü", "du", "ti", "tı", "tü", "tu",
        "yse", "ysa", "se", "sa",
        "dir", "dır", "dür", "dur", "tir", "tır", "tür", "tur",
        "sin", "sın", "sün", "sun",
        "yım", "yim", "yüm", "yum", "ım", "im", "um", "üm",
        "yız", "yiz", "yuz", "yüz", "ız", "iz", "uz", "üz",
    ],
    # Asama 2: Bilesik iyelik + durum ekleri (-lerinden, -imizden, -inde vb.)
    [
        "larımızdan", "lerimizden", "larımızda", "lerimizde",
        "larımızı", "lerimizi", "larımıza", "lerimize", "larımızın", "lerimizin",
        "mızdan", "mizden", "muzdan", "müzden", "nızdan", "nizden", "nuzdan", "nüzden",
        "umuzdan", "ümüzden", "ımızdan", "imizden",
        "lerinden", "larından", "lerinde", "larında", "lerine", "larına", "lerini", "larını",
        "inden", "ından", "ünden", "undan",
        "inde", "ında", "ünde", "unda",
        "ine", "ına", "üne", "una",
        "ini", "ını", "ünü", "unu",
        "inin", "ının", "ünün", "unun",
        "ndan", "nden", "nda", "nde", "na", "ne", "nı", "ni", "nu", "nü",
    ],
    # Asama 3: Yalin durum ekleri (Ablative, Locative, Dative, Accusative, Genitive, Instrumental)
    [
        "dan", "den", "tan", "ten",
        "da", "de", "ta", "te",
        "nın", "nin", "nun", "nün",
        "yla", "yle", "la", "le",
        "ya", "ye",
        "yı", "yi", "yu", "yü",
    ],
    # Asama 4: Yalin iyelik ekleri
    [
        "larımız", "lerimiz",
        "ımız", "imiz", "umuz", "ümüz",
        "ınız", "iniz", "unuz", "ünüz",
        "mız", "miz", "muz", "müz",
        "nız", "niz", "nuz", "nüz",
        "ları", "leri",
        "sı", "si", "su", "sü",
    ],
    # Asama 5: Cogul eki
    [
        "lar", "ler",
    ],
    # Asama 6: Yaygin isimden isim yapim ve fiil mastar ekleri
    [
        "mak", "mek",
        "lık", "lik", "luk", "lük",
        "sız", "siz", "suz", "süz",
        "lı", "li", "lu", "lü",
        "cı", "ci", "cu", "cü", "çı", "çi", "çu", "çü",
    ],
]

_WORD_CLEAN_RE = re.compile(r"^[^a-zçğıöşü]+|[^a-zçğıöşü]+$")


def _has_vowel(text: str) -> bool:
    return any(ch in TURKISH_VOWELS for ch in text)


def stem(word: str) -> str:
    """Tek bir kelimenin eklerini kirparak yaklasik kok/govde dondurur.

    Ozel isim kesme isaretlerini ve cevreleyen noktalama isaretlerini temizler.
    Kok boyutu 2 harften kisa olamaz ve icinde en az bir unlu harf bulunmalidir.
    """
    token = turkish_casefold(word.strip())

    # Kesme isaretli ozel isimlerde kesme isareti koku ve ekleri ayirir
    has_apostrophe = False
    if "'" in token:
        token = token.split("'")[0]
        has_apostrophe = True
    elif "’" in token:
        token = token.split("’")[0]
        has_apostrophe = True

    # Cevreleyen ozel karakterleri temizle
    token = _WORD_CLEAN_RE.sub("", token)

    if has_apostrophe or len(token) <= 2:
        return token

    current = token
    for stage in _SUFFIX_STAGES:
        matched_suffix: str | None = None
        for s in stage:
            if current.endswith(s):
                candidate = current[: -len(s)]
                # Kalan kok en az 2 harfli olmali ve en az 1 sesli harf icermeli
                if len(candidate) >= 2 and _has_vowel(candidate):
                    matched_suffix = s
                    current = candidate
                    break
        if matched_suffix is not None:
            continue

    return current


def stem_words(text: str) -> list[str]:
    """Bir metindeki tum kelimeleri budar ve kucuk harfli kok listesi dondurur."""
    raw_words = re.findall(r"[a-zçğıöşüA-ZÇĞİÖŞÜ0-9'’-]+", text)
    stems: list[str] = []
    for w in raw_words:
        st = stem(w)
        if st:
            stems.append(st)
    return stems
