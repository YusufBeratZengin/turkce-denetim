"""Yazim ve tipografi kurallari (TD021 - TD024)."""

from __future__ import annotations

import re

from turkce_denetim.casing import turkish_casefold
from turkce_denetim.document import offset_to_line_col
from turkce_denetim.models import Document, Finding, Severity
from turkce_denetim.rules.base import Rule


class DeDaBaglaciRule(Rule):
    """TD021: 'de/da' baglacinin bitisik yazimi veya bulunma halinin yanlis ayrilmasi."""

    id = "TD021"
    name = "de-da-baglaci"
    description = (
        "'de/da' baglacinin fiillerden sonra bitisik yazilmasi veya bulunma halinin ayri yazilmasi."
    )
    severity = Severity.ERROR
    suggestion = "Baglac olan 'de/da' her zaman ayri yazilir ve 'te/ta' bicimini almaz. Bulunma durumu eki '-de/-da' ise bitisik yazilir."

    # Fiil cekimi ardindan bitisen -de/-da/-te/-ta (yuksek guvenli)
    _VERB_PAST_DE = re.compile(
        r"\b([a-zçğıöşü]+(?:dim|din|di|dik|diniz|diler|tim|tin|ti|tik|tiniz|tiler|dım|dın|dı|dık|dınız|dılar|tım|tın|tı|tık|tınız|tılar|düm|dün|dü|dük|dünüz|düler|tüm|tün|tü|tük|tünüz|tüler|dum|dun|du|duk|dunuz|dular|tum|tun|tu|tuk|tunuz|tular))(de|da|te|ta)\b",
        re.IGNORECASE,
    )
    _VERB_GERUND_DE = re.compile(
        r"\b([a-zçğıöşü]+(?:ıp|ip|up|üp))(ta|te|da|de)\b",
        re.IGNORECASE,
    )

    # Zamir ardindan bitisen baglac (yuksek guvenli pozisyonlar)
    _PRONOUN_DE = re.compile(
        r"\b(ben|sen|o|biz|siz|onlar)de\s+(?:de|bir|gel|git|yap|bil|gör|iste|sev|duy|çalış|dur|oku|yaz|düşün|katıl)\w*\b",
        re.IGNORECASE,
    )

    # Yanlis ayrilmis bulunma hali (ev de kaldim, okul da okudum vb.)
    _SPLIT_LOCATIVE = re.compile(
        r"\b(ev|ofis|okul|sokak|oda|masa|yatak|araba|şehir|köy)\s+(?:de|da|te|ta)\s+(?:kal|dur|otur|çalış|yat|uyu|büyü|yaşa)\w*\b",
        re.IGNORECASE,
    )

    _NOUNS_TI = frozenset(
        [
            "toplantı",
            "ayrıntı",
            "bağlantı",
            "sıkıntı",
            "yaşantı",
            "görüntü",
            "akıntı",
            "çıkıntı",
            "kalıntı",
            "tıkıntı",
            "kayıntı",
            "yıkıntı",
        ]
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []

        # 1. Fiil + de/da/te/ta bitisik yazimi
        for match in self._VERB_PAST_DE.finditer(document.clean_content):
            stem_part = match.group(1)
            suffix_part = match.group(2)
            if turkish_casefold(stem_part) in self._NOUNS_TI:
                continue

            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"Fiilden sonra gelen '{suffix_part}' baglactir ve ayri yazilmalidir ('{stem_part} {suffix_part}').",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    suggestion=f"{stem_part} {'da' if suffix_part in ('da', 'ta') else 'de'}",
                    context=match.group(0),
                )
            )

        for match in self._VERB_GERUND_DE.finditer(document.clean_content):
            stem_part = match.group(1)
            suffix_part = match.group(2)
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            correct_conj = "da" if suffix_part in ("da", "ta") else "de"
            findings.append(
                self.create_finding(
                    message=f"Zarf-fiilden sonra gelen baglac ayri yazilmalidir ('{stem_part} {correct_conj}').",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    suggestion=f"{stem_part} {correct_conj}",
                    context=match.group(0),
                )
            )

        # 2. Zamir + de baglaci
        for match in self._PRONOUN_DE.finditer(document.clean_content):
            pronoun = match.group(1)
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"Zamir ardindaki '{pronoun}de' baglaci ayri yazilmalidir ('{pronoun} de').",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    suggestion=f"{pronoun} de",
                    context=match.group(0),
                )
            )

        # 3. Bulunma durumunun yanlis ayrilmasi
        for match in self._SPLIT_LOCATIVE.finditer(document.clean_content):
            noun = match.group(1)
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"Bulunma durumu eki bitisik yazilmalidir ('{noun}de/{noun}da').",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )

        return findings


