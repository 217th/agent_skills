#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\n(?P<yaml>.*?\n)---\n", re.DOTALL)
ALLOWED_FRONTMATTER_KEYS = {"name", "description"}

LINK_RE = re.compile(r"\[[^\]]+\]\((?P<target>[^)]+)\)")
CODE_TICK_PATH_RE = re.compile(r"`(?P<path>(?:assets|references|scripts)/[A-Za-z0-9._/\-]+)`")


@dataclass(frozen=True)
class Finding:
    level: str  # "error" | "warn"
    message: str


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("SKILL.md must start with YAML frontmatter delimited by ---")

    yaml_text = match.group("yaml")
    body = text[match.end() :]

    data: dict[str, str] = {}
    for raw_line in yaml_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid YAML line in frontmatter: {raw_line!r}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
            value = value[1:-1]
        data[key] = value

    return data, body


def _is_external_link(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:"))


def _is_anchor(target: str) -> bool:
    return target.startswith("#")


def _normalize_link_target(target: str) -> str:
    return target.split("#", 1)[0]


def lint(skill_dir: Path, *, strict: bool) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [Finding("error", f"missing {skill_md}")], 1

    text = skill_md.read_text(encoding="utf-8")
    try:
        fm, body = _parse_frontmatter(text)
    except ValueError as e:
        return [Finding("error", str(e))], 1

    keys = set(fm.keys())
    if keys != ALLOWED_FRONTMATTER_KEYS:
        extra = sorted(keys - ALLOWED_FRONTMATTER_KEYS)
        missing = sorted(ALLOWED_FRONTMATTER_KEYS - keys)
        if extra:
            findings.append(Finding("error", f"frontmatter has extra keys: {', '.join(extra)}"))
        if missing:
            findings.append(Finding("error", f"frontmatter missing keys: {', '.join(missing)}"))

    for key in ["name", "description"]:
        if not fm.get(key, "").strip():
            findings.append(Finding("error", f"frontmatter field '{key}' is empty"))

    if "TODO" in body or "[TODO" in body or "TODO:" in body:
        findings.append(Finding("error", "SKILL.md contains TODO markers; remove placeholders"))

    if "skills/public/" in text:
        findings.append(
            Finding(
                "warn",
                "SKILL.md references 'skills/public/...'; prefer '~/.codex/skills/<skill-name>/' for installed usage",
            )
        )

    expected_paths = [
        Path("references/component_docs_checklist.ru.md"),
        Path("references/docs_reference_structure.ru.md"),
        Path("assets/docs-component-template"),
        Path("scripts/init_component_docs.py"),
        Path("scripts/checklist_status.py"),
    ]
    for rel in expected_paths:
        if not (skill_dir / rel).exists():
            findings.append(Finding("warn", f"expected resource missing: {rel.as_posix()}"))

    for match in LINK_RE.finditer(text):
        target = match.group("target").strip()
        if not target or _is_external_link(target) or _is_anchor(target):
            continue
        target = _normalize_link_target(target)
        if not target or target.startswith(("~", "$", "/")):
            continue
        if not (skill_dir / target).exists():
            findings.append(Finding("warn", f"broken link target in SKILL.md: {target}"))

    for match in CODE_TICK_PATH_RE.finditer(text):
        rel = match.group("path")
        if not (skill_dir / rel).exists():
            findings.append(Finding("warn", f"missing referenced path in SKILL.md: {rel}"))

    errors = [f for f in findings if f.level == "error"]
    warns = [f for f in findings if f.level == "warn"]
    if errors:
        return findings, 1
    if strict and warns:
        return findings, 2
    return findings, 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint a Codex skill folder for basic consistency.")
    parser.add_argument(
        "--skill-dir",
        default=None,
        help="path to skill directory (default: auto-detect from this script location)",
    )
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures (exit code 2)")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve() if args.skill_dir else Path(__file__).resolve().parent.parent
    findings, code = lint(skill_dir, strict=args.strict)

    if not findings:
        print("[OK] No issues found")
        return 0

    for f in findings:
        prefix = "ERROR" if f.level == "error" else "WARN"
        print(f"{prefix}: {f.message}")
    if code == 0:
        print("[OK] Lint passed with warnings")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
