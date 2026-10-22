"""Yapay zeka metin kaliplarini tespit eden kurallar (TD008 - TD016)."""

from __future__ import annotations

import re

from turkce_denetim.casing import turkish_casefold
from turkce_denetim.document import offset_to_line_col
from turkce_denetim.models import Document, Finding, Severity
from turkce_denetim.rules.base import Rule


class ElbetteAcilisRule(Rule):
    """TD008: 'Elbette!', 'Kesinlikle!' gibi dalkavukca yapay zeka acilislari."""

    id = "TD008"
    name = "elbette-acilis"
    description = "Metin veya yanit basindaki dalkavukca acilis unlemleri ('Elbette!', 'Kesinlikle!')."
    severity = Severity.WARN
    suggestion = "Dalkavukca acilis yerine dogrudan konuya veya bilgiye girin."

    _PATTERN = re.compile(
        r"^(?:\s*)(?:elbette|kesinlikle|şüphesiz|tabii\s+ki)[!.,]",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        if not document.sentences:
            return findings

        # Belgenin ilk cumlesini veya ilk paragraf baslangicini kontrol et
        first_sentence = document.sentences[0]
        match = self._PATTERN.search(first_sentence.text)
        if match:
            findings.append(
                self.create_finding(
                    message=f"Metin basinda dalkavukca yapay zeka acilisi tespit edildi ('{match.group(0).strip()}').",
                    line=first_sentence.line,
                    column=first_sentence.column,
                    end_line=first_sentence.line,
                    end_column=first_sentence.column + len(match.group(0)),
                    context=first_sentence.text,
                )
            )
        return findings


class HarikaSoruRule(Rule):
    """TD009: 'Harika bir soru', 'Cok guzel bir soru' gibi yapay zeka iltifat kaliplari."""

    id = "TD009"
    name = "harika-soru"
    description = "Yapay zeka ovgu/iltifat basmakaliplari ('Harika bir soru')."
    severity = Severity.WARN
    suggestion = "Iltifat kalibini silerek dogrudan yanita baslayin."

    _PATTERN = re.compile(
        r"\b(?:harika|mükemmel|çok\s+güzel|yerinde)\s+bir\s+soru\b|\bharika\s+bir\s+konuya\s+değindin\b",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"Yapay zeka ovgu kalibi tespit edildi: '{match.group(0)}'.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class SonucOlarakKapanisRule(Rule):
    """TD010: Son paragrafin 'Sonuc olarak,' ile baslamasi klisesi."""

    id = "TD010"
    name = "sonuc-olarak-kapanis"
    description = "Kapanis paragrafinin 'Sonuc olarak,', 'Ozetle,' gibi basmakalip baglacla acilmasi."
    severity = Severity.INFO
    suggestion = "Basmakalip baglac yerine kapanis dusuncesini dogrudan ana fikirle ifade edin."

    _PATTERN = re.compile(
        r"^(?:sonuç\s+olarak|özetle|özetlemek\s+gerekirse|toparlamak\s+gerekirse|kısacası)[,:]",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        # En az iki paragraf varsa ve son paragraf bu kalipla basliyorsa
        if len(document.paragraphs) < 2:
            return findings

        last_para = document.paragraphs[-1]
        if not last_para.sentences:
            return findings

        first_sent = last_para.sentences[0]
        match = self._PATTERN.search(first_sent.text.strip())
        if match:
            findings.append(
                self.create_finding(
                    message=f"Kapanis paragrafi basmakalip '{match.group(0)}' ile basliyor.",
                    line=first_sent.line,
                    column=first_sent.column,
                    end_line=first_sent.line,
                    end_column=first_sent.column + len(match.group(0)),
                    context=first_sent.text,
                )
            )
        return findings


class DunyasiMetaforuRule(Rule):
    """TD011: '...dunyasi / dunyasinda' soyut metafor kalibi."""

    id = "TD011"
    name = "dunyasi-metaforu"
    description = "'...dünyasında' kalibi ('in the world of...' cevirisi)."
    severity = Severity.INFO
    suggestion = "'...dünyasında' yerine dogrudan alan adini yonelme veya bulunma ile belirtin (orn: 'yazilimda')."

    _PATTERN = re.compile(
        r"\b([a-zçğıöşüâîû]+)\s+dünyasın(?:da|dan|a|ı|ın)\b|\bdijital\s+dünyada\b",
        re.IGNORECASE,
    )

    _EXCLUDED = frozenset(["iş", "hayvanlar", "üçüncü", "yeraltı", "çocuk"])

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            prefix = match.group(1)
            if prefix and turkish_casefold(prefix) in self._EXCLUDED:
                continue

            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"'{match.group(0)}' soyut metaforu yapay zeka metinlerinde sik gorulur.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class YolculukMetaforuRule(Rule):
    """TD012: Soyut surecler icin 'yolculuk' metaforu kullanimi."""

    id = "TD012"
    name = "yolculuk-metaforu"
    description = "Soyut surecler icin kliselesmis 'yolculuk' ('journey') metaforu."
    severity = Severity.WARN
    suggestion = "'Yolculuk' metaforu yerine 'sureci', 'adimlari' veya somut asamalari yazin."

    _PATTERN = re.compile(
        r"\b(?:dijital\s+dönüşüm|öğrenme|kariyer|başarı|hayat|kodlama|gelişim|dönüşüm|keşif)\s+yolculuğ(?:u|unda|una|unun|undan)\b|\bbir\s+yolculuğa\s+(?:çık|adım|başla)\w*\b",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"'{match.group(0)}' klisesi yapay zeka metinlerinde soyut 'journey' cevirisidir.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class DerinlemesineRule(Rule):
    """TD013: 'Derinlemesine' abarti zarfi."""

    id = "TD013"
    name = "derinlemesine"
    description = "'Derinlemesine' ('in-depth / deeply') yapay zeka dolgu zarfi."
    severity = Severity.INFO
    suggestion = "'Derinlemesine' yerine 'ayrintili bicimde', 'kapsamlica' veya dogrudan eylemin kendisini yazin."

    _PATTERN = re.compile(
        r"\bderinlemesine\s+(?:incele|ele\s+al|analiz|bak|araştır|öğren|değerlendir|anlat)\w*\b|\bderinlemesine\s+bir\s+(?:şekilde|bakış|inceleme|analiz)\b",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"'{match.group(0)}' ifadesi yapay zekanin sik kullandigi abartili bir dolgudur.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class KapsamliSekildeRule(Rule):
    """TD014: 'Kapsamli bir sekilde' dolgusu."""

    id = "TD014"
    name = "kapsamli-sekilde"
    description = "'Kapsamlı bir şekilde' ('comprehensively') dolgu kalibi."
    severity = Severity.INFO
    suggestion = "'...bir şekilde' yerine 'kapsamlica', 'ayrintilariyla' veya dogrudan yalin eylem kullanin."

    _PATTERN = re.compile(
        r"\b(?:kapsamlı|detaylı|ayrıntılı)\s+bir\s+şekilde\b",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"'{match.group(0)}' kalibi yerine 'kapsamlica' veya 'ayrintilariyla' gibi yalin zarflar tercih edilebilir.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class UcluSifatDizisiRule(Rule):
    """TD015: Uclu sifat dizisi ('hizli, guvenli ve etkili bir cozum')."""

    id = "TD015"
    name = "uclu-sifat-dizisi"
    description = "Uclu sifat dizisi ('X, Y ve Z bir...' yapay zeka siralama uslubu)."
    severity = Severity.INFO
    suggestion = "Sifat dizisini sadelestirin veya somut gerekcelerle ayri cumlelere bolun."

    _PATTERN = re.compile(
        r"\b([a-zçğıöşü]+),\s+([a-zçğıöşü]+)\s+ve\s+([a-zçğıöşü]+)\s+bir\s+([a-zçğıöşü]+)\b",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"'{match.group(0)}' uclu sifat dizisi yapay zekanin tipik listeleme uslubudur.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class ParagrafAcilisTekrariRule(Rule):
    """TD016: Ardisik paragraflarin ayni kalipla baslamasi."""

    id = "TD016"
    name = "paragraf-acilis-tekrari"
    description = "Ardisik iki veya daha fazla paragrafin ayni sozcuk veya kalipla baslamasi."
    severity = Severity.WARN
    suggestion = "Paragraf girislerini cesitlendirin; ayni baglac veya kalipla baslamaktan kacinin."

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        if len(document.paragraphs) < 2:
            return findings

        prev_w1 = ""
        prev_w2 = ""
        for p in document.paragraphs:
            if not p.sentences:
                continue
            first_sentence = p.sentences[0]
            words = first_sentence.words
            if not words:
                continue

            w1 = turkish_casefold(words[0])
            w2 = turkish_casefold(f"{words[0]} {words[1]}") if len(words) >= 2 else w1

            # Tekrarlayan ilk kelime veya ilk iki kelime
            is_repeated = False
            repeated_str = ""
            if prev_w1 and w1 == prev_w1:
                is_repeated = True
                repeated_str = words[0]
            elif prev_w2 and w2 == prev_w2:
                is_repeated = True
                repeated_str = f"{words[0]} {words[1]}"

            if is_repeated:
                findings.append(
                    self.create_finding(
                        message=f"Ardisik paragraflar ayni giris kalibiyla basliyor: '{repeated_str}'.",
                        line=p.line,
                        column=p.column,
                        end_line=p.line,
                        end_column=p.column + len(repeated_str),
                        context=first_sentence.text,
                    )
                )
            prev_w1 = w1
            prev_w2 = w2

        return findings
