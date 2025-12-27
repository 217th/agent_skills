# Observability

## Logging contract

Logging contract is part of the component/service **public operational API**. Keep it stable and query-friendly.

### Logging backend and runtime expectation

- Logging backend: **<backend>** (example: Google Cloud Logging).
- Log format: **structured JSON** (prefer) / plain text (only if constrained).
- Runtime expectation:
  - Log to stdout/stderr via the language logger (example: Python `logging`).
  - Ensure the platform ingests these logs into the backend with JSON preserved (example: `jsonPayload.*` in Cloud Logging).

### Baseline goals

- Provide a **stable event taxonomy** so dashboards/alerts can query by `event`.
- Support at-least-once delivery if the ingress mechanism can duplicate/reorder events.
- Be safe by default: avoid leaking secrets, PII, tokens, prompts, or full artifacts.

### Required fields (every log entry)

Define a strict baseline schema for every log entry:

- `service`: stable service name for dashboards (example: `worker_llm_client`)
- `env`: environment (`dev|staging|prod` or similar)
- `component`: stable component identifier (may equal `service`)
- `event`: stable event name in **snake_case** (see event catalog below)
- `severity`: `DEBUG|INFO|WARNING|ERROR`
- `message`: default equals `event` (human-friendly summary allowed)
- `time`: RFC3339 timestamp (UTC)
- Correlation:
  - `eventId`: ingress event ID (example: CloudEvent `id`)
  - `runId`: main business correlation id (if applicable)
  - `stepId`: sub-unit of work id (if applicable)
- Trace context (when available):
  - `trace`, `spanId`

### Recommended fields (when applicable)

- Ingress metadata:
  - `eventType` (example: CloudEvent `type`)
  - `subject` (example: CloudEvent `subject`)
- Attempting / retry context:
  - `attempt` (attempt number within a single invocation)
  - `retryCount` (if platform retries are observable)
- Domain fields (only when already available from the domain object):
  - `<domainKey1>`, `<domainKey2>` (e.g., `flowKey`, `timeframe`, `symbol`)
- Storage pointers (prefer pointers over payloads):
  - `artifact.uri` (e.g., `gs://...`)
  - `artifacts`: array of compact summaries (URIs, sizes, hashes; no full contents)
- Timing:
  - `durationMs`
- Errors (sanitized):
  - `error.code` (stable)
  - `error.message` (sanitized; no secrets)
  - `error.retryable` (bool)
  - `exception` (stack trace when needed; ensure no secrets)
- For LLM / AI components (if applicable):
  - `llm.promptId`, `llm.modelName`
  - `llm.requestId` (provider id, when available)
  - `llm.usage` (tokens/usage summary)
  - `llm.schemaId`, `llm.schemaSha256`, `llm.schemaVersion` (for structured output schemas)
  - `llm.generationConfig` (sanitized summary only)

### Event names (baseline proposal)

Event names are a stable API for dashboards/alerts. Keep them in **snake_case**, version only when breaking.

#### Ingress lifecycle (example: CloudEvent-triggered)

- `cloud_event_received`
- `cloud_event_parsed`
- `cloud_event_ignored` (filtered/invalid)
- `cloud_event_noop` (expected no-op)
- `cloud_event_finished`

#### Unit-of-work lifecycle (example: step-based worker)

- `ready_step_selected`
- `claim_attempt` (`claimed=true|false`)
- `step_completed`
- `step_failed`

#### External calls (generic)

- `external_call_started`
- `external_call_finished`

#### Storage IO (generic)

- `storage_read_started`
- `storage_read_finished`
- `storage_write_started`
- `storage_write_finished`

#### Structured output / schema validation (only if applicable)

- `structured_output_invalid`
- `structured_output_schema_invalid`
- `structured_output_repair_attempt_started`
- `structured_output_repair_attempt_finished`

### Event catalog (MVP)

Create a canonical event taxonomy table. This table is the source of truth for `event`.

#### Ingress lifecycle

