---
name: gcp-functions-gen2-python-deploy
description: Deploy and update Python services on Google Cloud Functions (2nd gen / Cloud Run Functions gen2) using gcloud. Use for first-time bootstrap (APIs/IAM/trigger wiring), safe redeploys that preserve existing config, and optional cloud functional/integration verification via Cloud Logging.
---

# GCP Functions Gen2 Python Deploy

Use this skill to deploy a Python project to **Google Cloud Functions (2nd gen)** (a.k.a. “Cloud Run Functions gen2”) with a repeatable, low-surprise workflow.

## Source of truth (must use)

The canonical procedure is the bundled playbook:
- `references/cloud_run_functions_gen2_deploy_first_try.md`

When executing a deploy, follow the playbook steps **verbatim**. Do not “summarize from memory” or silently skip steps.

## What to ask the human for (input block)

Ask the user to provide the **Deploy request block** from:
- `references/cloud_run_functions_gen2_deploy_first_try.md` → Section 1

Rules:
- Do not ask the human for `ENTRY_POINT`; derive it from the codebase as in the playbook.
- Do not run smoke verification unless `APPROVE_SMOKE_VERIFY=true`.
- Never commit real identifiers/secrets into docs; keep placeholders in any tracked text.

## Workflow (high-level)

1. Decide deploy mode (first-time vs update): playbook Section 2.
2. Execute the matching path:
   - First-time deploy: playbook Section 4 (bootstrap + validations).
   - Update deploy: playbook Section 5 (minimal changes; preserve existing config).
3. If functional/integration verification in cloud is requested and explicitly approved:
   - Use playbook Section 6 (Cloud Logging queries + optional smoke verification).
4. If deploy fails:
   - Use playbook Section 8 (troubleshooting). Stop and ask for confirmation before destructive actions.

## Safety constraints

- Treat trigger changes as behavior-changing and potentially destructive; require explicit confirmation (playbook Section 5.3).
- Do not introduce broad IAM roles if the used services are unknown; require `USED_GCP_SERVICES` or ask the human.
- Avoid keys; prefer service account impersonation for verification where possible (playbook Section 4.6.4).

