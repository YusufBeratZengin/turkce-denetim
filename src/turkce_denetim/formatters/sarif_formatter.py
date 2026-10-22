"""SARIF 2.1.0 cikti bicimlendiricisi (GitHub code scanning ile tam uyumlu)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from turkce_denetim import __version__
from turkce_denetim.models import Severity
from turkce_denetim.rules.registry import ALL_RULES

if TYPE_CHECKING:
    from turkce_denetim.models import AnalysisResult

_SARIF_LEVEL_MAP = {
    Severity.ERROR: "error",
    Severity.WARN: "warning",
    Severity.INFO: "note",
}


def _rule_to_sarif_descriptor(rule_cls: type[Any]) -> dict[str, Any]:
    level = _SARIF_LEVEL_MAP.get(rule_cls.severity, "warning")
    return {
        "id": rule_cls.id,
        "name": rule_cls.name.replace("-", "_"),
        "shortDescription": {
            "text": rule_cls.description,
        },
        "fullDescription": {
            "text": f"{rule_cls.description} Öneri: {rule_cls.suggestion}",
        },
        "help": {
            "text": rule_cls.suggestion,
            "markdown": f"**Öneri**: {rule_cls.suggestion}",
        },
        "defaultConfiguration": {
            "level": level,
        },
        "properties": {
            "tags": ["turkish", "style", "ai-detection"],
        },
    }


def format_sarif(results: list[AnalysisResult], indent: int = 2) -> str:
    """Denetim sonuclarini SARIF 2.1.0 standardina uygun JSON dizgisine cevirir."""
    # Kural fihristi
    rules_list = [_rule_to_sarif_descriptor(r) for r in ALL_RULES]
    rule_id_to_index = {r["id"]: idx for idx, r in enumerate(rules_list)}

    sarif_results: list[dict[str, Any]] = []

    for res in results:
        raw_path = res.path or "stdin"
        # Windows ters egik cizgilerini SARIF URI standardina (/) cevir
        file_uri = Path(raw_path).as_posix()

        for finding in res.findings:
            rule_idx = rule_id_to_index.get(finding.rule_id)
            level = _SARIF_LEVEL_MAP.get(finding.severity, "note")

            result_entry: dict[str, Any] = {
                "ruleId": finding.rule_id,
                "level": level,
                "message": {
                    "text": finding.message,
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": file_uri,
                            },
                            "region": {
                                "startLine": max(1, finding.line),
                                "startColumn": max(1, finding.column),
                                "endLine": max(1, finding.end_line),
                                "endColumn": max(1, finding.end_column),
                            },
                        }
                    }
                ],
            }

            if rule_idx is not None:
                result_entry["ruleIndex"] = rule_idx

            sarif_results.append(result_entry)

    sarif_doc = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "turkce-denetim",
                        "semanticVersion": __version__,
                        "informationUri": "https://github.com/YusufBeratZengin/turkce-denetim",
                        "rules": rules_list,
                    }
                },
                "results": sarif_results,
            }
        ],
    }

    return json.dumps(sarif_doc, ensure_ascii=False, indent=indent)
