"""Komut satırı arayüzü (CLI)."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from turkce_denetim import __version__
from turkce_denetim.config import find_and_load_config, load_config_from_file
from turkce_denetim.engine import analyze_paths, analyze_text, collect_target_files
from turkce_denetim.formatters import format_json, format_sarif, format_text
from turkce_denetim.models import AnalysisResult, Severity


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="turkce-denetim",
        description="Türkçe metinlerde yapay zekâ ve çeviri kokusu kalıplarını bulan kural tabanlı linter.",
    )
    parser.add_argument(
        "targets",
        nargs="*",
        default=["."],
        help="Denetlenecek dosya, dizin veya standart girdi için '-' (varsayılan: .)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json", "sarif"],
        default="text",
        help="Çıktı biçimi: text (varsayılan), json, sarif",
    )
    parser.add_argument(
        "-d",
        "--disable",
        help="Devre dışı bırakılacak kural kimlikleri (virgülle ayrılmış, örn: TD001,TD005)",
    )
    parser.add_argument(
        "-s",
        "--min-severity",
        choices=["info", "warn", "error"],
        help="Raporlanacak asgari önem derecesi (info, warn, error)",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Özel yapılandırma dosyası (TOML) yolu",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Renkli terminal çıktısını kapat",
    )
    parser.add_argument(
        "--score-only",
        action="store_true",
        help="Yalnızca hesaplanan doğallık puanını yazdır",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # 1. Yapilandirmayi yukle
    if args.config:
        config = load_config_from_file(args.config)
    else:
        config = find_and_load_config()

    # CLI argumanlariyla yapilandirmayi gecersiz kil (override)
    if args.disable:
        cli_disabled = [x.strip().upper() for x in args.disable.split(",") if x.strip()]
        config.disable = list(set(config.disable + cli_disabled))

    if args.min_severity:
        config.min_severity = Severity.from_str(args.min_severity)

    # 2. Hedefleri belirle ve calistir
    results: list[AnalysisResult] = []

    if len(args.targets) == 1 and args.targets[0] == "-":
        # Standart girdi oku
        input_text = sys.stdin.read()
        res = analyze_text(input_text, config, path="<stdin>")
        results.append(res)
    else:
        target_files = collect_target_files(args.targets)
        if not target_files:
            if args.format == "text":
                sys.stderr.write("Uyarı: Denetlenecek geçerli (.md, .txt) dosya bulunamadı.\n")
            elif args.format == "json":
                sys.stdout.write(format_json([]))
                sys.stdout.write("\n")
            elif args.format == "sarif":
                sys.stdout.write(format_sarif([]))
                sys.stdout.write("\n")
            return 0

        results = analyze_paths(target_files, config)

    # 3. Yalnizca puan isteniyorsa
    if args.score_only:
        all_findings = [f for r in results for f in r.findings]
        total_words = sum(r.word_count for r in results)
        from turkce_denetim.scoring import calculate_naturalness_score

        score = calculate_naturalness_score(total_words, all_findings)
        sys.stdout.write(f"{score:.1f}\n")
        has_error = any(r.error_count > 0 for r in results)
        return 1 if has_error else 0

    # 4. Bicimlendirme ve cikti
    use_color = not args.no_color and sys.stdout.isatty()

    if args.format == "json":
        output = format_json(results)
    elif args.format == "sarif":
        output = format_sarif(results)
    else:
        output = format_text(results, use_color=use_color)

    sys.stdout.write(output)
    sys.stdout.write("\n")

    # 5. Cikis kodu: Hata seviyesinde bulgu varsa cikis 1
    has_error = any(r.error_count > 0 for r in results)
    return 1 if has_error else 0


if __name__ == "__main__":
    sys.exit(main())
