"""SARIF 2.1.0 bicimi dogrulama testleri."""

from __future__ import annotations

import json
import re
from pathlib import Path

from turkce_denetim.config import Config
from turkce_denetim.engine import analyze_text
from turkce_denetim.formatters.sarif_formatter import format_sarif
from turkce_denetim.rules.registry import ALL_RULES


def test_sarif_schema_and_required_fields() -> None:
    text = "Herşey yolunda ve bu noktada inceleme yapıldı."
    config = Config()
    result = analyze_text(text, config, path="ornek.md")

    sarif_output = format_sarif([result])
    data = json.loads(sarif_output)

    # SARIF 2.1.0 zorunlu ust alanlar
    assert (
        data["$schema"]
        == "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
    )
    assert data["version"] == "2.1.0"
    assert "runs" in data
    assert len(data["runs"]) == 1

    run = data["runs"][0]
    # Tool ve Driver alanlari
    assert "tool" in run
    driver = run["tool"]["driver"]
    assert driver["name"] == "turkce-denetim"
    assert "semanticVersion" in driver
    assert "rules" in driver
    assert len(driver["rules"]) >= 20

    # Kural yapisi
    assert len(driver["rules"]) == 25
    for r in driver["rules"]:
        assert "id" in r
        assert "name" in r
        assert "shortDescription" in r
        assert "defaultConfiguration" in r
        assert not any(c in r["name"] for c in "çğıöşüÇĞİÖŞÜ")  # kebab-case ASCII
        assert "_" not in r["name"]  # must be kebab-case, not snake_case

    # Sonuclar (Results)
    assert "results" in run
    assert len(run["results"]) >= 1

    first_result = run["results"][0]
    for res_item in run["results"]:
        assert "ruleId" in res_item
        assert res_item["level"] in ("error", "warning", "note")
        assert "message" in res_item
        assert "locations" in res_item
        assert len(res_item["locations"]) >= 1

    loc = first_result["locations"][0]["physicalLocation"]
    assert "artifactLocation" in loc
    assert loc["artifactLocation"]["uri"] == "ornek.md"
    assert "region" in loc
    region = loc["region"]
    assert "startLine" in region
    assert "startColumn" in region
    assert region["startLine"] >= 1


def test_readme_rules_table_matches_registry() -> None:
    """Ensure every rule ID and name documented in README matches the rule registry."""
    registry_rules = {cls.id: cls.name for cls in ALL_RULES}

    for doc_name in ("README.md", "README.tr.md"):
        doc_path = Path(__file__).resolve().parent.parent / doc_name
        content = doc_path.read_text(encoding="utf-8")

        # Match rows like: | `TD001` | `ile-birlikte-asiri` |
        matches = re.findall(r"\|\s*`(TD\d{3})`\s*\|\s*`([^`]+)`\s*\|", content)
        doc_rules = dict(matches)

        assert len(doc_rules) == len(ALL_RULES), (
            f"Expected {len(ALL_RULES)} rules in {doc_name} table, found {len(doc_rules)}"
        )

        for rule_id, rule_name in doc_rules.items():
            assert rule_id in registry_rules, f"Rule {rule_id} in {doc_name} is not registered"
            assert registry_rules[rule_id] == rule_name, (
                f"Rule {rule_id} name mismatch in {doc_name}: registry '{registry_rules[rule_id]}' != {doc_name} '{rule_name}'"
            )
