# Contributing to turkce-denetim

Thank you for your interest in contributing to `turkce-denetim`. This project provides a rule-based, zero-runtime-dependency linter for identifying translation artifacts and AI text smells in Turkish.

## Development Setup

Requirements:
- Python >= 3.10
- Git

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/YusufBeratZengin/turkce-denetim.git
cd turkce-denetim
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
pip install --upgrade pip
pip install -e ".[dev]"
```

## Adding a New Rule

All rules are pure Python classes inheriting from `turkce_denetim.rules.base.Rule`.

1. Choose a unique identifier (`TDxxx`) and a kebab-case name.
2. Implement the rule in the appropriate module under `src/turkce_denetim/rules/`:
   - `translation.py`: Translation artifacts and calques.
   - `ai_patterns.py`: Machine-generated formulaic phrasing.
   - `readability.py`: Sentence length, paragraph structure, repetition.
   - `spelling.py`: High-confidence orthography and typography.
3. Define the following attributes:
   - `id`: e.g. `"TD026"`
   - `name`: e.g. `"yeni-kural"`
   - `description`: Single sentence describing the issue.
   - `severity`: `Severity.INFO`, `Severity.WARN`, or `Severity.ERROR`
   - `suggestion`: Practical guidance for the writer.
4. Implement the `check(self, document: Document) -> list[Finding]` method.
5. Register the rule in `src/turkce_denetim/rules/registry.py`.
6. Add unit tests in `tests/`:
   - Positive test cases (sentences that must trigger the rule).
   - Negative test cases (natural sentences that must not trigger false positives).
7. Document the new rule in both `README.md` and `README.tr.md`.

## Quality Standards

Before opening a pull request, ensure all linters, type checks, and tests pass:

```bash
# Code formatting check
ruff format --check .

# Linting
ruff check .

# Static type checking
mypy src tests

# Unit test suite
pytest
```

## Commit Guidelines

Use Conventional Commits with concise, explanatory English messages:

- `feat(rules): implement TD026 ...`
- `fix(spelling): handle edge case in ...`
- `test(casing): add coverage for ...`
- `docs: update rule table with ...`

## Reporting False Positives

Reducing false positives on idiomatic, natural Turkish is an ongoing priority. If an existing rule incorrectly flags legitimate phrasing:
1. Open a **False Positive Report** using the issue template.
2. Provide the minimal natural sentence that triggered the issue and a brief justification.
3. If possible, suggest an improved regex heuristic or negative guard test case.

## Determinism and AI Policy

- `turkce-denetim` is fundamentally rule-based with zero external runtime dependencies and zero LLM calls.
- PRs proposing new rules must use pure Python standard library regex or morphological heuristics.
- Any AI-assisted code contributions must be thoroughly tested, readable, and verified by the author.

## Security

Please do not report security vulnerabilities in public GitHub issues. Follow the confidential reporting instructions in [SECURITY.md](SECURITY.md).

## Code of Conduct

All contributors and maintainers are expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md).
