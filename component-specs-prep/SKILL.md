---
name: component-specs-prep
description: Prepare, structure, and validate a component/service specification pack so it is ready for architecture/technical design and epic decomposition. Use when you need to (1) create or improve component/service docs, (2) migrate existing scattered docs into a recommended structure (either move-only or content refactor), (3) track readiness against a checklist (critical/needed/desirable), (4) maintain open questions and an "inbox" for unstructured notes, and (5) keep docs change-by-change in Git with a detailed changelog entry per important commit.
---

# Component Specs Prep

## Overview

Produce a consistent “spec pack” for a component (one service in a larger multi-service system), validate it against a readiness checklist, and keep it versioned in Git with clear iteration status and open questions.

This skill assumes the spec pack must cover both:
- **System integration**: contracts and interactions with other services / external systems.
- **Service details**: behavior, domain model, errors/retries, observability, deploy/runbook basics.

If the request includes logging / observability details, the output must include a **fully specified logging contract** (not just headings): backend + format, required vs recommended fields, required vs optional events, JSON examples for key events, mapping events to the execution flow, and explicit security/privacy rules. Use the structure in `assets/docs-component-template/spec/observability.md`.

## Quick start (what to do first)

1. Decide the mode: **Greenfield** (new docs) vs **Existing docs** (migration + cleanup).
2. Ensure there is (or create) a single component docs root folder (recommended: `docs-<component-key>/`).
3. Create or update:
   - `questions/open_questions.md` (always up-to-date)
   - `inbox/` (append-only raw artifacts; must be triaged continuously; do not edit artifacts after processing)
   - a checklist file you will tick (recommended to copy from `references/component_docs_checklist.ru.md`)
   - the recommended docs structure reference (copy `references/docs_reference_structure.ru.md` alongside the checklist)
   - `plan_wbs.md` (kept up-to-date; contains epic-level increments, value, and acceptance criteria)
4. Iterate: add/adjust specs → tick checklist items → commit with changelog entry → report status.

If you need a scaffold quickly, run:

```bash
python3 ~/.codex/skills/component-specs-prep/scripts/init_component_docs.py \
  --component-key <component-key>
```

## Workflow decision tree

### A) Greenfield (new component)

1. Create `docs-<component-key>/` using the template (script or manual copy from `assets/docs-component-template/`).
2. Fill minimum integration + service specs (start with the checklist’s critical section).
3. Create formal contracts (schemas) and at least minimal test vectors.
4. Tick checklist items as they become true; do not “tick by intention”.

### B) Existing docs (migration / cleanup)

1. Inventory what exists: list files/links, identify duplicates and contradictions.
2. Decide **whether restructuring is worth it**:
   - If docs are small/medium and will be actively maintained → restructure is usually worth it.
   - If docs are huge/legacy and only lightly touched → consider minimal, non-disruptive changes.
3. Choose manipulation mode:
   - **Move-only (light mode)**: `git mv` into a recommended layout, rename for clarity, no content edits.
   - **Refactor (deep mode)**: read existing docs, extract useful facts, reconcile contradictions, rewrite into the new structure with consistent terminology.
4. Keep a trail:
   - Preserve provenance with links (e.g., “Source: <old-doc>”) during refactor.
   - Keep `questions/open_questions.md` updated with unresolved ambiguities.

## Recommended docs layout (non-binding)

Use the checklist’s recommended structure as a baseline (it is not a hard requirement). The template in `assets/docs-component-template/` also includes:
- `inbox/` (append-only raw artifacts to triage)
- `changelog.md` (detailed, per meaningful commit)

## Iteration loop (spec refinement)

Repeat until all critical items are complete and “needed” items are reasonably covered:

1. Pull new information from:
   - stakeholder notes, tickets, diagrams, legacy docs, code, runbooks, incident postmortems
   - `inbox/` (triage continuously; do not let it grow indefinitely; keep artifacts immutable)
2. Update specs:
   - keep integration contracts and service behavior consistent
   - explicitly call out assumptions and unknowns
3. Tick checklist items that are now satisfied.
4. Update `questions/open_questions.md` (close items or reword them precisely).
5. Commit the change + update `changelog.md` in the same commit.
6. Report status (critical/needed/desirable completed vs missing).

## Status reporting (every iteration)

Maintain a clear, current readiness view:

1. Run the helper to summarize checklist status:

```bash
python3 ~/.codex/skills/component-specs-prep/scripts/checklist_status.py path/to/component_docs_checklist.md
```

2. In your human-facing update (chat / PR / message), include:
   - **Critical**: done / missing (+ list missing)
   - **Needed**: done / missing (+ list missing)
   - **Desirable**: done / missing (+ list missing)
   - **Open questions**: count + top blockers (link to `questions/open_questions.md`)

## Git + changelog discipline

Rules of thumb:
- Make **one meaningful change per commit** (or per tightly related set of file edits).
- For every meaningful commit, update `docs-<component-key>/changelog.md` with:
  - what changed (concrete)
  - why it changed (intent / decision)
  - any checklist status delta (if applicable)
  - any open questions added/closed

Use `git mv` when restructuring so history remains traceable.

## Plan / WBS discipline (kept up-to-date)

Maintain `docs-<component-key>/plan_wbs.md` as the epic-level view of delivery increments:
- **What changes** in the service (plain words)
- **Why it matters** (product value)
- **How to accept** (what to check)

Keep epic descriptions actionable and acceptance-focused; avoid implementation detail unless it is contract-critical.

## Inbox triage policy

`inbox/` is a temporary holding area for unstructured information **and** a provenance log for raw artifacts.
- Treat inbox artifacts as **append-only**: once an item is added and processed, **do not edit it later**.
- Never treat inbox contents as “done”; distill them into the proper spec files.
- Do not leave links/references from the main spec pack to inbox artifacts: `inbox/` is not a long-lived source of truth.
- If you cannot place an item confidently, add an open question and **copy the necessary context** into `questions/open_questions.md` (no links back to inbox).
- If new information corrects/overrides an inbox artifact, add a **new** inbox item that references the original (inside `inbox/`), instead of modifying the original.

## Included resources

- `references/component_docs_checklist.ru.md`: readiness checklist (source of truth for categories and items).
- `references/docs_reference_structure.ru.md`: recommended docs tree + mapping to checklist items.
- `assets/docs-component-template/`: recommended starter structure + placeholder docs.
- `scripts/init_component_docs.py`: scaffold a new `docs-<component-key>/` folder from the template.
- `scripts/checklist_status.py`: compute completion stats and list missing checklist items.
