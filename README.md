# agent_skills

This repo contains Codex skills.

## Skills

### `component-specs-prep`

Prepares, structures, and validates a component/service “spec pack” so it’s ready for architecture/technical design and **epic-level decomposition**. It provides a recommended docs scaffold, a readiness checklist, and a workflow that keeps specs iterated cleanly (including inbox triage rules and a changelog discipline).

Main outcomes: a consistent docs tree for a component (`docs-<component-key>/`), clear open questions, an epic-oriented `plan_wbs.md`, and a checklist-driven definition of “ready to decompose”.

### `arch-spikes-hunter`

Reviews an in-repo specification pack and produces a prioritized backlog of **architectural spike questions** (research/design/prototyping) that must be answered before implementation is “ready”. The output is evidence-anchored (file paths + sections), avoids inventing missing facts, and is written as a single markdown file.

Main outcome: `questions/arch_spikes.md` with 12–30 spikes categorized by risk area (contracts, idempotency, security, observability, prompt/context storage, deploy/env, testing, etc).

### `gcp-functions-gen2-python-deploy`

Deploys and updates Python projects on **Google Cloud Functions (2nd gen / Cloud Run Functions gen2)**. It supports first-time bootstrap (APIs/IAM/trigger wiring), safe update deploys that preserve existing config, and optional cloud functional/integration verification using Cloud Logging.

## How to connect to Codex

Install the skill folder into your Codex skills directory (most setups use `~/.codex/skills/`):

```bash
mkdir -p ~/.codex/skills
cp -R component-specs-prep ~/.codex/skills/component-specs-prep
cp -R arch-spikes-hunter ~/.codex/skills/arch-spikes-hunter
cp -R gcp-functions-gen2-python-deploy ~/.codex/skills/gcp-functions-gen2-python-deploy
```

If your environment uses `CODEX_HOME`, install under `$CODEX_HOME/skills/<skill-name>` instead.

## How to use

1. In your Codex prompt, explicitly ask to use the skill (e.g., `component-specs-prep` or `gcp-functions-gen2-python-deploy`).
2. For `component-specs-prep`: provide the component key (kebab-case) and any existing docs/notes; the skill guides structuring and checklist validation.
3. To scaffold a new docs pack, run:

```bash
python3 ~/.codex/skills/component-specs-prep/scripts/init_component_docs.py --component-key <component-key>
```

4. Keep epic increments in `docs-<component-key>/plan_wbs.md` (value + acceptance), keep open questions in `docs-<component-key>/questions/open_questions.md`, and triage `docs-<component-key>/inbox/` as append-only raw artifacts (no links from the main spec pack back to inbox items).
5. For `gcp-functions-gen2-python-deploy`: provide the “Deploy request block” described in `gcp-functions-gen2-python-deploy/references/cloud_run_functions_gen2_deploy_first_try.md`.
