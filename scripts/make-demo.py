#!/usr/bin/env python3
"""Generates docs/demo.svg — a terminal-style SVG screenshot of turkce-denetim."""

from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "examples" / "bad.md"
OUTPUT_SVG = REPO_ROOT / "docs" / "demo.svg"


def run_cli_command() -> tuple[str, list[str]]:
    """Runs the CLI against examples/bad.md and captures its stdout."""
    import os

    rel_target = TARGET_FILE.relative_to(REPO_ROOT).as_posix()
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONPATH": str(REPO_ROOT / "src")}
    cmd = [sys.executable, "-m", "turkce_denetim", rel_target, "--no-color"]
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )
    raw_lines = proc.stdout.strip().splitlines()
    display_cmd = f"turkce-denetim {rel_target}"
    return display_cmd, raw_lines


def colorize_line(line: str) -> str:
    """Converts a plaintext terminal output line into SVG tspan tags with colors."""
    escaped = html.escape(line)

    # 1. Finding header line: examples/bad.md:1:1: warn  [TD008] ...
    finding_match = re.match(
        r"^(examples/bad\.md:\d+:\d+:)\s+(error|warn|info)\s+(\[[A-Z0-9]+\])\s+(.*)$",
        escaped,
    )
    if finding_match:
        loc, sev, rule, msg = finding_match.groups()
        sev_color = {
            "error": "#f38ba8",  # Red
            "warn": "#f9e2af",  # Yellow/Amber
            "info": "#89dceb",  # Cyan
        }.get(sev, "#cdd6f4")

        return (
            f'<tspan fill="#7f849c">{loc}</tspan> '
            f'<tspan fill="{sev_color}" font-weight="bold">{sev:<5}</tspan> '
            f'<tspan fill="#cba6f7">{rule}</tspan> '
            f'<tspan fill="#cdd6f4">{msg}</tspan>'
        )

    # 2. Suggestion line:     öneri: ...
    if escaped.startswith("    öneri:"):
        prefix, rest = escaped[:10], escaped[10:]
        return (
            f'<tspan fill="#a6e3a1" font-weight="bold">{prefix}</tspan>'
            f'<tspan fill="#9399b2" font-style="italic">{rest}</tspan>'
        )

    # 3. Section header: --- Denetim Özeti ---
    if "Denetim Özeti" in escaped:
        return f'<tspan fill="#89b4fa" font-weight="bold">{escaped}</tspan>'

    # 4. Summary metrics
    if ":" in escaped:
        label, val = escaped.split(":", 1)
        if "Doğallık Puanı" in label:
            return (
                f'<tspan fill="#fab387" font-weight="bold">{label}:</tspan>'
                f'<tspan fill="#f9e2af" font-weight="bold">{val}</tspan>'
            )
        return (
            f'<tspan fill="#a6adc8">{label}:</tspan>'
            f'<tspan fill="#cdd6f4" font-weight="bold">{val}</tspan>'
        )

    return f'<tspan fill="#cdd6f4">{escaped}</tspan>'


def generate_svg(command: str, lines: list[str]) -> str:
    """Builds a polished SVG window rendering the terminal session."""
    font_size = 13
    line_height = 20
    padding_top = 54
    padding_bottom = 20
    padding_left = 24

    total_lines = 1 + len(lines)  # prompt line + output lines
    width = 880
    height = padding_top + (total_lines * line_height) + padding_bottom

    svg_lines: list[str] = []
    current_y = padding_top + font_size

    # Command prompt line
    prompt_svg = (
        f'<text x="{padding_left}" y="{current_y}" xml:space="preserve">'
        f'<tspan fill="#a6e3a1" font-weight="bold">$ </tspan>'
        f'<tspan fill="#cdd6f4" font-weight="bold">{html.escape(command)}</tspan>'
        f"</text>"
    )
    svg_lines.append(prompt_svg)

    for line in lines:
        current_y += line_height
        if not line.strip():
            continue
        colored = colorize_line(line)
        text_elem = (
            f'<text x="{padding_left}" y="{current_y}" xml:space="preserve">{colored}</text>'
        )
        svg_lines.append(text_elem)

    content_svg = "\n    ".join(svg_lines)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" style="max-width: {width}px;">
  <defs>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="10" stdDeviation="16" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
  </defs>

  <g filter="url(#shadow)">
    <!-- Terminal Background -->
    <rect x="0" y="0" width="{width}" height="{height}" rx="10" ry="10" fill="#1e1e2e" stroke="#313244" stroke-width="1"/>

    <!-- Title Bar -->
    <rect x="0" y="0" width="{width}" height="38" rx="10" ry="10" fill="#181825"/>
    <rect x="0" y="28" width="{width}" height="10" fill="#181825"/>
    <line x1="0" y1="38" x2="{width}" y2="38" stroke="#313244" stroke-width="1"/>

    <!-- Window Controls (Red, Yellow, Green dots) -->
    <circle cx="20" cy="19" r="6" fill="#f38ba8"/>
    <circle cx="40" cy="19" r="6" fill="#f9e2af"/>
    <circle cx="60" cy="19" r="6" fill="#a6e3a1"/>

    <!-- Window Title -->
    <text x="{width / 2}" y="23" fill="#a6adc8" font-family="ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace" font-size="12" font-weight="bold" text-anchor="middle">turkce-denetim — bash</text>
  </g>

  <!-- Terminal Content -->
  <g font-family="ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace" font-size="{font_size}px">
    {content_svg}
  </g>
</svg>
"""


def main() -> None:
    cmd, lines = run_cli_command()
    svg_content = generate_svg(cmd, lines)
    OUTPUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SVG.write_text(svg_content, encoding="utf-8")
    print(f"Generated {OUTPUT_SVG} ({len(lines) + 1} lines)")


if __name__ == "__main__":
    main()
