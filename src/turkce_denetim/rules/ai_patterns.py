"""Yapay zekâ metin kalıplarını tespit eden kurallar (TD008 - TD016)."""

from __future__ import annotations

import re

from turkce_denetim.casing import turkish_casefold
from turkce_denetim.document import offset_to_line_col
from turkce_denetim.models import Document, Finding, Severity
from turkce_denetim.rules.base import Rule


class ElbetteAcilisRule(Rule):
    """TD008: 'Elbette!', 'Kesinlikle!' gibi dalkavukça yapay zekâ açılışları."""

    id = "TD008"
    name = "elbette-açılış"
    description = (
        "Metin veya yanıt başındaki dalkavukça açılış ünlemleri ('Elbette!', 'Kesinlikle!')."
    )
    severity = Severity.WARN
    suggestion = "Dalkavukça açılış yerine doğrudan konuya veya bilgiye girin."

    # Yalnızca ünlemli açılış ('Elbette!') ya da asistan kalıbı ('Elbette, size yardımcı
    # olabilirim') yakalanır. 'Elbette, kapıyı ben açarım' ve 'Kesinlikle.' doğal yanıttır.
    _PATTERN = re.compile(
        r"^(?:\s*)(?:(?:elbette|kesinlikle|şüphesiz|tabii\s+ki)!|"
        r"(?:elbette|tabii\s+ki),\s+(?:size\s+|sana\s+)?(?:yardımcı|hemen|memnuniyetle|işte)\b)",
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
                    message=f"Metin başında dalkavukça yapay zekâ açılışı tespit edildi ('{match.group(0).strip()}').",
                    line=first_sentence.line,
                    column=first_sentence.column,
                    end_line=first_sentence.line,
                    end_column=first_sentence.column + len(match.group(0)),
                    context=first_sentence.text,
                )
            )
        return findings


class HarikaSoruRule(Rule):
    """TD009: 'Harika bir soru', 'Çok güzel bir soru' gibi yapay zekâ iltifat kalıpları."""

    id = "TD009"
    name = "harika-soru"
    description = "Yapay zekâ övgü/iltifat basmakalıpları ('Harika bir soru')."
    severity = Severity.WARN
    suggestion = "İltifat kalıbını silerek doğrudan yanıta başlayın."

    _PATTERN = re.compile(
        r"\b(?:harika|mükemmel|çok\s+güzel|yerinde)\s+bir\s+soru\b(?!-)|\bharika\s+bir\s+konuya\s+değindin\b",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"Yapay zekâ övgü kalıbı tespit edildi: '{match.group(0)}'.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class SonucOlarakKapanisRule(Rule):
    """TD010: Son paragrafın 'Sonuç olarak,' ile başlaması klişesi."""

    id = "TD010"
    name = "sonuç-olarak-kapanış"
    description = (
        "Kapanış paragrafının 'Sonuç olarak,', 'Özetle,' gibi basmakalıp bağlaçla açılması."
    )
    severity = Severity.INFO
    suggestion = "Basmakalıp bağlaç yerine kapanış düşüncesini doğrudan ana fikirle ifade edin."

    _PATTERN = re.compile(
        r"^(?:sonuç\s+olarak|özetle|özetlemek\s+gerekirse|toparlamak\s+gerekirse)[,:]",
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
                    message=f"Kapanış paragrafi basmakalıp '{match.group(0)}' ile başlıyor.",
                    line=first_sent.line,
                    column=first_sent.column,
                    end_line=first_sent.line,
                    end_column=first_sent.column + len(match.group(0)),
                    context=first_sent.text,
                )
            )
        return findings


