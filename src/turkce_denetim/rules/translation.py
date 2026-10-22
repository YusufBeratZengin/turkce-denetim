"""Çeviri kokusu kalıplarını tespit eden kurallar (TD001 - TD007)."""

from __future__ import annotations

import re

from turkce_denetim.casing import turkish_casefold
from turkce_denetim.document import offset_to_line_col
from turkce_denetim.models import Document, Finding, Severity
from turkce_denetim.rules.base import Rule


class IleBirlikteAsiriRule(Rule):
    """TD001: '...ile birlikte' kalıbının aşırı/gereksiz kullanımı."""

    id = "TD001"
    name = "ile-birlikte-aşırı"
    description = "'...ile birlikte' dolgu kalıbı ('along with' çevirisi)."
    severity = Severity.INFO
    suggestion = "'ile birlikte' yerine 'ile', 'bunun yanında', 'ayrica' veya yalın ek kullanın."

    # Yalnizca ayri yazilan 'ile birlikte' taranir. 'Bununla birlikte', 'arkadaslarimla birlikte'
    # ve 'Ayse ile birlikte' dogal Turkcedir.
    _PATTERN = re.compile(r"\b([^\W\d_]+)\s+ile\s+birlikte\b", re.IGNORECASE)

    _PRONOUNS = frozenset(["ben", "sen", "o", "biz", "siz", "onlar", "bu", "şu", "bunlar"])
    _ABSTRACT_ENDINGS = ("ler", "lar", "lik", "lık", "luk", "lük", "me", "ma", "mesi", "ması", "ış", "iş", "uş", "üş")

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for match in self._PATTERN.finditer(document.clean_content):
            previous = match.group(1)
            folded = turkish_casefold(previous)
            if folded in self._PRONOUNS:
                continue
            if previous[0].isupper():
                # Cumle ortasinda buyuk harf ozel addir ('Ayse ile birlikte'). Cumle basinda ise
                # yalniz soyut ad eki tasiyan sozcukler ('Gelismeler ile birlikte') yakalanir.
                before = document.clean_content[: match.start()].rstrip()
                at_sentence_start = not before or before[-1] in ".!?…:"
                if not (at_sentence_start and folded.endswith(self._ABSTRACT_ENDINGS)):
                    continue
            matched_text = match.group(0)
            start_l, start_c = offset_to_line_col(document.clean_content, match.start())
            end_l, end_c = offset_to_line_col(document.clean_content, match.end())
            findings.append(
                self.create_finding(
                    message=f"'{matched_text}' kalıbı çeviri kokusu taşıyabilir; daha yalın bağlaçlar tercih edilebilir.",
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
    description = "'Bu noktada' dolgu ifadesi ('at this point' kalıp çevirisi)."
    severity = Severity.INFO
    suggestion = "'Bu noktada' yerine 'burada', 'bu aşamada' veya doğrudan konuya giren bir ifade tercih edin."

    # Yalnizca cumle basindaki 'Bu noktada' soylem dolgusudur; 'geldigimiz bu noktada'
    # gibi cumle ortasi kullanimlar dogaldir.
    _PATTERN = re.compile(r"^bu\s+noktada\b", re.IGNORECASE)

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for sentence in document.sentences:
            match = self._PATTERN.search(sentence.text)
            if not match:
                continue
            findings.append(
                self.create_finding(
                    message="Cümle başında 'Bu noktada' dolgu ifadesi tespit edildi.",
                    line=sentence.line,
                    column=sentence.column,
                    end_line=sentence.line,
                    end_column=sentence.column + len(match.group(0)),
                    context=match.group(0),
                )
            )
        return findings


class GununSonundaRule(Rule):
    """TD003: 'günün sonunda' basmakalıp çevirisi."""

    id = "TD003"
    name = "günün-sonunda"
    description = "'Günün sonunda' basmakalıp deyimi ('at the end of the day' çevirisi)."
    severity = Severity.WARN
    suggestion = (
        "'Günün sonunda' yerine 'sonuçta', 'eninde sonunda', 'nihayetinde' veya 'özünde' kullanın."
    )

    # Soylem isareti olarak kullanilan 'Gunun sonunda, ...' yakalanir. 'Gunun sonunda eve
    # dondum' gibi gercek zaman bildiren kullanim dogaldir; yalnizca virgul ya da genel yargi
    # oznesi (herkes, her sey, onemli olan...) izleyen cumle basi kullanimlar taranir.
    _PATTERN = re.compile(
        r"^günün\s+sonunda(?=,|\s+(?:herkes|her\s+şey|hiç|önemli|asıl|mesele|tüm|bütün|"
        r"hepimiz|insan|kimse|sonuç)\b)",
        re.IGNORECASE,
    )

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for sentence in document.sentences:
            match = self._PATTERN.search(sentence.text)
            if not match:
                continue
            findings.append(
                self.create_finding(
                    message="'Günün sonunda' ifadesi birebir İngilizce çeviridir ('at the end of the day').",
                    line=sentence.line,
                    column=sentence.column,
                    end_line=sentence.line,
                    end_column=sentence.column + len(match.group(0)),
                    context=match.group(0),
                )
            )
        return findings


class OnemlidirKiRule(Rule):
    """TD004: '...önemlidir ki' kalıbı."""

    id = "TD004"
    name = "önemlidir-ki"
    description = (
        "'...önemlidir ki' veya 'şunu belirtmek önemlidir ki' çevirisi ('it is important that')."
    )
    severity = Severity.WARN
    suggestion = "'...önemlidir ki' yerine '...belirtmek gerekir', '...önem taşır' veya doğrudan yargı cümlesi kurun."

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
                    message=f"'{match.group(0)}' kalıbı İngilizce 'it is important that' çevirisidir.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=match.group(0),
                )
            )
        return findings


