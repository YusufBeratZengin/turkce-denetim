"""Belge yapilandirma ve Markdown kod blogu atlama testleri."""

from __future__ import annotations

from turkce_denetim.document import mask_markdown_code, parse_document


def test_mask_markdown_fenced_blocks() -> None:
    text = (
        "Giris cumlesi burada yer aliyor.\n"
        "```python\n"
        "def selam():\n"
        "    print('Elbette!')\n"
        "```\n"
        "Kapanis cumlesi ise buradadir."
    )
    masked = mask_markdown_code(text)
    # Satir sayisi ayni kalmali
    assert masked.count("\n") == text.count("\n")
    # Kod blogunun ici boslukla maskelenmeli
    assert "def selam():" not in masked
    assert "Elbette!" not in masked
    # Disindaki metinler yerinde kalmali
    assert "Giris cumlesi burada yer aliyor." in masked
    assert "Kapanis cumlesi ise buradadir." in masked


def test_mask_inline_code() -> None:
    text = "Burada `print('Elbette!')` kodu vardir."
    masked = mask_markdown_code(text)
    assert "`print('Elbette!')`" not in masked
    assert len(masked) == len(text)
    assert "Burada" in masked
    assert "kodu vardir." in masked


def test_mask_html_comments() -> None:
    text = "Giriş metni.\n<!-- Gizli yorum satırı\nve devamı -->\nSonuç metni."
    masked = mask_markdown_code(text)
    assert "Gizli yorum" not in masked
    assert masked.count("\n") == text.count("\n")
    assert "Giriş metni." in masked
    assert "Sonuç metni." in masked


def test_parse_document_paragraphs_and_sentences() -> None:
    text = (
        "Birinci paragraf. Prof. Dr. Ahmet Bey geldi.\n\n"
        "İkinci paragraf burada. Başka bir cümle daha var.\n\n"
        "```bash\necho test\n```\n\n"
        "Üçüncü paragraf sonudur."
    )
    doc = parse_document(text, path="test.md")
    assert doc.path == "test.md"
    assert len(doc.paragraphs) >= 3
    # Kisaltmalar cumleyi bolmemeli (Prof. Dr.)
    first_p = doc.paragraphs[0]
    # 'Birinci paragraf.' ve 'Prof. Dr. Ahmet Bey geldi.' -> 2 cumle
    assert len(first_p.sentences) == 2
    assert "Prof. Dr. Ahmet Bey" in first_p.sentences[1].text


def test_parse_document_numbers_and_unpunctuated_lines() -> None:
    text = "Sürüm 3.14 yayınlandı. Bu son satır noktalamasız"
    doc = parse_document(text)
    assert len(doc.sentences) == 2
    assert "3.14" in doc.sentences[0].text
    assert doc.sentences[1].text == "Bu son satır noktalamasız"


def test_parse_empty_document() -> None:
    doc = parse_document("")
    assert doc.word_count == 0
    assert len(doc.sentences) == 0
    assert len(doc.paragraphs) == 0
