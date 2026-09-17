---
identifier: "PAP-129"
title: "Create the prompt/response log store (session, character, issue, tokens, cost, tool calls) with redaction"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Docs and prompt log stores"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-269", "PAP-32", "PAP-33", "PAP-35"]
blocks: ["PAP-107", "PAP-135"]
key: "collab/prompt-log-store"
url: "https://linear.app/paperos/issue/PAP-129/create-the-promptresponse-log-store-session-character-issue-tokens"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-129: Create the prompt/response log store (session, character, issue, tokens, cost, tool calls) with redaction

**Goal**

Build the system of record for how agents built PaperOS: Postgres tables and an ingest API that store every session, prompt, response, tool call, token count and cost with redaction and dedupe, queryable by issue, character and PR. Credit metering, evals, memory curation and the prompt-log browser all read from here.

**Scope**

In:
- Drizzle schema in `packages/db/src/schema/prompt-log.ts`: `prompt_session` (`id` text from Claude session id, `tenant_id` platform tenant, `character`, `sub_agent`, `issue_key`, `linear_issue_id`, `repo`, `branch`, `worktree`, `model`, `launch: hook|sdk`, `parent_session_id`, `started_at`, `ended_at`, `status: running|completed|killed|failed`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`, `cost_usd numeric(12,6)`, `pr_url`, `summary`, `redaction_count`); `prompt_event` (`id uuidv7`, `session_id`, `seq int`, `ts`, `event`, `role`, `content text`, `content_file_id` for blobs over 64 KB in `data-layer/file-storage`, `tool_name`, `tool_input jsonb`, `tool_output text`, `usage jsonb`, `cost_usd`, `model`, `redactions jsonb`, `truncated bool`), unique `(session_id, seq)`, partitioned monthly by `ts`; `prompt_model_price` (`model`, `input_per_mtok`, `output_per_mtok`, `cache_read_per_mtok`, `cache_write_per_mtok`, `effective_from`).
- Ingest `POST /api/v1/prompt-log/events` accepting NDJSON in the event shape from `agents/prompt-logging-hook` (`sessionId, seq, ts, character, issueKey, event, role, content, toolName, toolInput, toolOutput, usage, costUsd, model, redactions`), bearer token per character from `identity/agent-principals`, batch cap 5 MB, idempotent on `(session_id, seq)`, upserts the session row, recomputes cost from `prompt_model_price` when `costUsd` is absent, returns `{ accepted, duplicates, gaps: [{ from, to }] }`.
- Server-side second-pass redaction with the shared regex set (`packages/agents/src/redact.ts`) so a misconfigured hook cannot store raw keys; matches counted into `redaction_count`.
- oRPC procedures: `promptLog.sessions.list({ filter: { character?, issueKey?, status?, from?, to? }, cursor })`, `promptLog.sessions.get(id)`, `promptLog.events.list({ sessionId, cursor, kinds? })`, `promptLog.stats({ groupBy: issue|character|day })` returning tokens and cost sums, `promptLog.sessions.setSummary`.
- RLS: platform tenant only; roles `owner|admin` and `agent` principals read; only ingest tokens write.
- Retention job: raw events older than 180 days moved to cold storage (NDJSON in MinIO) and deleted; session rows and stats kept forever.

Out: hooks and shipping (`agents/prompt-logging-hook`), the browser UI (`collab/prompt-log-ui`), metering reports (`pm-linear/credit-metering`), knowledge curation (Quill's Prompt Logger).

**Spec**

- `seq` gaps are stored on the session as `gaps jsonb` and surfaced by `stats`; a `session.killed` synthetic event from the orchestrator closes sessions.
- Cost formula: sum over events of tokens times price for the event's model at `ts`; nightly job recomputes sessions whose prices changed.
- Ingest p95 under 150 ms for a 1 MB batch; `COPY`-style multi-row insert with `ON CONFLICT DO NOTHING`.
- Indexes: `(issue_key, started_at desc)`, `(character, started_at desc)`, `(session_id, seq)`, GIN on `tool_input` for tool-name and path searches.
- Full-text: sessions registered with `data-layer/search` (`title` from issue and summary, `body` from summary) for `collab/knowledge-search`; events are not indexed.

**Definition of done**

- Drizzle migration applied on staging; RLS tests from `data-layer/rls-tenancy` harness show a non-platform tenant sees nothing.
- Vitest: ingest dedupe, gap detection, cost computation, second-pass redaction (30 fixtures), batch cap rejection with `413`.
- Integration: a 20-turn recorded session from `agents/prompt-logging-hook` fixtures ingests fully; token totals match within 1 percent.
- Load: 50 concurrent sessions shipping 200 events each ingest under 2 minutes with no duplicates (k6 script committed).
- `docs/collab/prompt-log.md` (schema, API, retention, redaction); CHANGELOG entry; Linear comment with test and load results.

**Edge cases**

- Event arrives before its session's first event: session row created from the event's fields; later `SessionStart` fills details.
- Same `seq` with different content (hook retried after edit): first wins, mismatch logged to `ingest_anomaly` table.
- Model unknown in the price table: cost stored null and flagged; `stats` reports uncosted tokens separately.
- Content over 64 KB and MinIO unavailable: truncated with `truncated: true`, never rejected.
- Clock skew across hosts: ordering uses `seq`, `ts` only for display.
- Token revoked mid-session: ingest returns 401; shipper spools until the orchestrator rotates the token.

**Dependencies**

`data-layer/core-entities` (hard, tenant and user), `data-layer/drizzle-schema`, `data-layer/api-layer`. Soft: `identity/agent-principals` (tokens; use a static per-character token from env until then), `data-layer/file-storage`. Unblocks `agents/prompt-logging-hook`, `collab/prompt-log-ui`, `pm-linear/credit-metering`, `agents/eval-harness`.

**Agent**

Built by Forge (Schema Wright) with Quill (Prompt Logger) defining fields. Reviewed by Sentinel (Security Auditor for redaction and RLS) and Atlas.

**Size**

M: schema and ingest are contained, but performance, dedupe and redaction must be proven.