| Event | Severity | When | Required fields (in addition to base) |
| --- | --- | --- | --- |
| `cloud_event_received` | INFO | entrypoint invoked | `eventType`, `subject` |
| `cloud_event_ignored` | WARNING | event filtered/invalid | `reason` |
| `cloud_event_parsed` | INFO | correlation id parsed + domain loaded | `runFound` (bool), `runStatus`, `runSteps[]` (compact summaries) |
| `cloud_event_noop` | INFO | expected no-op | `reason` |
| `cloud_event_finished` | INFO | handler ends | `status` (`noop|ok|failed`) |

Keep `cloud_event_noop.reason` values stable (enumeration).

#### Work selection / claim (example)

| Event | Severity | When | Required fields |
| --- | --- | --- | --- |
| `ready_step_selected` | INFO | READY unit of work chosen | `stepId`, `stepType` |
| `claim_attempt` | INFO/WARNING | claim attempted | `claimed` (bool), `reason` (`ok|precondition_failed|error`) |

#### External calls (example)

| Event | Severity | When | Required fields |
| --- | --- | --- | --- |
| `external_call_started` | INFO | before calling provider | `provider`, `operation`, optional `requestId` |
| `external_call_finished` | INFO/ERROR | after provider call | `provider`, `operation`, `status` (`succeeded|failed`), optional `durationMs` |

### JSON examples (structured logs)

Provide at least:
- one “happy path” ingestion event (compact, query-friendly),
- one “error path” event (sanitized error and correlation),
- one “no-op” example (with stable `reason`).

Example (illustrative):

```json
{
  "service": "worker_llm_client",
  "env": "dev",
  "component": "worker_llm_client",
  "event": "cloud_event_parsed",
  "severity": "INFO",
  "eventId": "8e101933-5679-46f0-bc89-089edbb2cada",
  "runId": "20251224-061000_LINKUSDT_demo92",
  "runFound": true,
  "runStatus": "RUNNING",
  "runSteps": [
    { "id": "ohlcv_export:1M", "stepType": "OHLCV_EXPORT", "status": "SUCCEEDED", "dependsOn": [] },
    { "id": "charts:1M:ctpl_price_ma1226_vol_v1", "stepType": "CHART_EXPORT", "status": "SUCCEEDED", "dependsOn": ["ohlcv_export:1M"] }
  ],
  "message": "CloudEvent parsed, runId extracted",
  "time": "2025-12-24T06:10:00Z"
}
```

### Mapping events to execution flow

Describe the expected ordering on a typical successful run, and list expected no-op flows.

Typical success flow (one invocation):
1. `cloud_event_received`
2. `cloud_event_parsed`
3. `ready_step_selected`
4. `claim_attempt` (`claimed=true`)
5. `external_call_started` → `external_call_finished`
6. `storage_write_started` → `storage_write_finished`
7. `step_completed`
8. `cloud_event_finished`

Expected no-op flows:
- no READY work: `cloud_event_noop` (`reason=no_ready_step`)
- dependencies not satisfied: `cloud_event_noop` (`reason=dependency_not_succeeded`)
- claim lost race: `cloud_event_noop` (`reason=claim_conflict`)

### Security and privacy requirements

Explicitly list “never log” rules and safe alternatives:
- Never log secrets (tokens, credentials, secret manager values).
- Never log full prompts or raw LLM outputs; prefer sizes + hashes + sanitized summaries.
- Avoid logging full domain objects (e.g., full “run” documents); log IDs + compact summaries.
- Do not put secrets/PII into object names, URLs, or other identifiers that may leak.

### Structured output diagnostics (only if applicable)

If the component uses structured output (JSON schema / response schema), define how failures are diagnosable **without** logging raw payloads.

Rules:
- Never log raw candidate text / JSON payload.
- Log sizes + hashes of candidate text and **sanitized** validation errors (capped).

Recommended fields for `structured_output_invalid`:
- `reason.kind` (`finish_reason|missing_text|json_parse|schema_validation`)
- `reason.message` (sanitized)
- `diagnostics.textBytes`, `diagnostics.textSha256`
- `diagnostics.validationErrors[]` (sanitized, capped)
- `policy.repairEligible`, `policy.repairExecuted`

## Metrics

## Alerts and dashboards