class DunyasiMetaforuRule(Rule):
    """TD011: '...dünyası / dünyasında' soyut metafor kalıbı."""

    id = "TD011"
    name = "dünyası-metaforu"
    description = "'...dünyasında' kalıbı ('in the world of...' çevirisi)."
    severity = Severity.INFO
    suggestion = "'...dünyasında' yerine doğrudan alan adını yönelme veya bulunma ile belirtin (orn: 'yazılımda')."

    _PATTERN = re.compile(
        r"\b([a-zçğıöşüâîû]+)\s+dünyasın(?:da|dan|a|ı|ın)\b|\bdijital\s+dünyada\b",
        re.IGNORECASE,
    )

    # Yalnızca kliş haline gelmiş soyut alan adları taranır. 'Onun dünyasında', 'çocukların
    # dünyasında', 'iş dünyasında', 'Harry Potter dünyasında' gibi kullanımlar doğaldır.
    _DOMAINS = frozenset(
        [
            "yazılım",
            "teknoloji",
            "zekâ",
            "zeka",
            "dijital",
            "girişim",
            "girişimcilik",
            "pazarlama",
            "moda",
            "finans",
            "veri",
            "kodlama",
            "bilişim",
            "siber",
            "kripto",
            "medya",
            "e-ticaret",
        ]
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            prefix = match.group(1)
            if prefix and turkish_casefold(prefix) not in self._DOMAINS:
                continue

            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"'{match.group(0)}' soyut metaforu yapay zekâ metinlerinde sık görülür.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class YolculukMetaforuRule(Rule):
    """TD012: Soyut süreçler için 'yolculuk' metaforu kullanımı."""

    id = "TD012"
    name = "yolculuk-metaforu"
    description = "Soyut süreçler için klişeleşmiş 'yolculuk' ('journey') metaforu."
    severity = Severity.WARN
    suggestion = "'Yolculuk' metaforu yerine 'süreci', 'adımları' veya somut aşamaları yazın."

    _PATTERN = re.compile(
        r"\b(?:dijital\s+dönüşüm|öğrenme|kariyer|başarı|kodlama|gelişim|dönüşüm|keşif)\s+yolculuğ\w*",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"'{match.group(0)}' klişesi yapay zekâ metinlerinde soyut 'journey' çevirisidir.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class DerinlemesineRule(Rule):
    """TD013: 'Derinlemesine' abartı zarfı."""

    id = "TD013"
    name = "derinlemesine"
    description = "'Derinlemesine' ('in-depth / deeply') yapay zekâ dolgu zarfı."
    severity = Severity.INFO
    suggestion = "'Derinlemesine' yerine 'ayrıntılı biçimde', 'kapsamlıca' veya doğrudan eylemin kendisini yazın."

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
                    message=f"'{match.group(0)}' ifadesi yapay zekânın sik kullandığı abartılı bir dolgudur.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class KapsamliSekildeRule(Rule):
    """TD014: 'Kapsamlı bir şekilde' dolgusu."""

    id = "TD014"
    name = "kapsamlı-şekilde"
    description = "'Kapsamlı bir şekilde' ('comprehensively') dolgu kalıbı."
    severity = Severity.INFO
    suggestion = (
        "'...bir şekilde' yerine 'kapsamlıca', 'ayrıntılarıyla' veya doğrudan yalın eylem kullanın."
    )

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
                    message=f"'{match.group(0)}' kalıbı yerine 'kapsamlıca' veya 'ayrıntılarıyla' gibi yalın zarflar tercih edilebilir.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class UcluSifatDizisiRule(Rule):
    """TD015: Üçlü sıfat dizisi ('hızlı, güvenli ve etkili bir çözüm')."""

    id = "TD015"
    name = "üçlü-sıfat-dizisi"
    description = "Üçlü sıfat dizisi ('X, Y ve Z bir...' yapay zekâ sıralama üslubu)."
    severity = Severity.INFO
    suggestion = "Sıfat dizisini sadeleştirin veya somut gerekçelerle ayrı cümlelere bölün."

    # Üç sıfat + soyut bir ad ('hızlı, güvenli ve esnek bir çözüm'). 'Ali, Veli ve Ayşe bir
    # araya geldi' gibi sayımlar ad kümesi olmadığı için eşleşmez.
    _NOUNS = (
        "çözüm|yaklaşım|deneyim|platform|sistem|araç|yöntem|hizmet|ürün|süreç|yapı|"
        "mimari|uygulama|altyapı|çerçeve|kombinasyon|tasarım"
    )
    _PATTERN = re.compile(
        rf"\b([a-zçğıöşü]+),\s+([a-zçğıöşü]+)\s+ve\s+([a-zçğıöşü]+)\s+bir\s+({_NOUNS})\b",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"'{match.group(0)}' üçlü sıfat dizisi yapay zekânın tipik listeleme üslubudur.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class ParagrafAcilisTekrariRule(Rule):
    """TD016: Ardışık paragrafların aynı kalıpla başlaması."""

    id = "TD016"
    name = "paragraf-açılış-tekrarı"
    description = "Ardışık iki veya daha fazla paragrafın aynı sözcük veya kalıpla başlaması."
    severity = Severity.WARN
    suggestion = "Paragraf girişlerini çeşitlendirin; aynı bağlaç veya kalıpla başlamaktan kaçının."

    # Doğal metinde art arda paragrafı açabilen zamir ve gösterme sözcükleri; bunlar tek başına
    # tekrar sayılmaz (iki sözcüklü tekrar, 'Bu yüzden ... Bu yüzden ...', yine yakalanır).
    _COMMON_OPENERS = frozenset(
        ["bu", "şu", "o", "bir", "ben", "biz", "sen", "siz", "ve", "bunlar"]
    )

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
            if prev_w1 and w1 == prev_w1 and w1 not in self._COMMON_OPENERS:
                is_repeated = True
                repeated_str = words[0]
            elif prev_w2 and w2 == prev_w2:
                is_repeated = True
                repeated_str = f"{words[0]} {words[1]}"

            if is_repeated:
                findings.append(
                    self.create_finding(
                        message=f"Ardışık paragraflar aynı giriş kalıbıyla başlıyor: '{repeated_str}'.",
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
