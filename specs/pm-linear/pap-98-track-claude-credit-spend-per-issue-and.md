---
identifier: "PAP-98"
title: "Track Claude credit spend per issue and project and post a daily burn report to Linear"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-96", "PAP-283"]
blocks: ["PAP-111", "PAP-113"]
key: "pm-linear/credit-metering"
url: "https://linear.app/paperos/issue/PAP-98/track-claude-credit-spend-per-issue-and-project-and-post-a-daily-burn"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:18.010Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-98: Track Claude credit spend per issue and project and post a daily burn report to Linear

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Build M, P0 in pm-linear

**Goal**

Know at all times how much of the roughly $10,000 of credit has been spent, by which issue, project and character, and whether the 12/45/30/8/5 split holds. A daily burn report lands in Linear so Justin steers from his phone, and the live totals feed PAP-111.

**Scope**

* In: `usage_events` and `budgets` tables, the price table, area classification, `pnpm burn`, the daily report, weekly reconciliation against the Anthropic Console export, `docs/pm/credit-metering.md`.
* Out: enforcement (PAP-111), per-character daily pools (PAP-111), the org chart display (PAP-113).

**Spec**

* `usage_events(id, session_id, issue_id, project_key, character, model, input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens, cost_usd, turns, duration_ms, recorded_at, source: "sdk" | "hook" | "partial")`, unique on `(session_id, source)`; populated from the Agent SDK `result` message and from PAP-107 transcripts for hook-based sessions.
* `prices.ts`: per-model rates keyed by model id with `effectiveFrom`; the SDK `total_cost_usd` is authoritative, prices only recompute when it is missing. Unknown model: recompute impossible, flag `PRICE_UNKNOWN`.
* `budgets(scope_type: "area" | "project" | "character", scope_key, allocated_usd, spent_usd, updated_at)` seeded from plan.json shares of `totalUsd` (default 10000); area from Type label (Spec and Research to planning with Research split at 5 percent, Build and Infra to building, Review to review, Docs to docs).
* Report from `templates/burn-report.md`: totals, per area vs share, top ten issues, cache hit ratio, 14-day ASCII sparkline, under 3000 characters; posted daily 06:00 UTC to the pinned `Burn report` issue.
* Reconciliation job compares with CSV in `ops/metering/console/` on a 48 h window; drift above 10 percent flags the report.

**Interface contract**

* Provides: `recordUsage(event)`, `spent({ scope })`, `remaining({ scope })`, `liveTotal(sessionId)` (running sum from streamed messages), Zod `UsageEvent`, the `budgets` table, `pnpm burn [--json]`.
* Consumers: PAP-111 pre-flight and in-flight checks, PAP-113 (`spentTodayUsd`, `dailyCapUsd`), PAP-110 (`cost_usd` per eval run), PAP-306 (spend per project).
* Requires: PAP-96 sessions table and SDK stream; PAP-107 spool format for hook sessions.

**Definition of done**

* Recomputed price matches SDK cost within 1 percent on 20 recorded sessions.
* Three daily reports posted in staging; screenshots at 375 px and 1280 px.
* `pnpm burn` output for current spend pasted here.
* One reconciliation run against a real Console export with drift printed.
* Docs page; changelog entry; Linear comment with screenshots.

**Test plan**

* Unit: price recomputation, area classification for every Type label, share arithmetic when `totalUsd` changes mid-programme (history kept), partial-session summation.
* Integration: 20 recorded SDK result messages through `recordUsage` into SQLite; idempotent re-ingest.
* e2e: staging report job for three days.
* Visual: report in Linear mobile at 375 px shows the sparkline without wrapping.

**Demo**

Run `pnpm burn` and read the area table against the 12/45/30/8/5 shares, then `pnpm burn:report --post` and open the pinned issue on a phone. One minute.

**Edge cases**

* Session crashes before `result`: sum streamed `usage`, mark `partial`.
* Three attempts on one issue: costs aggregate; report shows attempt count.
* Sonnet sub-agent inside a Fable session: SDK cost already includes it; hook sessions price by `model`.
* Negative or missing `total_cost_usd`: recompute and flag.
* Console export lags: reconcile on the 48 h window only.

**Dependencies**

Blocked by PAP-96. Blocks PAP-111. Soft: PAP-107.

**Agent**

Built by Atlas (lead); reviewed by Sentinel (Code Reviewer).

**Size**

M
