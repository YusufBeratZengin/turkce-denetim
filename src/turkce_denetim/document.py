"""Belge yapılandırma, Markdown kod bloklarını maskeleme ve cümle/paragraf ayrıştırma."""

from __future__ import annotations

import re

from turkce_denetim.models import Document, Paragraph, Sentence

# Turkcede sik kullanilan ve cumle sonu sayilmamasi gereken kisaltmalar
_ABBREVIATIONS = frozenset(
    [
        "vb",
        "bkz",
        "örn",
        "dr",
        "prof",
        "doç",
        "av",
        "vs",
        "vd",
        "cad",
        "sok",
        "mah",
        "no",
        "mad",
        "sf",
        "s",
        "m.ö",
        "m.s",
        "tc",
        "yy",
        "cm",
        "mm",
        "km",
        "kg",
        "gr",
        "lt",
    ]
)

# Markdown bloklari ve inline kod kaliplari
_FENCE_START_RE = re.compile(r"^[ \t]*(?:```|~~~)")
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_HTML_COMMENT_RE = re.compile(r"<!--[\s\S]*?-->")

_WORD_TOKEN_RE = re.compile(r"[a-zçğıöşüA-ZÇĞİÖŞÜ0-9'’-]+")


def mask_markdown_code(content: str) -> str:
    """Markdown kod bloklarını ve satır içi kodları boşlukla maskeler.

    Böylece satır ve sütun numaraları tam olarak korunur, ancak kural motoru
    kod içindeki metinleri denetlemez.
    """

    # Once HTML yorumlarini ayni uzunlukta boslukla maskele
    def _mask_comment(match: re.Match[str]) -> str:
        s = match.group(0)
        # satir sonlarini koru
        return "".join("\n" if c == "\n" else " " for c in s)

    masked = _HTML_COMMENT_RE.sub(_mask_comment, content)

    # Satir satir fenced code blocks maskele
    lines = masked.split("\n")
    in_fence = False
    fence_char = ""
    clean_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not in_fence:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = True
                fence_char = stripped[:3]
                clean_lines.append(" " * len(line))
            else:
                # Satir ici kodlari maskele
                clean_line = _INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), line)
                clean_lines.append(clean_line)
        else:
            if stripped.startswith(fence_char):
                in_fence = False
                clean_lines.append(" " * len(line))
            else:
                clean_lines.append(" " * len(line))

    return "\n".join(clean_lines)


def offset_to_line_col(text: str, offset: int) -> tuple[int, int]:
    """Metin içindeki karakter indeksini (satır, sütun) ikilisine çevirir (1-tabanlı)."""
    offset = max(0, min(offset, len(text)))
    prefix = text[:offset]
    line = prefix.count("\n") + 1
    last_nl = prefix.rfind("\n")
    col = offset + 1 if last_nl == -1 else offset - last_nl
    return line, col


def _split_into_sentences(
    paragraph_text: str, para_start_offset: int, full_doc: str
) -> list[Sentence]:
    """Bir paragrafi Türkçe kurallarına ve kısaltmalarına göre cümlelere ayırır."""
    sentences: list[Sentence] = []
    text_len = len(paragraph_text)
    if text_len == 0:
        return sentences

    # Cumle sonu adaylarini bul
    # Nokta, soru isareti, unlem veya uc nokta ardindan bosluk ya da metin sonu
    pattern = re.compile(r"([.!?…]+)(?:\s+|$)")
    last_end = 0

    for match in pattern.finditer(paragraph_text):
        punct = match.group(1)
        punct_end = match.end(1)
        candidate = paragraph_text[last_end:punct_end].strip()

        # Kisaltma kontrolu: Eger nokta tek nokta ise ve onceki kelime kisaltmaysa bolme
        if punct == ".":
            # Onceki kelimeyi bul
            before = paragraph_text[last_end : match.start(1)].strip()
            prev_word = before.split()[-1] if before.split() else ""
            clean_prev = prev_word.lower().strip("()'\"[]")
            if clean_prev in _ABBREVIATIONS:
                continue

            # Sayi kontrolu: 3.14 veya 1. Madde gibi durumlar
            # Eger noktadan sonra rakam geliyorsa bolme
            if punct_end < text_len and paragraph_text[punct_end].isdigit():
                continue

        if not candidate:
            continue

        # Cumlenin paragraf ve belge icindeki konumunu bul
        c_start = paragraph_text.find(candidate, last_end)
        if c_start == -1:
            c_start = last_end
        c_end = c_start + len(candidate)

        doc_start = para_start_offset + c_start
        doc_end = para_start_offset + c_end

        start_line, start_col = offset_to_line_col(full_doc, doc_start)
        end_line, end_col = offset_to_line_col(full_doc, doc_end)

        words = _WORD_TOKEN_RE.findall(candidate)
        sentences.append(
            Sentence(
                text=candidate,
                line=start_line,
                column=start_col,
                end_line=end_line,
                end_column=end_col,
                words=words,
            )
        )
        last_end = match.end()

    # Kalan metin varsa (noktalamasiz biten son cumle/satir)
    remaining = paragraph_text[last_end:].strip()
    if remaining:
        c_start = paragraph_text.find(remaining, last_end)
        if c_start == -1:
            c_start = last_end
        c_end = c_start + len(remaining)
        doc_start = para_start_offset + c_start
        doc_end = para_start_offset + c_end

        start_line, start_col = offset_to_line_col(full_doc, doc_start)
        end_line, end_col = offset_to_line_col(full_doc, doc_end)
        words = _WORD_TOKEN_RE.findall(remaining)
        sentences.append(
            Sentence(
                text=remaining,
                line=start_line,
                column=start_col,
                end_line=end_line,
                end_column=end_col,
                words=words,
            )
        )

    return sentences


def parse_document(content: str, path: str | None = None) -> Document:
    """Ham metin içeriğini ayrıntılı Document nesnesine çevirir."""
    clean_content = mask_markdown_code(content)
    raw_lines = content.split("\n")
    clean_lines = clean_content.split("\n")

    # Paragraflari ayir: 2 veya daha fazla ardisik \n
    # Konum takibi icin re.finditer kullan
    # Maskelenmis kod satirlari yalniz bosluk icerir; bunlar paragraf ayiricisi sayilir.
    para_pattern = re.compile(r"([^\n]*\S[^\n]*(?:\n[^\n]*\S[^\n]*)*)")
    paragraphs: list[Paragraph] = []
    all_sentences: list[Sentence] = []

    for match in para_pattern.finditer(clean_content):
        para_text = match.group(0).strip()
        if not para_text:
            continue

        start_offset = match.start(0)
        end_offset = match.end(0)

        start_line, start_col = offset_to_line_col(clean_content, start_offset)
        end_line, end_col = offset_to_line_col(clean_content, end_offset)

        sentences = _split_into_sentences(para_text, start_offset, clean_content)
        paragraph = Paragraph(
            text=para_text,
            line=start_line,
            column=start_col,
            end_line=end_line,
            end_column=end_col,
            sentences=sentences,
        )
        paragraphs.append(paragraph)
        all_sentences.extend(sentences)

    return Document(
        raw_content=content,
        clean_content=clean_content,
        path=path,
        lines=raw_lines,
        clean_lines=clean_lines,
        paragraphs=paragraphs,
        sentences=all_sentences,
    )
