# Cloud Run Functions gen2 — Cloud Logging reference (extracted)

## IAM note (runtime SA) — Cloud Logging

- Cloud Logging:
  - Cloud Run Functions automatically ships stdout/stderr to Cloud Logging; no IAM role is usually needed for that.
  - Only grant `roles/logging.logWriter` if your code calls Cloud Logging API directly.

## Cloud Logging transport (what exists by default)

Cloud Run Functions gen2 automatically ships `stdout`/`stderr` to Cloud Logging.

If the application prints **JSON per line**, Cloud Logging typically renders it under `jsonPayload`.
If the application prints plain text, it appears under `textPayload`.

### Gen2 log resource type (common confusion)

For Cloud Run Functions gen2, application logs commonly appear under:
- `resource.type="cloud_run_revision"`
- `resource.labels.service_name="<function_name>"`

Quick query template:

```bash
gcloud logging read \
  'resource.type="cloud_run_revision"
   resource.labels.service_name="'"${FUNCTION_NAME}"'"' \
  --project "${PROJECT_ID}" \
  --limit 50 \
  --freshness 30m
```

## Logs and event names differ by component and step types

Different components (and even different step types in the same component) can emit different log events.

Therefore:
- The agent must not assume the presence of specific event names.
- The agent must first scan code for event naming conventions (e.g., look for a stable `event` key).

## Eventarc “service agent” invoker — evidence from logs (403 delivery)

If your logs show Eventarc delivery attempts but the Cloud Run request log reports `403`, grant invoker to the delivery identity.

Human-in-the-middle:
- Only apply this if there is evidence (403 delivery) and you can identify the actual caller identity from logs/trigger config.

## Human-in-the-middle: required log bundle for ignored events

- provide the event ID and the function logs around that time.

## Audit logs: identify failing principal (Eventarc storage triggers)

3) Identify the actual failing principal from audit logs (preferred). If you cannot, a common identity for Cloud Storage notifications is:
`service-${PROJECT_NUMBER}@gs-project-accounts.iam.gserviceaccount.com`

Important:
- Do not apply this blindly. Always confirm the principal from logs/audit logs when possible.
