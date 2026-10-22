"""Ceviri kokusu kaliplarini tespit eden kurallar (TD001 - TD007)."""

from __future__ import annotations

import re

from turkce_denetim.casing import turkish_casefold
from turkce_denetim.document import offset_to_line_col
from turkce_denetim.models import Document, Finding, Severity
from turkce_denetim.rules.base import Rule


class IleBirlikteAsiriRule(Rule):
    """TD001: '...ile birlikte' kalibinin asiri/gereksiz kullanimi."""

    id = "TD001"
    name = "ile-birlikte-asiri"
    description = "'...ile birlikte' dolgu kalibi ('along with' cevirisi)."
    severity = Severity.WARN
    suggestion = "'ile birlikte' yerine 'ile', 'bunun yaninda', 'ayrica' veya yalin ek kullanin."

    _PATTERN = re.compile(
        r"\b(?:[a-zçğıöşü]+(?:ile|'le|'la|le|la)|bununla|şununla|onunla)\s+birlikte\b",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            matched_text = match.group(0)
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"'{matched_text}' kalibi ceviri kokusu tasiyabilir; daha yalin baglaclar tercih edilebilir.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=matched_text,
                )
            )
        return findings


class BuNoktadaRule(Rule):
    """TD002: 'bu noktada' dolgu ifadesi."""

    id = "TD002"
    name = "bu-noktada"
    description = "'Bu noktada' dolgu ifadesi ('at this point' kalip cevirisi)."
    severity = Severity.WARN
    suggestion = "'Bu noktada' yerine 'burada', 'bu asamada' veya dogrudan konuya giren bir ifade tercih edin."

    _PATTERN = re.compile(r"\bbu\s+noktada\b", re.IGNORECASE)

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message="'Bu noktada' dolgu ifadesi tespit edildi.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class GununSonundaRule(Rule):
    """TD003: 'günün sonunda' basmakalip cevirisi."""

    id = "TD003"
    name = "gunun-sonunda"
    description = "'Günün sonunda' basmakalip deyimi ('at the end of the day' cevirisi)."
    severity = Severity.WARN
    suggestion = "'Günün sonunda' yerine 'sonucta', 'eninde sonunda', 'nihayetinde' veya 'ozunde' kullanin."

    _PATTERN = re.compile(r"\bgünün\s+sonunda\b", re.IGNORECASE)

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message="'Günün sonunda' ifadesi birebir Ingilizce ceviridir ('at the end of the day').",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class OnemlidirKiRule(Rule):
    """TD004: '...önemlidir ki' kalibi."""

    id = "TD004"
    name = "onemlidir-ki"
    description = "'...önemlidir ki' veya 'şunu belirtmek önemlidir ki' cevirisi ('it is important that')."
    severity = Severity.WARN
    suggestion = "'...önemlidir ki' yerine '...belirtmek gerekir', '...onem tasir' veya dogrudan yargi cumlesi kurun."

    _PATTERN = re.compile(
        r"\b(?:(?:şunu\s+)?(?:belirtmek|vurgulamak|hatırlatmak)\s+)?önemlidir\s+ki\b",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"'{match.group(0)}' kalibi Ingilizce 'it is important that' cevirisidir.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class KonusundaYigilmasiRule(Rule):
    """TD005: Bir cumlede '...konusunda' yigilmasi."""

    id = "TD005"
    name = "konusunda-yigilmasi"
    description = "Ayni cumlede birden cok '...konusunda / konusundaki' yigilmasi ('regarding' cevirisi)."
    severity = Severity.WARN
    suggestion = "'konusunda' yerine '-e dair', '-le ilgili' veya dogrudan yonelme/belirtme eki kullanin."

    _PATTERN = re.compile(r"\bkonusunda(?:ki)?\b", re.IGNORECASE)

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for sentence in document.sentences:
            matches = list(self._PATTERN.finditer(sentence.text))
            if len(matches) >= 2:
                findings.append(
                    self.create_finding(
                        message=f"Cumle icinde 'konusunda' kalibi {len(matches)} kez tekrarlandi.",
                        line=sentence.line,
                        column=sentence.column,
                        end_line=sentence.end_line,
                        end_column=sentence.end_column,
                        context=sentence.text,
                    )
                )
        return findings


class SahipOlmakRule(Rule):
    """TD006: Gereksiz 'sahip olmak' ('have' cevirisi)."""

    id = "TD006"
    name = "sahip-olmak"
    description = "Iyelik eki yerine Ingilizce 'have' karsiligi kullanilan gereksiz 'sahip olmak' yapisi."
    severity = Severity.WARN
    suggestion = "'...sahiptir / sahip olmak' yerine '...vardir', '...bulunur' veya iyelik eki kullanin."

    # 'özelliklere sahiptir', 'hıza sahip bir telefon', 'sahip olmak'
    _PATTERN = re.compile(
        r"\b(?:[a-zçğıöşü]+[ea]\s+sahip(?:tir|ti|tirler)?|sahip\s+(?:olmak|olduğu|olan|olması|olup|olurlar|olur|oldu|olacaktır))\b",
        re.IGNORECASE,
    )

    # Istisnalar: hak sahibi, ev sahibi, eser sahibi gibi gercek mulkiyet/hukuki sahiplikler
    _EXCLUDE_RE = re.compile(
        r"\b(?:hak|ev|arsa|iş|eser|telif|mülk|pay|kart)\s+sahip",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            matched_text = match.group(0)
            # Baglam kontrolu (hemen oncesi bir istisna mi?)
            start_idx = max(0, match.start() - 20)
            prefix = document.clean_content[start_idx : match.end()]
            if self._EXCLUDE_RE.search(prefix):
                continue

            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"'{matched_text}' yapisi 'have' cevirisi kokusu tasiyor olabilir; iyelik eki ('...vardir') tercih edilebilir.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=matched_text,
                )
            )
        return findings


