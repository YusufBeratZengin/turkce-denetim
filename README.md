# turkce-denetim

> A rule-based (no LLM, zero runtime dependencies) Turkish text linter and CLI for detecting AI-generated text smells, translation artifacts, and orthographic inconsistencies.

[![CI](https://github.com/YusufBeratZengin/turkce-denetim/actions/workflows/ci.yml/badge.svg)](https://github.com/YusufBeratZengin/turkce-denetim/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/turkce-denetim.svg)](https://pypi.org/project/turkce-denetim/)
[![Python Version](https://img.shields.io/pypi/pyversions/turkce-denetim.svg)](https://pypi.org/project/turkce-denetim/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[Türkçe Dokümantasyon için tıklayınız (README.tr.md)](README.tr.md)

---

<p align="center">
  <img src="docs/demo.svg" alt="turkce-denetim terminal demo" width="860">
</p>

---

## Why turkce-denetim?

- **Zero Runtime Dependencies & Deterministic**: Runs entirely on the Python Standard Library (Python >= 3.10) with instant startup, zero cloud API fees or tokens, and 100% reproducible results free from LLM drift or hallucination.
- **Engineered for Turkish Morphology**: Built specifically for Turkish linguistics—native dotted/dotless I (`İ/i` and `I/ı`) casing, custom suffix stripping for repetition detection, and curated rules flagging calques ("sahip olmak", "...ile birlikte", "...noktasında") and LLM tropes ("Elbette!", "...dünyasında", "yolculuk").
- **Developer-Native & CI-Ready**: Comes with ANSI color terminal diagnostics, machine-readable JSON, native SARIF 2.1.0 export for GitHub Code Scanning, pre-commit integration, and a normalized Naturalness Score (0-100).

---

## Quick Start

Install via pip and lint your Markdown or text files immediately:

```bash
# Install the package
pip install turkce-denetim

# Lint a file or directory
turkce-denetim document.md
```

---

## Important Disclaimer

> **This tool does not prove that a text was authored by artificial intelligence.**
> It identifies recurring stylistic patterns, translation calques, and formulaic phrasing that frequently appear in machine-generated or mechanically translated Turkish content. Human writers can naturally use these patterns, and machine-generated text can be edited to avoid them. The naturalness score is an advisory metric, not a definitive verdict.

---

## Features

- **Zero Runtime Dependencies**: Built entirely with the Python Standard Library (Python >= 3.10).
- **25 Specialized Rules**: Categorized across translation calques, AI-specific tropes, readability indicators, and high-confidence orthography.
- **Accurate Turkish Case Handling**: Native support for dotted and dotless I (`İ/i` and `I/ı`) across all casing transformations.
- **Turkish Stemmer**: Suffix stripper designed for Turkish agglutinative morphology to detect proximity stem repetitions without external NLP packages.
- **Markdown-Aware**: Masks fenced code blocks (```` ``` ```` and `~~~`), HTML comments (`<!-- ... -->`), and inline code (`` `...` ``) with spaces so that code contents are ignored while exact line and column coordinates are preserved.
- **Multiple Output Formats**: Human-readable terminal output with ANSI colors, machine-parsable JSON (`--format json`), and SARIF 2.1.0 (`--format sarif`) for GitHub Code Scanning.
- **Naturalness Score (0-100)**: Transparent, normalized metric measuring the stylistic density of detected patterns per 100 words.
- **Configurable**: Configurable via `pyproject.toml` (`[tool.turkce-denetim]`) or command-line options (`--disable`, `--min-severity`).

---

## Usage

### Command Line Interface

```bash
# Check all Markdown and text files in the current directory
turkce-denetim

# Check a specific file or folder
turkce-denetim document.md
turkce-denetim docs/

# Same thing as a module (when the script is not on PATH)
python -m turkce_denetim document.md

# Read from standard input
cat draft.txt | turkce-denetim -

# Output structured JSON
turkce-denetim document.md --format json

# Export SARIF for GitHub Code Scanning
turkce-denetim docs/ --format sarif > results.sarif

# Disable specific rules
turkce-denetim document.md --disable TD001,TD005

# Filter by minimum severity (info, warn, error)
turkce-denetim document.md --min-severity warn

# Print only the naturalness score (0-100)
turkce-denetim document.md --score-only

# List all available rules
turkce-denetim --list-rules
```

### CLI Options

| Option | Type | Default | Description |
|---|---|---|---|
| `targets` | Positional | `.` | Files, directories, or `-` for stdin. |
| `-f, --format` | Choice | `text` | Output format: `text`, `json`, or `sarif`. |
| `-d, --disable` | String | None | Comma-separated rule IDs to skip (e.g. `TD001,TD003`). |
| `-s, --min-severity`| Choice | `info` | Minimum severity threshold: `info`, `warn`, or `error`. |
| `-c, --config` | Path | None | Path to custom TOML configuration file. |
| `--no-color` | Flag | False | Disable ANSI color codes in terminal output. |
| `--score-only` | Flag | False | Print only the numerical naturalness score. |
| `--list-rules` | Flag | False | List all available linting rules (ID, name, severity, description). |
| `-v, --version` | Flag | | Show program version. |

### Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success: no error-level findings detected (text is clean or contains only info/warn suggestions). |
| `1` | Linting errors found: one or more `error`-severity findings detected (e.g. spelling or grammar violations). |
| `2` | Usage, configuration, or I/O error: invalid CLI arguments, unreadable files, or malformed TOML configuration. |

### Live Demo Output

```bash
$ turkce-denetim examples/bad.md --no-color
examples/bad.md:1:1: warn  [TD008] Metin başında dalkavukça yapay zekâ açılışı tespit edildi ('Elbette!').
    öneri: Dalkavukça açılış yerine doğrudan konuya veya bilgiye girin.
examples/bad.md:1:74: info  [TD001] 'gelişmesi ile birlikte' kalıbı çeviri kokusu taşıyabilir; daha yalın bağlaçlar tercih edilebilir.
    öneri: 'ile birlikte' yerine 'ile', 'bunun yanında', 'ayrıca' veya yalın ek kullanın.
examples/bad.md:3:1: info  [TD002] Cümle başında 'Bu noktada' dolgu ifadesi tespit edildi.
    öneri: 'Bu noktada' yerine 'burada', 'bu aşamada' veya doğrudan konuya giren bir ifade tercih edin.
examples/bad.md:3:12: warn  [TD012] 'dijital dönüşüm yolculuğumuz' klişesi yapay zekâ metinlerinde soyut 'journey' çevirisidir.
    öneri: 'Yolculuk' metaforu yerine 'süreci', 'adımları' veya somut aşamaları yazın.
examples/bad.md:3:75: info  [TD013] 'derinlemesine incelemek' ifadesi yapay zekânın sık kullandığı abartılı bir dolgudur.
    öneri: 'Derinlemesine' yerine 'ayrıntılı biçimde', 'kapsamlıca' veya doğrudan eylemin kendisini yazın.
examples/bad.md:3:103: warn  [TD004] 'önemlidir ki' kalıbı İngilizce 'it is important that' çevirisidir.
    öneri: '...önemlidir ki' yerine '...belirtmek gerekir', '...önem taşır' veya doğrudan yargı cümlesi kurun.
examples/bad.md:5:14: error [TD023] 'herşey' yazımı hatalı; doğrusu 'her şey' olmalıdır.
    öneri: her şey

--- Denetim Özeti ---
Taranan belge sayısı : 1
Toplam kelime sayısı : 39
Bulgular             : 1 hata, 3 uyarı, 3 bilgi (toplam 7)
Kural dağılımı       : TD001: 1, TD002: 1, TD004: 1, TD008: 1, TD012: 1, TD013: 1, TD023: 1
Doğallık Puanı       : 60.0 / 100 (Orta (Belirgin yapay zekâ veya çeviri kokusu))
```

---

## Python API

You can integrate `turkce-denetim` directly into your Python scripts and services:

```python
from turkce_denetim import Config, analyze_text

content = "Bu noktada konuyu derinlemesine incelemek çok önemlidir ki sonuç alalım."
config = Config(min_severity="warn")

result = analyze_text(content, config)

print(f"Word count : {result.word_count}")
print(f"Naturalness: {result.naturalness_score} / 100")

for finding in result.findings:
    print(f"L{finding.line}:{finding.column} [{finding.rule_id}] {finding.message}")
    if finding.suggestion:
        print(f"  Suggestion: {finding.suggestion}")
```

---

## Pre-commit Integration

Add `turkce-denetim` to your `.pre-commit-config.yaml` to lint markdown and text files automatically before each commit:

```yaml
repos:
  - repo: https://github.com/YusufBeratZengin/turkce-denetim
    rev: v0.1.0
    hooks:
      - id: turkce-denetim
```

---

## GitHub Actions CI Integration

To inspect pull requests and upload findings directly into GitHub Code Scanning (SARIF tab):

```yaml
name: Text Quality

on:
  pull_request:
    branches: [main]

jobs:
  lint-text:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install turkce-denetim
        run: pip install turkce-denetim

      - name: Run linter and generate SARIF
        run: turkce-denetim . --format sarif > results.sarif
        continue-on-error: true

      - name: Upload SARIF report
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

---

## Rules Catalog

The linter implements 25 rules across 4 primary categories:

### 1. Translation Patterns (Çeviri Kalıpları)

| ID | Name | Severity | Problematic Example | Suggestion |
|---|---|---|---|---|
| `TD001` | `ile-birlikte-asiri` | `info` | "Teknolojinin gelişmesi ile birlikte..." | Use simple case endings ("gelişmesiyle") or conjunctions. |
| `TD002` | `bu-noktada` | `info` | "Bu noktada dikkat etmeliyiz." | Use "burada", "bu aşamada", or enter directly into the topic. |
| `TD003` | `gunun-sonunda` | `warn` | "Günün sonunda, karar verildi." | Literal calque of "at the end of the day". Use "sonuçta" or "nihayetinde". Plain time reference ("Günün sonunda eve döndük") is not flagged. |
| `TD004` | `onemlidir-ki` | `warn` | "Şunu belirtmek önemlidir ki bu bir hatadır." | Calque of "it is important that". Use "...belirtmek gerekir" or "...önem taşır". |
| `TD005` | `konusunda-yigilmasi` | `warn` | "Veri güvenliği konusunda ve mimari konusundaki..." | Avoid stacking "...konusunda" ("regarding"). Use "-e dair" or direct case endings. |
| `TD006` | `sahip-olmak` | `warn` | "Bu cihaz yüksek bir hıza sahiptir." | Calque of "to have". Use possessive suffixes or "vardır / bulunur". |
| `TD007` | `edilgen-yigilmasi` | `warn` | "Planlar yapıldı, bütçe onaylandı ve görevler dağıtıldı." | 3+ passive verbs in one sentence. Rewrite with active voice. |

### 2. AI Patterns (Yapay Zekâ Kalıpları)

| ID | Name | Severity | Problematic Example | Suggestion |
|---|---|---|---|---|
| `TD008` | `elbette-acilis` | `warn` | "Elbette! Size yardımcı olabilirim." | Sycophantic AI greeting. Start directly with the substance. |
| `TD009` | `harika-soru` | `warn` | "Harika bir soru sordunuz." | Conversational flattery trope. Remove and answer directly. |
| `TD010` | `sonuc-olarak-kapanis` | `info` | "Sonuç olarak, bu adımlar başarımızı artıracaktır." | Formulaic concluding opener. Start the closing paragraph with the core thought. |
| `TD011` | `dunyasi-metaforu` | `info` | "Yapay zekâ dünyasında her gün yeni bir adım..." | Calque of "in the world of...". Use direct locative: "yapay zekâda", "yazılımda". |
| `TD012` | `yolculuk-metaforu` | `warn` | "Dijital dönüşüm yolculuğumuz başladı." | Cliché metaphor for processes. Use "süreci", "adımları", or "deneyimi". |
| `TD013` | `derinlemesine` | `info` | "Bu konuyu derinlemesine inceleyelim." | Hyperbolic AI adverb. Use "ayrıntılı biçimde" or simply "inceleyelim". |
| `TD014` | `kapsamli-sekilde` | `info` | "Raporu kapsamlı bir şekilde hazırladık." | Padding phrase. Use "kapsamlıca" or direct verbs. |
| `TD015` | `uclu-sifat-dizisi` | `info` | "Hızlı, esnek ve güvenli bir çözüm." | Formulaic list of three adjectives. Distribute claims across arguments. |
| `TD016` | `paragraf-acilis-tekrari` | `warn` | Paragraphs 1 and 2 both beginning with "Ayrıca..." | Diversify paragraph transitions. |

### 3. Readability & Structure (Okunabilirlik)

| ID | Name | Severity | Problematic Example | Suggestion |
|---|---|---|---|---|
| `TD017` | `cumle-uzunlugu` | `warn` | Sentence exceeding 35 words. | Split into two or more independent sentences. |
| `TD018` | `paragraf-uzunlugu` | `info` | Paragraph exceeding 120 words. | Break into sub-points or distinct paragraphs. |
| `TD019` | `yakin-kelime-tekrari` | `warn` | Same root (e.g. "yaz-") repeated 3+ times in one sentence. | Use pronouns, synonyms, or restructure. |
| `TD020` | `virgul-zinciri` | `info` | Single sentence containing 5+ commas. | Break sentence or use bullet points / semicolons. |
| `TD025` | `veya-baglac-tekrari` | `info` | Single sentence containing 3+ "ve / veya" conjunctions. | Use comma lists or split the sentence. |

### 4. Spelling & Typography (Yazım ve Tipografi)

| ID | Name | Severity | Problematic Example | Suggestion |
|---|---|---|---|---|
| `TD021` | `de-da-baglaci` | `error` | "Gittide söylemedi" / "Ev de kaldım" | Conjunction "de/da" is written separately; locative suffix is attached. |
| `TD022` | `ki-baglaci` | `error` | "Gördümki her şey yolunda" / "Demekki" | Conjunction "ki" following inflected verbs is written separately. |
| `TD023` | `bilesik-ayri-yazim` | `error` | "herşey", "hiçbirşey", "bir çok", "farketmek" | Standard Turkish orthography ("her şey", "birçok", "fark etmek"). |
| `TD024` | `tirnak-tutarsizligi` | `info` | Mixing ASCII quotes (`"`) and typographic curly quotes (`“”`). | Maintain consistent quotation typography throughout the document. |

---

## Naturalness Score Formula

The Naturalness Score is a bounded metric ($0.0 - 100.0$) that measures pattern density per 100 words.

1. Each finding receives a weight based on severity:
   - **Error**: $8.0$ penalty points
   - **Warning**: $3.0$ penalty points
   - **Info**: $1.0$ penalty point
2. The total penalty is normalized against total word count $W$ with a 50-word floor:
   $$\text{Penalty} = \frac{\sum \text{Weights} \times 100}{\max(W, 50)}$$
3. The final score is bounded and rounded to one decimal place:
   $$\text{Score} = \max(0.0, \min(100.0, 100.0 - \text{Penalty}))$$

### Score Interpretation

| Range | Rating | Typical Profile |
|---|---|---|
| **90.0 – 100.0** | High Naturalness | Fluent, natural Turkish with zero or negligible pattern findings. |
| **75.0 – 89.9** | Good | Clear writing with minor isolated stylistic padding. |
| **50.0 – 74.9** | Moderate | Noticeable AI phrasing or translation artifacts. Needs revision. |
| **0.0 – 49.9** | Low | Heavy machine translation calques, repetitive tropes, or orthographic errors. |

---

## Configuration

You can configure `turkce-denetim` in your repository's `pyproject.toml` file under `[tool.turkce-denetim]`:

```toml
[tool.turkce-denetim]
# Minimum reporting level ("info", "warn", "error")
min_severity = "info"

# Rules to disable
disable = ["TD001", "TD014"]

# Thresholds
max_sentence_words = 35
max_paragraph_words = 120
max_commas_per_sentence = 5
max_passive_per_sentence = 3
min_word_repetition = 3
```

---

## FAQ & Limitations

### Does a low score prove a text was written by an LLM?
**No.** `turkce-denetim` identifies stylistic habits, translation calques, and repetition metrics commonly seen in model outputs and mechanical translations. Skilled human writers occasionally use these phrases, and AI-generated text can be post-edited to achieve a 100 score. The Naturalness Score is an advisory diagnostic tool, not an authorship watermark.

### Can it run completely offline and in air-gapped systems?
**Yes.** `turkce-denetim` has zero external runtime dependencies and makes zero network calls. It runs locally and securely on any machine with Python >= 3.10.

### What file formats are supported?
`turkce-denetim` processes Markdown (`.md`) and plain text (`.txt`) files. When parsing Markdown, code blocks (```` ``` ````, `~~~`), HTML comments (`<!-- ... -->`), and inline code (`` `...` ``) are masked with whitespace so that code snippets do not trigger false positives while preserving line and column coordinates.

### How does it handle Turkish dotted and dotless I?
Turkish uppercase `I` becomes lowercase `ı`, and uppercase `İ` becomes lowercase `i`. Standard library lowercase routines often mishandle this depending on system locale. `turkce-denetim` incorporates dedicated, locale-independent Turkish casing and casefolding algorithms.

---

## Contributing

Contributions are very welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for full setup instructions, testing guidelines, and code style standards.

```bash
# Clone and setup local development environment
git clone https://github.com/YusufBeratZengin/turkce-denetim.git
cd turkce-denetim
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
pip install -e ".[dev]"

# Run tests and linting
pytest
ruff check .
ruff format --check .
mypy src tests
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Yusuf Berat Zengin
