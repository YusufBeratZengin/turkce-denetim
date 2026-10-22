# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-22

### Added
- Rule engine with zero runtime dependencies (Python standard library only).
- 25 lint rules categorized into four linguistic domains:
  - Translation smell patterns (`TD001` - `TD007`): excessive "...ile birlikte", "bu noktada", "günün sonunda", "...önemlidir ki", "...konusunda" clustering, calque "sahip olmak", and passive voice density.
  - AI pattern smells (`TD008` - `TD016`): sycophantic openers ("Elbette!"), flattery openers ("Harika bir soru"), formulaic conclusion transitions ("Sonuç olarak,"), "...dünyasında" abstract metaphors, "yolculuk" metaphors, "derinlemesine" hyperbolic adverbs, "kapsamlı bir şekilde" fillers, triple adjective chains, and repeated paragraph openers.
  - Readability metrics (`TD017` - `TD020`, `TD025`): sentence length thresholds, paragraph length thresholds, close word stem repetition, comma chains, and conjunction clustering.
  - Spelling and typography (`TD021` - `TD024`): safe heuristics for "de/da" and "ki" conjunctions, common compound/separated spelling errors ("her şey", "birçok", "fark etmek"), and quotation mark consistency.
- Accurate Turkish case conversion helpers (`turkish_lower`, `turkish_upper`, `turkish_casefold`, `turkish_title`) properly handling dotted/dotless I (`İ/i` and `I/ı`).
- Rule-based Turkish suffix stripper (`stemmer`) for stem extraction and proximity repetition detection.
- Markdown parser with fence code block (```` ``` ```` and `~~~`) and inline code masking that preserves exact line and column coordinates.
- Output formatters:
  - Human-readable text formatter with ANSI color support.
  - Machine-readable JSON formatter (`--format json`).
  - SARIF 2.1.0 formatter (`--format sarif`) compliant with GitHub Code Scanning.
- Naturalness Score (0-100) calculation based on normalized weighted finding density per 100 words.
- Configuration loading from `pyproject.toml` (`[tool.turkce-denetim]`) with CLI flag overrides.
- Command-line interface (`turkce-denetim`) supporting files, directories, and standard input (`-`).
- Automated CI matrix testing Python 3.10 and 3.12 with pytest, ruff, and mypy (strict mode).
