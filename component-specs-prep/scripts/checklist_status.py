#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


SECTION_MAP: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^##\s+1\.\s+", re.IGNORECASE), "critical"),
    (re.compile(r"^##\s+2\.\s+", re.IGNORECASE), "needed"),
    (re.compile(r"^##\s+3\.\s+", re.IGNORECASE), "desirable"),
]


CHECKBOX_RE = re.compile(r"^\s*-\s*\[(?P<mark>[ xX])\]\s*(?P<body>.+?)\s*$")
TITLE_RE = re.compile(r"\*\*(?P<title>[^*]+)\*\*")


@dataclass(frozen=True)
class Item:
    section: str
    title: str
    checked: bool


def _detect_section(line: str, current: str | None) -> str | None:
    for pattern, section in SECTION_MAP:
        if pattern.match(line):
            return section
    return current


def _extract_title(body: str) -> str:
    match = TITLE_RE.search(body)
    if match:
        return match.group("title").strip()
    return body.strip()


def parse_items(text: str) -> list[Item]:
    items: list[Item] = []
    current_section: str | None = None
    for line in text.splitlines():
        current_section = _detect_section(line, current_section)
        checkbox = CHECKBOX_RE.match(line)
        if not checkbox or current_section is None:
            continue

        mark = checkbox.group("mark")
        body = checkbox.group("body")
        items.append(
            Item(
                section=current_section,
                title=_extract_title(body),
                checked=(mark.strip().lower() == "x"),
            )
        )
    return items


def summarize(items: list[Item]) -> dict[str, object]:
    sections = ["critical", "needed", "desirable"]
    summary: dict[str, object] = {"sections": {}, "totals": {}}
    total_checked = 0
    total_all = 0
    for section in sections:
        sec_items = [i for i in items if i.section == section]
        checked = [i for i in sec_items if i.checked]
        missing = [i for i in sec_items if not i.checked]
        summary["sections"][section] = {
            "done": len(checked),
            "missing": len(missing),
            "total": len(sec_items),
            "missing_titles": [i.title for i in missing],
        }
        total_checked += len(checked)
        total_all += len(sec_items)
    summary["totals"] = {"done": total_checked, "total": total_all, "missing": total_all - total_checked}
    return summary


def render_text(summary: dict[str, object]) -> str:
    sections = summary["sections"]  # type: ignore[assignment]
    totals = summary["totals"]  # type: ignore[assignment]
    lines: list[str] = []
    lines.append(f"Total: {totals['done']}/{totals['total']} done; {totals['missing']} missing")
    for key, label in [("critical", "Critical"), ("needed", "Needed"), ("desirable", "Desirable")]:
        sec = sections[key]
        lines.append(f"{label}: {sec['done']}/{sec['total']} done; {sec['missing']} missing")
        for title in sec["missing_titles"]:
            lines.append(f"  - {title}")
    return "\n".join(lines)


def render_markdown(summary: dict[str, object]) -> str:
    sections = summary["sections"]  # type: ignore[assignment]
    totals = summary["totals"]  # type: ignore[assignment]
    out: list[str] = []
    out.append(f"- Total: **{totals['done']} / {totals['total']}** done; **{totals['missing']}** missing")
    for key, label in [("critical", "Critical"), ("needed", "Needed"), ("desirable", "Desirable")]:
        sec = sections[key]
        out.append(f"- {label}: **{sec['done']} / {sec['total']}** done; **{sec['missing']}** missing")
        if sec["missing_titles"]:
            out.append("  - Missing:")
            for title in sec["missing_titles"]:
                out.append(f"    - {title}")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize checklist readiness by section (critical/needed/desirable)."
    )
    parser.add_argument("path", help="path to a markdown checklist file with - [ ] items")
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="output format (default: text)",
    )
    args = parser.parse_args()

    path = Path(args.path)
    text = path.read_text(encoding="utf-8")
    items = parse_items(text)
    summary = summarize(items)

    if args.format == "json":
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    if args.format == "markdown":
        print(render_markdown(summary))
        return 0

    print(render_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

