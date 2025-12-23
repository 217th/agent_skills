#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
from pathlib import Path


def _validate_component_key(component_key: str) -> str:
    component_key = component_key.strip()
    if not component_key:
        raise SystemExit("component key is empty")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", component_key):
        raise SystemExit(
            "component key must match: [a-z0-9]+(?:-[a-z0-9]+)* (example: worker-chart-export)"
        )
    return component_key


def _replace_tokens_in_file(path: Path, replacements: dict[str, str]) -> None:
    if path.suffix.lower() not in {".md", ".json", ".schema", ".txt"} and not path.name.endswith(
        ".schema.json"
    ):
        return

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return

    updated = text
    for needle, value in replacements.items():
        updated = updated.replace(needle, value)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a docs-<component-key>/ folder from the bundled template."
    )
    parser.add_argument("--component-key", required=True, help="kebab-case component key")
    parser.add_argument(
        "--dest",
        default=".",
        help="destination parent directory (default: current directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite destination directory if it already exists",
    )
    args = parser.parse_args()

    component_key = _validate_component_key(args.component_key)

    script_dir = Path(__file__).resolve().parent
    template_dir = (script_dir.parent / "assets" / "docs-component-template").resolve()
    if not template_dir.is_dir():
        raise SystemExit(f"template directory not found: {template_dir}")

    dest_parent = Path(args.dest).resolve()
    dest_dir = dest_parent / f"docs-{component_key}"

    if dest_dir.exists():
        if not args.force:
            raise SystemExit(f"destination already exists: {dest_dir} (use --force to overwrite)")
        shutil.rmtree(dest_dir)

    shutil.copytree(template_dir, dest_dir)

    replacements = {
        "{{component_key}}": component_key,
        "{{docs_root}}": f"docs-{component_key}",
    }
    for file_path in dest_dir.rglob("*"):
        if file_path.is_file():
            _replace_tokens_in_file(file_path, replacements)

    print(f"[OK] Initialized: {dest_dir}")
    print(
        f\"[Next] Copy checklist + structure reference: references/component_docs_checklist.ru.md and references/docs_reference_structure.ru.md -> {dest_dir}/checklists/\"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
