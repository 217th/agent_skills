# Spec pack guidelines (English quick reference)

Use this as a short, English navigation aid for the Russian checklist in `component_docs_checklist.ru.md`.
For the recommended file tree and checklist mapping, see `docs_reference_structure.ru.md`.

## Readiness buckets

- **Critical**: must be complete before epic decomposition starts.
- **Needed**: strongly recommended for planning quality (not a hard blocker).
- **Desirable**: nice-to-have; improves robustness and delivery quality.

## What to keep always up-to-date

- `questions/open_questions.md`: explicit unknowns, assumptions, and blockers.
- `inbox/`: temporary holding for unstructured notes (raw artifacts); triage continuously; keep artifacts append-only.
- A tickable checklist file (copy from `component_docs_checklist.ru.md`) that reflects the current truth.

## Two operating modes

- **Greenfield**: create docs from scratch, using the recommended structure as a starting point.
- **Existing docs**:
  - **Move-only**: re-home files into a structure with minimal content edits.
  - **Refactor**: extract facts, reconcile contradictions, rewrite into consistent spec files.

## Git discipline

- Use `git mv` for restructuring.
- Make one meaningful change per commit.
- Update the component `changelog.md` for each meaningful commit.
