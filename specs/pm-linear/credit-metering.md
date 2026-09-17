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
blockedBy: ["PAP-96"]
blocks: ["PAP-111", "PAP-113"]
key: "pm-linear/credit-metering"
url: "https://linear.app/paperos/issue/PAP-98/track-claude-credit-spend-per-issue-and-project-and-post-a-daily-burn"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-98: Track Claude credit spend per issue and project and post a daily burn report to Linear

**Goal**

Know at all times how much of the roughly $10,000 of Claude Fable 5.1 credit has been spent, by which issue, project and character, and whether the plan's 12/45/30/8/5 split is holding. A daily burn report lands in Linear so Justin can steer without opening a dashboard, and the numbers feed `agents/cost-controls`.

**Scope**

In:
- Metering table `orchestrator.usage_events(id, session_id, issue_id, project_key, character, model, input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens, cost_usd, turns, duration_ms, recorded_at, source)` populated from the Agent SDK `result` message (`total_cost_usd`, `usage`) and, for hook-based sessions, from transcript JSONL `usage` fields via `agents/prompt-logging-hook`.
- Price table `src/metering/prices.ts` with Fable 5.1 rates ($10 input, $50 output per million tokens; cache reads $0.25 per million; cache writes at the published multiplier) and a fallback for other models; used only to recompute when the SDK cost is absent, otherwise the SDK figure is authoritative.
- Budget ledger: `budgets(scope_type, scope_key, allocated_usd, spent_usd)` seeded from plan.json `budget[]` shares of a configurable `totalUsd` (default 10000) and per-project allocations.
- Daily report (cron 13:00 UTC) posted to pinned issue `PAP-BURN-REPORT`: total spent, remaining, days left to 2026-10-01, burn per day and projected finish, top 10 issues by cost, per-character totals, per-area share versus plan, any issue over its estimate-derived cap (S $60, M $180, L $450 default).
- Per-issue cost comment: when a session ends, the footer JSON already carries `costUsd`; metering also updates a running total in the issue's status comment (via `pm-linear/webhooks`).
- CLI `pnpm burn --by project|character|issue --since 7d` printing a table; JSON export for `agents/org-chart-ui`.

Out: enforcing limits (`agents/cost-controls`), Anthropic Console reconciliation UI, invoicing.

**Spec**

- Area classification: Type label maps to budget area (Spec/Research to planning, Build/Infra to building, Review to review, Docs to docs) with Research separated at 5 percent as in plan.json.
- Report rendered from `templates/burn-report.md` with a small ASCII sparkline of the last 14 days; keep under 3000 characters for mobile.
- Reconciliation: weekly job compares the metered total with the Anthropic Console usage export (CSV dropped in `ops/metering/console/`) and reports drift; drift above 10 percent flags the report.
- Idempotency: `usage_events` unique on `(session_id, source)`.
- Zod schemas for the result message subset used, so SDK shape changes fail loudly.

**Definition of done**

- Unit tests: price recomputation matches SDK cost within 1 percent on 20 recorded sessions; area classification; cap detection.
- Three daily reports posted in staging, screenshots at 375 px and 1280 px.
- `pnpm burn` output for the current spend pasted in this issue.
- Reconciliation job run once against a real Console export.
- Docs: `docs/pm/credit-metering.md` explaining sources, prices, caps and how to change `totalUsd`; changelog entry; Linear comment with screenshots.

**Edge cases**

- Session crashes before the `result` message: sum `usage` from streamed assistant messages and mark `source: "partial"`.
- Same issue worked by three sessions (retries): cost aggregates; report shows attempts count.
- Model differs from Fable 5.1 (a Sonnet sub-agent): price by `model` field, never assume.
- Cache read tokens dominate: report cache hit ratio; low ratio is a prompt-design signal for Atlas.
- Console export lags a day: reconcile on a 48-hour delay window.
- Negative or missing `total_cost_usd` (SDK bug): recompute from tokens, flag.
- Budget total changed mid-programme: recompute shares, keep history of allocations.

**Dependencies**

- `pm-linear/orchestrator` (sessions table and result stream).
- Feeds `agents/cost-controls`; consumes `agents/prompt-logging-hook` for non-SDK sessions when it lands.

**Agent**

Built by Atlas (lead); reviewed by Sentinel (Code Reviewer) and Ledger (Bookkeeper) for the arithmetic.

**Size**

M: straightforward data plumbing, but correctness of money numbers requires reconciliation.
