"""Yazım ve tipografi kuralları (TD021 - TD024)."""

from __future__ import annotations

import re

from turkce_denetim.casing import turkish_casefold
from turkce_denetim.document import offset_to_line_col
from turkce_denetim.models import Document, Finding, Severity
from turkce_denetim.rules.base import Rule


class DeDaBaglaciRule(Rule):
    """TD021: 'de/da' bağlacının bitişik yazımı veya bulunma halinin yanlış ayrılması."""

    id = "TD021"
    name = "de-da-bağlacı"
    description = (
        "'de/da' bağlacının fiillerden sonra bitişik yazılması veya bulunma halinin ayrı yazılması."
    )
    severity = Severity.ERROR
    suggestion = "Bağlaç olan 'de/da' her zaman ayrı yazılır ve 'te/ta' biçimini almaz. Bulunma durumu eki '-de/-da' ise bitişik yazılır."

    # Yaygin cekimli fiiller ardindan bitisen -de/-da/-te/-ta (yalniz yuksek guvenli durumlar)
    _COMMON_VERBS = (
        "gitti|geldi|yaptı|oldu|aldı|verdi|gördü|bildi|kaldı|çıktı|dedi|konuştu|"
        "buldu|yazdı|okudu|duydu|anladı|geçti|bitti|başladı|istedi|sordu|etti|durdu|baktı|sevdi"
    )
    _VERB_PAST_DE = re.compile(
        rf"\b({_COMMON_VERBS})(de|da|te|ta)\b",
        re.IGNORECASE,
    )
    _VERB_GERUND_DE = re.compile(
        r"\b([a-zçğıöşü]+(?:ıp|ip|up|üp))(ta|te)\b",
        re.IGNORECASE,
    )

    # Zamir ardindan bitisen baglac: yalnizca ozne ile uyumlu birinci/ikinci tekil kisi
    # gecmis zaman fiili izlediginde ('bende geldim'). 'Bende bir sorun var' bulunma halidir.
    _PRONOUN_DE = re.compile(
        r"\b(?:(ben)de\s+[a-zçğıöşü]+?[dt][ıiuü]m|(sen)de\s+[a-zçğıöşü]+?[dt][ıiuü]n)\b",
        re.IGNORECASE,
    )

    # Yanlis ayrilmis bulunma hali: fiil birinci kisi ise ('ev de kaldim') 'de' baglac olamaz,
    # ozne ben/biz oldugundan yer bildirir. 'Ev de kalabalikti' gibi ucuncu kisi cumleler dogaldir.
    _SPLIT_LOCATIVE = re.compile(
        r"\b(ev|ofis|okul|sokak|oda|masa|yatak|araba|şehir|köy)\s+(?:de|da|te|ta)\s+"
        r"(?:kal|dur|otur|çalış|yat|uyu|büyü|yaşa)[a-zçğıöşü]*?(?:[dt][ıiuü][mk]|yorum|yoruz|ırım|irim)\b",
        re.IGNORECASE,
    )

    # 'grupta', 'kulupte', 'tipte' gibi -p ile biten adlar zarf-fiil degildir.
    _P_NOUNS = frozenset(
        [
            "grup",
            "kulüp",
            "tip",
            "tüp",
            "ip",
            "kup",
            "çip",
            "klip",
            "slip",
            "hip",
            "şip",
            "set",
            "kamp",
            "stop",
            "shop",
            "top",
            "kep",
            "pip",
            "wip",
            "dip",
            "lip",
            "zip",
            "scoop",
            "loop",
            "hop",
            "drop",
            "flip",
            "chip",
            "ship",
            "trip",
            "cup",
        ]
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
                    message=f"Fiilden sonra gelen '{suffix_part}' bağlaçtır ve ayrı yazılmalıdır ('{stem_part} {suffix_part}').",
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
            if turkish_casefold(stem_part) in self._P_NOUNS:
                continue
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            correct_conj = "da" if suffix_part in ("da", "ta") else "de"
            findings.append(
                self.create_finding(
                    message=f"Zarf-fiilden sonra gelen bağlaç ayrı yazılmalıdır ('{stem_part} {correct_conj}').",
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
            pronoun = match.group(1) or match.group(2)
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"Zamir ardındaki '{pronoun}de' bağlacı ayrı yazılmalıdır ('{pronoun} de').",
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
                    message=f"Bulunma durumu eki bitişik yazılmalıdır ('{noun}de/{noun}da').",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )

        return findings


class KiBaglaciRule(Rule):
    """TD022: Fiillerden sonra gelen 'ki' bağlacının bitişik yazımı."""

    id = "TD022"
    name = "ki-bağlacı"
    description = "Fiillerden ve bağlaç kalıplarından sonra gelen 'ki' bağlacının bitişik yazımı."
    severity = Severity.ERROR
    suggestion = (
        "Fiillerden sonra gelen 'ki' bağlacını ayrı yazın ('gördüm ki', 'demek ki', 'yeter ki')."
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
                    message=f"Fiilden sonra gelen 'ki' bağlaç olarak ayrı yazılmalıdır ('{stem_part} ki').",
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
    """TD023: Türkçede yaygın yapılan bileşik/ayrı yazım ve imla yanlışları."""

    id = "TD023"
    name = "bileşik-ayrı-yazım"
    description = "Sıkça yapılan imla ve bileşik/ayrı sözcük hataları ('herşey', 'bir çok' vb.)."
    severity = Severity.ERROR
    suggestion = "TDK imla kurallarına uygun doğru yazımı tercih edin."

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
                    message=f"'{raw}' yazımı hatalı; doğrusu '{correct}' olmalıdır.",
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
    """TD024: Metin genelinde tırnak/kesme işaretlerinin tutarsız kullanımı."""

    id = "TD024"
    name = "tırnak-tutarsızlığı"
    description = (
        "Metinde hem duz tirnak (\" / ') hem de tipografik tirnak (“” / ’) karisik kullanimi."
    )
    severity = Severity.INFO
    suggestion = "Metin boyunca tutarlı tek bir tırnak/kesme stili tercih edin."

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        content = document.clean_content

        has_straight_double = '"' in content
        has_curly_double = ("“" in content) or ("”" in content)

        if has_straight_double and has_curly_double:
            findings.append(
                self.create_finding(
                    message='Metinde hem düz çift tırnak (") hem de tipografik çift tırnak (“ ”) birlikte kullanılmış.',
                    line=1,
                    column=1,
                    end_line=1,
                    end_column=1,
                    suggestion="Belge boyunca tek bir çift tırnak biçimi tercih edin.",
                )
            )

        has_straight_single = "'" in content
        has_curly_single = ("’" in content) or ("‘" in content)

        if has_straight_single and has_curly_single:
            findings.append(
                self.create_finding(
                    message="Metinde hem düz kesme (') hem de tipografik kesme (’) birlikte kullanılmış.",
                    line=1,
                    column=1,
                    end_line=1,
                    end_column=1,
                    suggestion="Belge boyunca tek bir kesme işareti stili tercih edin.",
                )
            )

        return findings
