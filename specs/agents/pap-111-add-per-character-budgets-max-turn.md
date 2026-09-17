---
identifier: "PAP-111"
title: "Add per-character budgets, max-turn limits and a kill switch"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-98", "PAP-298", "PAP-300", "PAP-466"]
blocks: []
key: "agents/cost-controls"
url: "https://linear.app/paperos/issue/PAP-111/add-per-character-budgets-max-turn-limits-and-a-kill-switch"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:57:13.042Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-111: Add per-character budgets, max-turn limits and a kill switch

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Bound spend at every level so no runaway session or over-eager character can burn the budget: per-session and per-day caps per character, max-turn limits, per-issue caps by size, a release-week reserve and a kill switch that stops one session, one character or everything within seconds and leaves a clean record.

**Scope**

* In: `src/limits/{preflight,inflight,kill,reset}.ts` in the orchestrator, tables `budgets` extension and `kill_state`, the `budget-hold` label flow, the `KILL` comment grammar, `docs/pm/cost-controls.md`.
* Out: metering itself (PAP-98), eval caps content (PAP-110 passes its cap in).

**Spec**

* Limits: schema `budget` (`perSessionUsd`, `perDayUsd`, `maxTurns`) plus config `limits.perIssueUsd` by Size (S 60, M 180, L 450), `globalPerDayUsd`, `reserveUsd`; label override `budget:<usd>` up to twice the default.
* Pre-flight before spawn: character daily remaining, issue remaining across attempts, global remaining, reserve untouched; expected cost is the character's median of the last ten sessions (default $25); failure comments and labels `budget-hold`.
* In-flight: `liveTotal(sessionId)` from PAP-98; at 80 percent inject a wrap-up user turn asking for the handoff (PAP-108); at 100 percent abort through the SDK abort controller with a 20 s grace, commit `wip:`, push, post footer `status: "partial"`.
* Kill switch: comment `KILL <PAP-key> | KILL <character> | KILL ALL [hard]` by Justin on any issue or the burn report; also `POST /kill` with an admin token; `/status` shows `paused`; `RESUME` reverses. The poll loop scans the burn-report comments every 30 s as a webhook fallback.
* Reviewers (Sentinel subs) have a separate daily pool matching the 30 percent review share.

**Interface contract**

* Provides: `preflight(issue, character): Allow | Hold`, `attachInflight(session, abortController)`, `kill(scope, hard?)`, `resume(scope)`, `limitsFor(character)`, events `limit.warned`, `limit.aborted`, `kill.requested`, `kill.completed` on the PAP-96 bus, `/status.limits` block.
* Consumers: PAP-96 (spawn path and abort), PAP-99 (`budget-hold` exclusion), PAP-110 (`--cap` per run), PAP-113 (paused ring, pause button calls `kill(character)`), PAP-108 (over-budget receivers queue).
* Requires: PAP-98 `liveTotal`, `spent`, `budgets`; PAP-103 `budget` fields; PAP-94 for reserve release decisions; PAP-107 `session.killed` writer.

**Definition of done**

* Unit tests for pre-flight decisions, 80 and 100 percent thresholds, reset at day boundary, cap arithmetic.
* Integration: a toy session with `perSessionUsd: 2` is warned then aborted; `wip:` pushed; footer posted (recording).
* `KILL ALL` from Justin stops three running sessions within five seconds; `/status` paused; `RESUME` works (recording).
* Runbook including "what to do if the budget is gone"; changelog; Linear comment with recordings.

**Test plan**

* Unit: decision table, median cost with fewer than ten sessions, label override cap, reviewer pool isolation.
* Integration: fake meter and fake clock driving in-flight thresholds; grace period lets a mocked `git push` finish.
* e2e: kill and resume on staging with three sessions.
* Visual: `/status` limits block at 1280 px.

**Demo**

Start a toy session with `perSessionUsd: 1`, watch `/status` show the running total, see the wrap-up warning appear in the transcript at 80 percent and the abort with a `wip:` commit at 100 percent. Then post `KILL ALL` and watch every slot pause. Two minutes.

**Edge cases**

* Metering lag: reconcile with the SDK `result` and charge overrun to the next allowance.
* Kill during push: grace lets it finish; never a worktree without a `wip:` commit.
* Webhooks down when `KILL` is posted: poll scan catches it within 30 s.
* Reserve breached in the final days: only Justin releases it via PAP-94.
* Sub-agents inside a session: parent cap applies; SDK cost includes them.

**Dependencies**

Blocked by PAP-98. Integrates with PAP-96, PAP-103, PAP-94.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel.

**Size**

M
