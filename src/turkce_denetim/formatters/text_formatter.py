"""Insan okur metin biçimlendiricisi (ANSI renk destekli)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from turkce_denetim.models import Severity
from turkce_denetim.scoring import get_naturalness_rating

if TYPE_CHECKING:
    from turkce_denetim.models import AnalysisResult

# ANSI renk kodlari
_RESET = "\033[0m"
_BOLD = "\033[1m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_MAGENTA = "\033[35m"
_GREEN = "\033[32m"
_GRAY = "\033[90m"


def _colorize(text: str, color: str, use_color: bool) -> str:
    return f"{color}{text}{_RESET}" if use_color else text


def format_text(
    results: list[AnalysisResult],
    use_color: bool = True,
    show_summary: bool = True,
) -> str:
    """Denetim sonuçlarını standart linter formatında metne çevirir."""
    lines: list[str] = []
    total_findings = 0
    total_words = 0
    rule_counts: dict[str, int] = {}
    severity_counts: dict[Severity, int] = {
        Severity.ERROR: 0,
        Severity.WARN: 0,
        Severity.INFO: 0,
    }

    for res in results:
        file_path = res.path or "<stdin>"
        total_words += res.word_count

        for finding in res.findings:
            total_findings += 1
            severity_counts[finding.severity] += 1
            rule_counts[finding.rule_id] = rule_counts.get(finding.rule_id, 0) + 1

            # Onem derecesi rengi
            if finding.severity == Severity.ERROR:
                sev_str = _colorize("error", _RED, use_color)
            elif finding.severity == Severity.WARN:
                sev_str = _colorize("warn ", _YELLOW, use_color)
            else:
                sev_str = _colorize("info ", _CYAN, use_color)

            rule_id_str = _colorize(finding.rule_id, _MAGENTA, use_color)
            loc_str = _colorize(f"{file_path}:{finding.line}:{finding.column}", _BOLD, use_color)

            lines.append(f"{loc_str}: {sev_str} [{rule_id_str}] {finding.message}")
            if finding.suggestion:
                sug_label = _colorize("öneri:", _GRAY, use_color)
                lines.append(f"    {sug_label} {finding.suggestion}")

    if show_summary:
        if lines:
            lines.append("")

        lines.append(_colorize("--- Denetim Özeti ---", _BOLD, use_color))
        lines.append(f"Taranan belge sayısı : {len(results)}")
        lines.append(f"Toplam kelime sayısı : {total_words}")

        err_cnt = severity_counts[Severity.ERROR]
        warn_cnt = severity_counts[Severity.WARN]
        info_cnt = severity_counts[Severity.INFO]

        err_disp = _colorize(f"{err_cnt} hata", _RED if err_cnt > 0 else _GRAY, use_color)
        warn_disp = _colorize(f"{warn_cnt} uyarı", _YELLOW if warn_cnt > 0 else _GRAY, use_color)
        info_disp = _colorize(f"{info_cnt} bilgi", _CYAN if info_cnt > 0 else _GRAY, use_color)

        lines.append(
            f"Bulgular             : {err_disp}, {warn_disp}, {info_disp} (toplam {total_findings})"
        )

        if rule_counts:
            breakdown = ", ".join(f"{k}: {v}" for k, v in sorted(rule_counts.items()))
            lines.append(f"Kural dağılımı       : {breakdown}")

        # Genel dogallik puani
        all_findings = [f for r in results for f in r.findings]
        from turkce_denetim.scoring import calculate_naturalness_score

        overall_score = calculate_naturalness_score(total_words, all_findings)
        rating_desc = get_naturalness_rating(overall_score)

        score_color = _GREEN if overall_score >= 85 else (_YELLOW if overall_score >= 60 else _RED)
        score_disp = _colorize(f"{overall_score:.1f} / 100", f"{_BOLD}{score_color}", use_color)
        lines.append(f"Doğallık Puanı       : {score_disp} ({rating_desc})")

    return "\n".join(lines)