class KiBaglaciRule(Rule):
    """TD022: Fiillerden sonra gelen 'ki' baglacinin bitisik yazimi."""

    id = "TD022"
    name = "ki-baglaci"
    description = "Fiillerden ve baglac kaliplarindan sonra gelen 'ki' baglacinin bitisik yazimi."
    severity = Severity.ERROR
    suggestion = (
        "Fiillerden sonra gelen 'ki' baglacini ayri yazin ('gördüm ki', 'demek ki', 'yeter ki')."
    )

    # SOMBAHCEMI istisnalari (bitisik yazilan kaliplasmis ki'ler)
    _SOMBAHCEMI = frozenset(
        ["sanki", "oysaki", "mademki", "belki", "halbuki", "hâlbuki", "çünkü", "meğerki", "illaki"]
    )

    # Sifat/ilgi zamiri yapan bitisik -ki ekleri (evdeki, dünkü, bizimki vb.)
    _ATTACHED_KI_SUFFIXES = re.compile(
        r"(?:deki|daki|teki|taki|dünkü|bugünkü|yarınki|onunki|bizimki|seninki|benimki)$",
        re.IGNORECASE,
    )

    _VERB_KI = re.compile(
        r"\b(?:[a-zçğıöşü]+(?:dim|din|di|dik|diniz|diler|dım|dın|dı|dık|dınız|dılar|dum|dun|du|duk|düm|dün|dü|dük|tim|tin|ti|tik|tım|tın|tı|tık|tum|tun|tu|tuk|tüm|tün|tü|tük|miş|mış|muş|müş|yor|sin|sın|sun|sün|yim|yım|yik|yık|alım|elim|meli|malı)|demek|öyle|şöyle|yeter|kaldı|farzet|varsay|varsayalım)ki\b",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._VERB_KI.finditer(document.clean_content):
            matched_str = match.group(0)
            cf = turkish_casefold(matched_str)
            if cf in self._SOMBAHCEMI:
                continue
            if self._ATTACHED_KI_SUFFIXES.search(cf):
                continue

            stem_part = matched_str[:-2]
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"Fiilden sonra gelen 'ki' baglac olarak ayri yazilmalidir ('{stem_part} ki').",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    suggestion=f"{stem_part} ki",
                    context=matched_str,
                )
            )
        return findings


class BilesikAyriYazimRule(Rule):
    """TD023: Turkcede yaygin yapilan bilesik/ayri yazim ve imla yanlislari."""

    id = "TD023"
    name = "bilesik-ayri-yazim"
    description = "Sikca yapilan imla ve bilesik/ayri sozcuk hatalari ('herşey', 'bir çok' vb.)."
    severity = Severity.ERROR
    suggestion = "TDK imla kurallarina uygun dogru yazimi tercih edin."

    _ERRORS: dict[str, str] = {
        "herşey": "her şey",
        "hiçbirşey": "hiçbir şey",
        "birşey": "bir şey",
        "herkez": "herkes",
        "yalnış": "yanlış",
        "yanlız": "yalnız",
        "tabiki": "tabii ki",
        "farketmek": "fark etmek",
        "farketti": "fark etti",
        "farkedecek": "fark edecek",
        "terketmek": "terk etmek",
        "terketti": "terk etti",
        "haketmek": "hak etmek",
        "haketti": "hak etti",
        "ayrıyeten": "ayrıca",
        "orjinal": "orijinal",
        "klavuz": "kılavuz",
        "ünvan": "unvan",
    }

    _WORD_REGEX = re.compile(
        r"\b(?:herşey|hiçbirşey|birşey|herkez|yalnış|yanlız|tabiki|farketmek|farketti|farkedecek|terketmek|terketti|haketmek|haketti|ayrıyeten|orjinal|klavuz|ünvan)\b|\b(?:bir\s+çok|bir\s+kaç)\b",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._WORD_REGEX.finditer(document.clean_content):
            raw = match.group(0)
            cf = turkish_casefold(raw)
            if cf == "bir çok":
                correct = "birçok"
            elif cf == "bir kaç":
                correct = "birkaç"
            else:
                correct = self._ERRORS.get(cf, "")

            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"'{raw}' yazimi hatali; dogrusu '{correct}' olmalidir.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    suggestion=correct,
                    context=raw,
                )
            )
        return findings


class TirnakTutarsizligiRule(Rule):
    """TD024: Metin genelinde tirnak/kesme isaretlerinin tutarsiz kullanimi."""

    id = "TD024"
    name = "tirnak-tutarsizligi"
    description = (
        "Metinde hem duz tirnak (\" / ') hem de tipografik tirnak (“” / ’) karisik kullanimi."
    )
    severity = Severity.INFO
    suggestion = "Metin boyunca tutarli tek bir tirnak/kesme stili tercih edin."

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        content = document.clean_content

        has_straight_double = '"' in content
        has_curly_double = ("“" in content) or ("”" in content)

        if has_straight_double and has_curly_double:
            findings.append(
                self.create_finding(
                    message='Metinde hem duz cift tirnak (") hem de tipografik cift tirnak (“ ”) birlikte kullanilmis.',
                    line=1,
                    column=1,
                    end_line=1,
                    end_column=1,
                    suggestion="Belge boyunca tek bir cift tirnak bicimi tercih edin.",
                )
            )

        has_straight_single = "'" in content
        has_curly_single = ("’" in content) or ("‘" in content)

        if has_straight_single and has_curly_single:
            findings.append(
                self.create_finding(
                    message="Metinde hem duz kesme (') hem de tipografik kesme (’) birlikte kullanilmis.",
                    line=1,
                    column=1,
                    end_line=1,
                    end_column=1,
                    suggestion="Belge boyunca tek bir kesme isareti stili tercih edin.",
                )
            )

        return findings
