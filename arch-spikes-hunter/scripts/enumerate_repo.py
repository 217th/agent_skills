#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_IGNORES_FILE = Path(__file__).resolve().parent.parent / "references" / "default_read_ignores.txt"


def _load_globs(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def _to_posix_relpath(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def _matches_any(path_posix: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if fnmatch.fnmatchcase(path_posix, pattern):
            return True
    return False


@dataclass(frozen=True)
class CandidateFile:
    relpath: str
    size_bytes: int

    def rank_key(self) -> tuple[int, int, str]:
        # Lower is better.
        p = self.relpath

        if p == "README.md":
            return (0, 0, p)

        # Prefer spec/*.md anywhere.
        if p.endswith(".md") and "/spec/" in f"/{p}":
            base = Path(p).name
            order = [
                "architecture_overview.md",
                "implementation_contract.md",
                "system_integration.md",
                "deploy_and_envs.md",
                "error_and_retry_model.md",
                "observability.md",
                "prompt_storage_and_context.md",
                "handoff_checklist.md",
            ]
            try:
                return (1, order.index(base), p)
            except ValueError:
                return (1, 999, p)

        # contracts
        if "/contracts/" in f"/{p}":
            if p.endswith("/contracts/README.md"):
                return (2, 0, p)
            if p.endswith(".schema.json"):
                return (2, 1, p)
            if p.endswith(".md"):
                return (2, 2, p)
            return (2, 999, p)

        if p.endswith("static_model.md"):
            return (3, 0, p)

        if "/fixtures/" in f"/{p}" or "/test_vectors/" in f"/{p}":
            if p.endswith("README.md"):
                return (4, 0, p)
            return (4, 1, p)

        return (9, 999, p)


def main() -> int:
    parser = argparse.ArgumentParser(description="Enumerate repo files applying ignore/allowlist globs and size limits.")
    parser.add_argument("--repo-root", required=True, help="Path to repository root to scan.")
    parser.add_argument("--ignore-glob", action="append", default=[], help="Additional READ ignore glob (repeatable).")
    parser.add_argument("--allowlist-glob", action="append", default=[], help="ALLOWLIST glob (repeatable).")
    parser.add_argument("--max-bytes", type=int, default=1_048_576, help="Max size of a single file to include.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    default_ignores = _load_globs(DEFAULT_IGNORES_FILE)
    user_ignores = list(args.ignore_glob or [])
    allowlist = list(args.allowlist_glob or [])
    ignores = default_ignores + user_ignores

    candidates: list[CandidateFile] = []

    for root, dirnames, filenames in os.walk(repo_root):
        root_path = Path(root)

        # Prune ignored directories early.
        pruned_dirnames: list[str] = []
        for d in dirnames:
            d_path = root_path / d
            rel = _to_posix_relpath(d_path, repo_root) + "/"
            if _matches_any(rel, ignores):
                continue
            pruned_dirnames.append(d)
        dirnames[:] = pruned_dirnames

        for fname in filenames:
            path = root_path / fname
            try:
                st = path.stat()
            except OSError:
                continue

            rel = _to_posix_relpath(path, repo_root)
            if _matches_any(rel, ignores):
                continue

            if allowlist and not _matches_any(rel, allowlist):
                continue

            if st.st_size > args.max_bytes:
                continue

            # Only list text-ish docs by default; keep broad but skip common binaries.
            if any(rel.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico")):
                continue

            candidates.append(CandidateFile(relpath=rel, size_bytes=int(st.st_size)))

    candidates.sort(key=lambda c: c.rank_key())

    print(f"repo_root: {repo_root}")
    print(f"max_bytes: {args.max_bytes}")
    print("allowlist_globs:", ", ".join(allowlist) if allowlist else "—")
    print("user_ignore_globs:", ", ".join(user_ignores) if user_ignores else "—")
    print()
    print("Candidates (prioritized):")
    for c in candidates:
        print(f"- {c.relpath} ({c.size_bytes} bytes)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

