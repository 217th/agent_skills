1. Разделить ветви: новый деплой, либо апдейт

2. Учесть:
/home/dd-user/projects/tda_llm_client/docs/spec/deploy_and_envs.md

### Lessons learned (dev deploy)
- Missing default compute SA can break deploys. Use `BUILD_SA_EMAIL` to supply a valid build service account.
- `BUILD_SA_EMAIL` must be a full resource name or a valid email; the script normalizes to
  `projects/<PROJECT_ID>/serviceAccounts/<EMAIL>`.
- Existing Cloud Run service with the same name blocks Functions gen2 creation. Delete it or use a new function name.
- Trigger SA must have `roles/eventarc.eventReceiver` and `roles/run.invoker` (on the service) for Firestore triggers.
- Runtime SA must have `roles/secretmanager.secretAccessor` for any Secret Manager–injected env var.
- Python 3.13 runtime + pinned `functions-framework` caused `ImportError: cannot import name 'T' from 're'` in startup;
  rely on the runtime-provided functions-framework instead of pinning in `requirements.txt`.