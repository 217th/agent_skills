---
name: arch-spikes-hunter
description: Review an in-repo specification pack and produce a prioritized backlog of architectural spike questions (design/research/prototyping) for a Python service on Google Cloud (Cloud Functions gen2 / Cloud Run) and LLM integrations. Use when you must identify gaps/risks before implementation. Output must be written to questions/arch_spikes.md (overwrite) and the chat response must only confirm the file path and spike counts.
---

# Arch Spikes Hunter

Generate a concise, evidence-anchored backlog of architectural spike questions from a repository’s spec pack. Do not propose full designs; output is **questions + why they matter + how to validate**.

## First message to the user (required)

Ask for:
- **Service name**
- **Runtime** (default Python)
- **Platform** (default Google Cloud Functions gen2; Cloud Run also possible)
- **Service responsibility** (1–3 sentences)
- **repo_root** (absolute path or workspace-relative path to the repo being analyzed)
- **User-defined READ ignore globs** (files/folders to skip in addition to defaults)
- (Optional) **ALLOWLIST globs**: if provided, read **only** allowlisted files (still obey ignores)

## Non-negotiable rules

- **Source of truth is the repository contents you can read.** Do not invent missing facts.
- If something is not explicitly specified, treat it as a **gap** and formulate it as a **spike question**.
- Anchor every spike to evidence by referencing **file paths** and (if available) **section headings**; quotes are optional but must be **≤20 words**.
- Do **not** propose full designs. Output is a spike backlog: **questions + why they matter + what to validate**.
- Be concise and structured. No narrative.
- Never read or output secrets. If you encounter likely secret files (e.g. `.env`, credentials, keys), **skip** them and treat as out of scope.
- Skip binary files and huge files. **Max text file size to read: 1 MB** (if bigger, treat as missing; do not partially read).

## Ignore policy (READING ONLY)

- Always apply default ignores from `references/default_read_ignores.txt`.
- Then apply the user-defined ignores.
- If ALLOWLIST is provided: read **only** files that match ALLOWLIST (and still not ignored).
- If unsure whether a file matches ignore patterns, err on the side of **skipping**.
- Treat `/questions` as **read-ignored**; do not read anything under it.

## Work plan (do it silently)

1. Enumerate files under `repo_root` applying allowlist + ignore rules.
2. Read prioritized docs/contracts/tests; cross-check inconsistencies.
3. Extract/merge/deduplicate existing open questions if found **outside ignored paths**; enrich rather than repeat.
4. Produce the spike list and write `questions/arch_spikes.md` (overwrite).

### File reading priority (when repo is large)

Prioritize reading in this order:
1. Root `README.md`
2. `spec/*.md` (architecture_overview, implementation_contract, system_integration, deploy_and_envs, error_and_retry_model, observability, prompt_storage_and_context, handoff_checklist)
3. `contracts/*.md` and `*.schema.json`, plus `contracts/README.md`
4. `static_model.md`
5. `fixtures/**` and `test_vectors/**` (inputs/outputs/README)

Tip: Use `scripts/enumerate_repo.py` to get a prioritized candidate list before opening files.

## What counts as an “architectural spike question”

A question is a spike if unanswered it could:
- block implementation
- cause production incidents
- create security/compliance risk
- break system integration/contracts
- significantly affect cost/latency/scaling
- prevent reliable testing/evaluation

## Spike categories (use one)

- contracts_api
- data_model
- idempotency_concurrency
- error_retry_recovery
- security_privacy_compliance
- observability_slo
- prompt_context_storage
- integration_dependencies
- deployment_env_config
- performance_cost_quotas
- testing_eval_quality
- migration_versioning

## Deliverable (MUST)

Write a markdown file at `questions/arch_spikes.md`:
- Create the `questions/` folder if missing.
- Overwrite the file if it already exists.
- Even if `/questions` is ignored for reading, writing the output file there is **required** (treat `/questions` as write-only).

The file must contain:
1. A short header:
   - Service name
   - Date (**use local time**)
   - Scope (what directories were analyzed; list allowlist)
   - Read-ignored paths summary (list the user-defined ignores)
2. A markdown table with **12–30** spikes (unless the spec is unusually complete).

### Table format (MUST be a valid Markdown table)

Columns:
| ID | Pri | Category | Decision Question | Why it matters | Evidence (file#section) | Unknowns to resolve | Options (A/B) | Recommended spike (type/timebox) | Validation steps | Done criteria | Dependencies | Confidence |

Formatting rules for table cells:
- Keep each cell compact.
- Use `<br>` for multi-line content inside a cell.
- Evidence must include at least one **file path**; add section heading when possible.
- Options should be **2 entries** (A/B) with short tradeoff notes.
- Dependencies: list `SPK-###` ids or `—`.
- `Pri` uses `P0`/`P1`/`P2`.

## Final response in chat (MUST)

After writing the file, output ONLY:
- One line: `Wrote questions/arch_spikes.md`
- One line: total spike count and `P0`/`P1`/`P2` breakdown

Do not paste the table in chat. Do not output JSON.

