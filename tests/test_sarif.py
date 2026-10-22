"""SARIF 2.1.0 bicimi dogrulama testleri."""

from __future__ import annotations

import json

from turkce_denetim.config import Config
from turkce_denetim.engine import analyze_text
from turkce_denetim.formatters.sarif_formatter import format_sarif


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
    rule_0 = driver["rules"][0]
    assert "id" in rule_0
    assert "shortDescription" in rule_0
    assert "defaultConfiguration" in rule_0

    # Sonuclar (Results)
    assert "results" in run
    assert len(run["results"]) >= 1

    first_result = run["results"][0]
    assert "ruleId" in first_result
    assert first_result["level"] in ("error", "warning", "note")
    assert "message" in first_result
    assert "locations" in first_result

    loc = first_result["locations"][0]["physicalLocation"]
    assert "artifactLocation" in loc
    assert loc["artifactLocation"]["uri"] == "ornek.md"
    assert "region" in loc
    region = loc["region"]
    assert "startLine" in region
    assert "startColumn" in region
    assert region["startLine"] >= 1
