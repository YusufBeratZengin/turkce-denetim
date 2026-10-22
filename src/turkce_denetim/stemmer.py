"""Turkce basit ek budayici (stemmer / suffix stripper).

Kelime tekrarlarini ve benzer kaliplari tespit etmek icin yaygin Turkce cekim ve yapim eklerini
kok duzeyine budar. Dis kutuphane bagimliligi yoktur.
"""

from __future__ import annotations

import re

from turkce_denetim.casing import turkish_casefold

TURKISH_VOWELS = frozenset("aeıioöuü")

_SUFFIX_GROUPS: list[list[str]] = [
    # 1. Uzun bilesik durum/iyelik/cogul ekleri
    [
        "larımızdan",
        "lerimizden",
        "larımızda",
        "lerimizde",
        "larımızı",
        "lerimizi",
        "larımıza",
        "lerimize",
        "larımızın",
        "lerimizin",
        "lerinden",
        "larından",
        "lerinde",
        "larında",
        "lerine",
        "larına",
        "lerini",
        "larını",
        "lerden",
        "lardan",
        "lerde",
        "larda",
        "lerle",
        "larla",
        "lerin",
        "ların",
        "mızdan",
        "mizden",
        "muzdan",
        "müzden",
        "nızdan",
        "nizden",
        "nuzdan",
        "nüzden",
        "umuzdan",
        "ümüzden",
        "ımızdan",
        "imizden",
        "dılar",
        "diler",
        "dular",
        "düler",
        "tılar",
        "tiler",
        "dınız",
        "diniz",
        "tınız",
        "tiniz",
        "dık",
        "dik",
        "duk",
        "dük",
        "tık",
        "tik",
        "tuk",
        "tük",
        "dım",
        "dim",
        "dum",
        "düm",
        "tım",
        "tim",
        "tum",
        "tüm",
        "dın",
        "din",
        "dun",
        "dün",
        "tın",
        "tin",
        "tun",
        "tün",
        "madan",
        "meden",
        "maktan",
        "mekten",
    ],
    # 2. Yalin durum ve cogul ekleri
    [
        "dan",
        "den",
        "tan",
        "ten",
        "da",
        "de",
        "ta",
        "te",
        "lar",
        "ler",
        "nın",
        "nin",
        "nun",
        "nün",
        "yla",
        "yle",
        "ya",
        "ye",
        "yı",
        "yi",
        "yu",
        "yü",
        "la",
        "le",
        "nde",
        "nda",
        "nden",
        "ndan",
        "ne",
        "na",
        "ni",
        "nı",
    ],
    # 3. Iyelik ve ek-fiil ekleri
    [
        "larımız",
        "lerimiz",
        "ları",
        "leri",
        "ımız",
        "imiz",
        "umuz",
        "ümüz",
        "ınız",
        "iniz",
        "unuz",
        "ünüz",
        "mız",
        "miz",
        "muz",
        "müz",
        "nız",
        "niz",
        "nuz",
        "nüz",
        "sı",
        "si",
        "su",
        "sü",
        "iyor",
        "ıyor",
        "uyor",
        "üyor",
        "acak",
        "ecek",
        "malı",
        "meli",
        "mış",
        "miş",
        "muş",
        "müş",
        "dı",
        "di",
        "du",
        "dü",
        "tı",
        "ti",
        "tu",
        "tü",
    ],
    # 4. Yapim ve mastar ekleri
    [
        "mak",
        "mek",
        "lık",
        "lik",
        "luk",
        "lük",
        "sız",
        "siz",
        "suz",
        "süz",
        "ıcı",
        "ici",
        "ucu",
        "ücü",
        "lı",
        "li",
        "lu",
        "lü",
        "cı",
        "ci",
        "cu",
        "cü",
        "çı",
        "çi",
        "çu",
        "çü",
    ],
    # 5. Kisa ekler (en son denenmeli)
    [
        "ar",
        "er",
        "ım",
        "im",
        "um",
        "üm",
        "ın",
        "in",
        "un",
        "ün",
        "ı",
        "i",
        "u",
        "ü",
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
    for _ in range(3):
        matched = False
        for group in _SUFFIX_GROUPS:
            for s in group:
                if current.endswith(s):
                    candidate = current[: -len(s)]
                    if len(candidate) >= 2 and _has_vowel(candidate):
                        current = candidate
                        matched = True
                        break
            if matched:
                break
        if not matched:
            break

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
