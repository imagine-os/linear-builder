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
blockedBy: ["PAP-98"]
blocks: []
key: "agents/cost-controls"
url: "https://linear.app/paperos/issue/PAP-111/add-per-character-budgets-max-turn-limits-and-a-kill-switch"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-111: Add per-character budgets, max-turn limits and a kill switch

**Goal**

Bound spend at every level so no runaway session or over-eager character can burn the budget: per-session and per-day caps per character, max-turn limits, per-issue caps derived from size, and a kill switch that stops one session, one character or everything within seconds and leaves a clean record.

**Scope**

In:
- Limits from the character schema `budget` (`perSessionUsd`, `perDayUsd`, `maxTurns`) plus orchestrator config `limits` (`perIssueUsd` by estimate S 60 / M 180 / L 450, `globalPerDayUsd`, `reserveUsd` kept untouchable for release week).
- Pre-flight check in `pm-linear/orchestrator` before spawning: character daily remaining, issue remaining (across attempts), global remaining; if any is below the expected session cost (median of the character's last 10 sessions, default $25), do not spawn; comment on the issue with the reason and label `budget-hold`.
- In-flight enforcement: the SDK stream is metered live (`pm-linear/credit-metering` running total); at 80 percent of the session cap the orchestrator injects a warning via the next user turn asking the session to wrap up and post its handoff; at 100 percent it aborts the query, commits `wip:`, pushes, posts the footer with `status: "budget-exceeded"`, and moves the issue to `Needs Justin` only if it is the third such event, otherwise back to `Ready for Claude` with `retry-n`.
- `maxTurns` passed to the SDK; turn exhaustion handled like budget exhaustion.
- Kill switch: `POST /admin/kill {scope: session|character|all, id?, reason}` protected by an admin token, plus CLI `pnpm kill --all "reason"`, plus a Linear escape hatch: a comment `KILL ALL` or `KILL <character>` from Justin on the burn-report issue; effect within 5 seconds: abort streams, mark sessions `killed`, pause claiming; `POST /admin/resume` re-enables.
- Daily reset at 00:00 UTC; caps visible on `/status` and in the burn report; changes to caps require a `Needs Justin` approval when they increase.
- Alerts: 50, 80, 95 percent of global daily budget posted as comments on the burn-report issue.

Out: metering arithmetic (`pm-linear/credit-metering`), Anthropic Console spend limits (documented as the outer wall, configured manually), per-tenant product billing.

**Spec**

- Module `src/limits/` in the orchestrator: `preflight.ts`, `inflight.ts`, `kill.ts`, `reset.ts`; state in `orchestrator.budgets` and `orchestrator.kill_state`.
- Abort uses the SDK query's abort controller; a grace period of 20 seconds lets the current tool call finish unless scope is `all` with `hard: true`.
- All limit decisions are logged as events with the numbers used, for the eval harness and post-mortems.
- Reviewers (Sentinel subs) have separate daily pools so a builder spending spree cannot starve review, matching the 30 percent review share.
- Character caps default from `roster.yaml`; per-issue override via label `budget:<usd>` (max 2x default without approval).

**Definition of done**

- Unit tests for pre-flight decisions, 80/100 percent thresholds, reset, and cap arithmetic with fake clocks and fake meters.
- Integration: a session on a toy issue with `perSessionUsd: 2` is warned and then aborted; `wip:` commit pushed; footer posted (recording).
- Kill switch: `KILL ALL` comment from Justin stops 3 running sessions within 5 seconds; `/status` shows paused; resume works (recording).
- Alerts observed at thresholds in a simulated day.
- Runbook `docs/pm/cost-controls.md` including "what to do if the budget is gone"; changelog entry; Linear comment with recordings.

**Edge cases**

- Metering lag means the cap is discovered late: compare with the SDK `result` cost afterwards and charge the overrun to the next session's allowance.
- Kill during a git push: let the push finish (grace), never leave a half-written worktree without a `wip:` commit.
- Justin's `KILL` comment arrives while Linear webhooks are down: the poll loop also scans the burn-report issue comments every 30 seconds.
- Character has no sessions yet (no median): use the default expected cost.
- Reserve breached in the final days: only Justin can release it through `Needs Justin`.
- Clock at daily reset while sessions are running: sessions keep their original day's allowance; new spend counts to the new day.
- Sub-agent spawns inside a session inherit the parent's session cap; the SDK cost includes them.

**Dependencies**

- `pm-linear/credit-metering` (live totals, price table, budgets table).
- Integrates with `pm-linear/orchestrator` launch path and `agents/character-schema` budget fields.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel (Security Auditor for the admin endpoints, Edge Case Hunter for abort paths) and Ledger for the arithmetic.

**Size**

M: focused logic with two live recordings to prove abort and kill behaviour.
