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
blockedBy: ["PAP-32", "PAP-33", "PAP-35", "PAP-269"]
blocks: ["PAP-107", "PAP-135", "PAP-480", "PAP-728", "PAP-729", "PAP-834", "PAP-836"]
key: "collab/prompt-log-store"
url: "https://linear.app/paperos/issue/PAP-129/create-the-promptresponse-log-store-session-character-issue-tokens"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:41.321Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-23"
cycle: null
---

# PAP-129: Create the prompt/response log store (session, character, issue, tokens, cost, tool calls) with redaction

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Build the system of record for how agents built PaperOS: Postgres tables and an ingest API storing every session, prompt, response, tool call, token count and cost with redaction and dedupe, queryable by issue, character and PR. Credit metering (PAP-98), evals (PAP-110), memory (PAP-109) and the browser (PAP-135) read from here.

**Scope**

In:

* Drizzle schema `packages/db/src/schema/prompt-log.ts`: `prompt_session` (`id` text = Claude session id, `tenant_id`, `character`, `sub_agent`, `issue_key`, `linear_issue_id`, `repo`, `branch`, `worktree`, `model`, `launch: hook|sdk`, `parent_session_id`, `started_at`, `ended_at`, `status: running|completed|killed|failed`, token columns, `cost_usd numeric(12,6)`, `pr_url`, `summary`, `redaction_count`, `gaps jsonb`); `prompt_event` (`id uuidv7`, `session_id`, `seq`, `ts`, `event`, `role`, `content`, `content_file_id`, `tool_name`, `tool_input jsonb`, `tool_output`, `usage jsonb`, `cost_usd`, `model`, `redactions jsonb`, `truncated`), unique `(session_id, seq)`, monthly partitions; `prompt_model_price`.
* Ingest `POST /api/v1/prompt-log/events` (NDJSON, 5 MB cap, idempotent on `(session_id, seq)`), bearer token per character from PAP-60, second-pass redaction with `packages/agents/src/redact.ts`, cost recomputed from the price table when absent.
* oRPC `promptLog.sessions.list|get|setSummary`, `promptLog.events.list`, `promptLog.stats({ groupBy })`.
* RLS: platform tenant only; `owner|admin` and agent principals read; ingest tokens write.
* Retention job (PAP-43): events older than 180 days to MinIO NDJSON; sessions and stats kept.

Out: hooks (PAP-107), browser UI (PAP-135), metering reports (PAP-98).

**Spec**

* `seq` gaps stored on the session and surfaced by `stats`; a synthetic `session.killed` event closes sessions.
* Cost = sum of tokens times the model price at `ts`; nightly recompute when prices change.
* Ingest p95 under 150 ms for a 1 MB batch via multi-row insert `ON CONFLICT DO NOTHING`.
* Indexes `(issue_key, started_at desc)`, `(character, started_at desc)`, `(session_id, seq)`, GIN on `tool_input`.
* Sessions registered as search entity `prompt_session` (PAP-39) for PAP-138.

*Round 4 amendment (2026-09-18):*
`prompt_session` gains `journal_path text` (written by PAP-728) and `summary_source: search|journal|manual`. Blob contents uploaded through `content_file_id` pass the second-pass redactor before upload, never after. `promptLog.sessions.list` accepts `filter: FilterTree` (PAP-279) so PAP-135's saved views compile server-side.

**Interface contract**

Exposes: tables above; ingest event shape `PromptEventIn { sessionId, seq, ts, character, subAgent?, issueKey?, event, role?, content?, toolName?, toolInput?, toolOutput?, usage?, costUsd?, model?, redactions? }` (Zod in `packages/contracts/prompt-log.ts`, shared with PAP-107); response `{ accepted, duplicates, gaps: [{ from, to }] }`; oRPC procedures above with `PromptSession` and `PromptEvent` types; `promptLog.stats` rows `{ key, inputTokens, outputTokens, cacheReadTokens, cacheWriteTokens, costUsd, sessions }`. Consumes: `tenant`/`user` from PAP-33, migrations from PAP-32, oRPC server and `callAs` from PAP-35, `verifyApiKey` from PAP-60 (static per-character env token until then), blob upload from PAP-37, job runtime from PAP-43.

**Definition of done**

* Migration applied on staging; RLS harness (PAP-34) shows a non-platform tenant sees nothing.
* A 20-turn recorded session from PAP-107 fixtures ingests fully; token totals within 1 percent.
* `docs/collab/prompt-log.md` (schema, API, retention, redaction); CHANGELOG entry; Linear comment with test and load results.

**Test plan**

* Vitest: dedupe on repeated `seq`, gap detection, cost computation with two price epochs, second-pass redaction over 30 fixtures (keys, tokens, emails), 413 on a 6 MB batch, unknown model leaves cost null and flagged.
* Integration (Postgres in CI): partition routing by month, RLS via `callAs(customerAdmin)` returns zero rows, retention job moves a 200-day-old partition to MinIO and deletes it.
* Load: k6 script `load/prompt-log.js`, 50 concurrent sessions × 200 events, completes under 2 minutes with zero duplicates; result JSON committed.
* Contract: PAP-107 fixture NDJSON validates against `PromptEventIn` in both repos' tests.

**Demo**

Run `pnpm prompt-log:replay fixtures/session-20-turns.ndjson` against staging, then call `promptLog.sessions.get` from the API playground and see tokens, cost and the PR URL; run `promptLog.stats({ groupBy: 'character' })` and read the totals. Under two minutes.

**Edge cases**

* Event arrives before `SessionStart`: session row created from event fields, filled later.
* Same `seq`, different content: first wins, mismatch logged to `ingest_anomaly`.
* Content over 64 KB with MinIO down: truncated with `truncated: true`, never rejected.
* Clock skew: order by `seq`, `ts` for display only.
* Token revoked mid-session: 401; shipper spools until rotation.

**Dependencies**

PAP-33, PAP-32, PAP-35 (hard, encoded). Soft: PAP-60, PAP-37, PAP-43. Blocks PAP-107, PAP-135; consumed by PAP-98, PAP-110.

**Agent**

Built by Forge (Schema Wright) with Quill (Prompt Logger) defining fields. Reviewed by Sentinel (Security Auditor for redaction and RLS) and Atlas.

**Size**

M: contained schema and ingest; performance, dedupe and redaction must be proven.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/collab/build-journals` = PAP-728.