class EdilgenYigilmasiRule(Rule):
    """TD007: Cumlede asiri edilgen cati yogunlugu."""

    id = "TD007"
    name = "edilgen-yigilmasi"
    description = "Tek bir cumlede 3 veya daha fazla edilgen eylem bulunmasi (edilgen cati yigilmasi)."
    severity = Severity.WARN
    suggestion = "Edilgen fiilleri etken catiya donusturerek cumlenin oznesini belirginlestirin."

    _PASSIVE_RE = re.compile(
        r"\b[a-zçğıöşü]+(?:ıl|il|ul|ül|ın|in|un|ün|lan|len)(?:makta|mekte|maktadır|mektedir|mıştır|miştir|muştur|müştür|mış|miş|muş|müş|dı|di|du|dü|tı|ti|tu|tü|acak|ecek|ıyor|iyor|uyor|üyor)(?:dır|dir|dur|dür|lar|ler)?\b",
        re.IGNORECASE,
    )

    _NOUN_EXCLUSIONS = frozenset([
        "toplantı", "ayrıntı", "bağlantı", "sıkıntı", "yaşantı", "görüntü",
        "akıntı", "özentü", "sızıntı", "gezinti", "çıkıntı", "kalıntı",
    ])

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for sentence in document.sentences:
            lower_sent = turkish_casefold(sentence.text)
            matches = self._PASSIVE_RE.findall(lower_sent)
            filtered = [m for m in matches if m not in self._NOUN_EXCLUSIONS]
            if len(filtered) >= 3:
                findings.append(
                    self.create_finding(
                        message=f"Cumlede {len(filtered)} edilgen fiil yigilmasi tespit edildi ({', '.join(filtered)}).",
                        line=sentence.line,
                        column=sentence.column,
                        end_line=sentence.end_line,
                        end_column=sentence.end_column,
                        context=sentence.text,
                    )
                )
        return findings
