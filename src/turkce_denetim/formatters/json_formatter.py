"""JSON çıktı biçimlendiricisi."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from turkce_denetim.scoring import calculate_naturalness_score, get_naturalness_rating

if TYPE_CHECKING:
    from turkce_denetim.models import AnalysisResult


def format_json(results: list[AnalysisResult], indent: int = 2) -> str:
    """Denetim sonuçlarını yapılandırılmış JSON dizgisine çevirir."""
    all_findings = [f for r in results for f in r.findings]
    total_words = sum(r.word_count for r in results)
    overall_score = calculate_naturalness_score(total_words, all_findings)

    rule_counts: dict[str, int] = {}
    for f in all_findings:
        rule_counts[f.rule_id] = rule_counts.get(f.rule_id, 0) + 1

    files_data: list[dict[str, Any]] = []
    for res in results:
        file_findings: list[dict[str, Any]] = []
        for f in res.findings:
            file_findings.append(
                {
                    "rule_id": f.rule_id,
                    "rule_name": f.rule_name,
                    "severity": f.severity.value,
                    "message": f.message,
                    "line": f.line,
                    "column": f.column,
                    "end_line": f.end_line,
                    "end_column": f.end_column,
                    "suggestion": f.suggestion,
                    "context": f.context,
                }
            )

        files_data.append(
            {
                "path": res.path,
                "word_count": res.word_count,
                "sentence_count": res.sentence_count,
                "paragraph_count": res.paragraph_count,
                "naturalness_score": res.naturalness_score,
                "findings_count": {
                    "error": res.error_count,
                    "warn": res.warn_count,
                    "info": res.info_count,
                    "total": len(res.findings),
                },
                "findings": file_findings,
            }
        )

    payload = {
        "summary": {
            "file_count": len(results),
            "word_count": total_words,
            "naturalness_score": overall_score,
            "naturalness_rating": get_naturalness_rating(overall_score),
            "findings_count": {
                "error": sum(r.error_count for r in results),
                "warn": sum(r.warn_count for r in results),
                "info": sum(r.info_count for r in results),
                "total": len(all_findings),
            },
            "rule_distribution": rule_counts,
        },
        "files": files_data,
    }

    return json.dumps(payload, ensure_ascii=False, indent=indent)
