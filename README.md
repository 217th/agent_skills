# agent_skills

This repo contains the `component-specs-prep` Codex skill. It helps you prepare, structure, and validate a component/service “spec pack” so it’s ready for architecture/technical design and **epic-level decomposition**. The skill provides a recommended docs scaffold, a readiness checklist, and a workflow that keeps specs iterated cleanly (including inbox triage rules and a changelog discipline).

The main outcomes are: a consistent docs tree for a component (`docs-<component-key>/`), clear open questions, an epic-oriented `plan_wbs.md`, and a checklist-driven definition of “ready to decompose”.

## How to connect to Codex

Install the skill folder into your Codex skills directory (most setups use `~/.codex/skills/`):

```bash
mkdir -p ~/.codex/skills
cp -R component-specs-prep ~/.codex/skills/component-specs-prep
```

If your environment uses `CODEX_HOME`, install under `$CODEX_HOME/skills/component-specs-prep` instead.

## How to use

1. In your Codex prompt, explicitly ask to use the skill (name it as `component-specs-prep`).
2. Provide the component key (kebab-case) and any existing docs/notes you have; the skill will guide you through structuring and checklist validation.
3. To scaffold a new docs pack, run:

```bash
python3 ~/.codex/skills/component-specs-prep/scripts/init_component_docs.py --component-key <component-key>
```

4. Keep epic increments in `docs-<component-key>/plan_wbs.md` (value + acceptance), keep open questions in `docs-<component-key>/questions/open_questions.md`, and triage `docs-<component-key>/inbox/` as append-only raw artifacts (no links from the main spec pack back to inbox items).

