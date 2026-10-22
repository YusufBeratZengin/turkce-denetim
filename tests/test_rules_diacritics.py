"""Test rule messages and suggestions for correct Turkish diacritics."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from turkce_denetim.rules.registry import ALL_RULES

KNOWN_ASCII_MISTAKES = ["ayrica", "paragrafi", "oneri", "cumle"]


def test_rule_metadata_diacritics() -> None:
    """Ensure rule suggestions and descriptions do not contain known ASCII mistakes."""
    for rule_cls in ALL_RULES:
        rule = rule_cls()
        for attr in ("suggestion", "description"):
            value = getattr(rule, attr, "")
            assert value, f"Rule {rule.id} must define non-empty {attr}"
            lowered = value.lower()
            for mistake in KNOWN_ASCII_MISTAKES:
                assert mistake not in lowered, (
                    f"Rule {rule.id}.{attr} contains ASCII mistake '{mistake}': {value}"
                )


def test_rule_ast_diacritics() -> None:
    """Inspect AST of all rule implementations for messages and suggestions."""
    rules_dir = Path(__file__).resolve().parent.parent / "src" / "turkce_denetim" / "rules"

    inspected_calls = 0
    for py_file in rules_dir.glob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "create_finding":
                inspected_calls += 1
                for kw in node.keywords:
                    if kw.arg in ("message", "suggestion"):
                        # Extract string literals or formatted value parts
                        text = ast.unparse(kw.value).lower()
                        for mistake in KNOWN_ASCII_MISTAKES:
                            assert mistake not in text, (
                                f"{py_file.name}:{kw.value.lineno} {kw.arg} contains '{mistake}': {text}"
                            )

    assert inspected_calls > 0, "Should have inspected at least one create_finding call"


@pytest.mark.parametrize(
    "old_snippet", ["Kapanış paragrafi", "ayrica ekleyin", "oneri metni", "cumle sonu"]
)
def test_mistakes_detected_by_check(old_snippet: str) -> None:
    """Verify that the detection logic indeed flags the old ASCII mistakes."""
    lowered = old_snippet.lower()
    assert any(m in lowered for m in KNOWN_ASCII_MISTAKES)