class KonusundaYigilmasiRule(Rule):
    """TD005: Bir cümlede '...konusunda' yığılması."""

    id = "TD005"
    name = "konusunda-yığılması"
    description = (
        "Aynı cümlede birden çok '...konusunda / konusundaki' yığılması ('regarding' çevirisi)."
    )
    severity = Severity.WARN
    suggestion = (
        "'konusunda' yerine '-e dair', '-le ilgili' veya doğrudan yönelme/belirtme eki kullanın."
    )

    _PATTERN = re.compile(r"\bkonusunda(?:ki)?\b", re.IGNORECASE)

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for sentence in document.sentences:
            matches = list(self._PATTERN.finditer(sentence.text))
            if len(matches) >= 2:
                findings.append(
                    self.create_finding(
                        message=f"Cümle içinde 'konusunda' kalıbı {len(matches)} kez tekrarlandı.",
                        line=sentence.line,
                        column=sentence.column,
                        end_line=sentence.end_line,
                        end_column=sentence.end_column,
                        context=sentence.text,
                    )
                )
        return findings


class SahipOlmakRule(Rule):
    """TD006: Gereksiz 'sahip olmak' ('have' çevirisi)."""

    id = "TD006"
    name = "sahip-olmak"
    description = (
        "İyelik eki yerine İngilizce 'have' karşılığı kullanılan gereksiz 'sahip olmak' yapısı."
    )
    severity = Severity.WARN
    suggestion = (
        "'...sahiptir / sahip olmak' yerine '...vardır', '...bulunur' veya iyelik eki kullanın."
    )

    # 'özelliklere sahiptir', 'hıza sahip bir telefon', 'özelliklere sahip olan'.
    # 'Sahip olmak istediğim', 'sahip çıkmak' gibi doğal kullanımlar taranmaz.
    _PATTERN = re.compile(
        r"\b[a-zçğıöşü]+[ea]\s+sahip(?:tir|ti|tirler|\s+(?:bir|olan|olduğu|olarak))\b",
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
                    message=f"'{matched_text}' yapısı 'have' çevirisi kokusu taşıyor olabilir; iyelik eki ('...vardır') tercih edilebilir.",
                    line=start_l,
                    column=start_c,
                    end_line=end_l,
                    end_column=end_c,
                    context=matched_text,
                )
            )
        return findings


class EdilgenYigilmasiRule(Rule):
    """TD007: Cümlede aşırı edilgen çatı yoğunluğu."""

    id = "TD007"
    name = "edilgen-yığılması"
    description = (
        "Tek bir cümlede 3 veya daha fazla edilgen eylem bulunması (edilgen çatı yığılması)."
    )
    severity = Severity.WARN
    suggestion = "Edilgen fiilleri etken çatıya dönüştürerek cümlenin öznesini belirginleştirin."

    # Gerçek edilgen gövdesi: -Il / -n / -lAn edilgenlik eki + zaman eki. Tek harflik köklü
    # '-il' ('bildi', 'gülüyor', 'sunuyor') etken fiillerle karışır, bu yüzden en az iki harflik
    # kök istenir; l ile biten kökte -n eki ('alındı', 'bulundu') ayrıca ve -lAn eki
    # ('onaylandı') ayrıca denetlenir.
    _TENSE = (
        r"(?:makta|mekte|maktadır|mektedir|mıştır|miştir|muştur|müştür|mış|miş|muş|müş|"
        r"dı|di|du|dü|tı|ti|tu|tü|acak|ecek|ıyor|iyor|uyor|üyor)(?:dır|dir|dur|dür|lar|ler)?"
    )
    _PASSIVE_RE = re.compile(
        rf"\b(?:[a-zçğıöşü]{{2,}}(?:ıl|il|ul|ül|lan|len)|[a-zçğıöşü]+(?:lın|lin|lun|lün)){_TENSE}\b",
        re.IGNORECASE,
    )

    # '-lan' ile biten ama edilgen olmayan temel fiiller ('kullandı', 'kullanıyor').
    _ACTIVE_PREFIXES = ("kullan", "uygulan", "yaslan", "dolan", "bulan", "kızılan")

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for sentence in document.sentences:
            lower_sent = turkish_casefold(sentence.text)
            matches = self._PASSIVE_RE.findall(lower_sent)
            filtered = [
                m
                for m in matches
                if not (m.startswith(self._ACTIVE_PREFIXES) and "ıl" not in m[6:])
            ]
            if len(filtered) >= 3:
                findings.append(
                    self.create_finding(
                        message=f"Cümlede {len(filtered)} edilgen fiil yığılması tespit edildi ({', '.join(filtered)}).",
                        line=sentence.line,
                        column=sentence.column,
                        end_line=sentence.end_line,
                        end_column=sentence.end_column,
                        context=sentence.text,
                    )
                )
        return findings
