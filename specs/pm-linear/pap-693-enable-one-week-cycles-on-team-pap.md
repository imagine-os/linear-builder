---
identifier: "PAP-693"
title: "Enable one-week cycles on team PAP, assign every scheduled issue to the cycle of its execution-schedule start day, and make claim ordering prefer the active cycle"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Infra"
priority: 2
surfaces: ["Agent"]
milestone: "Linear configured for the pipeline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-91", "PAP-692"]
blocks: ["PAP-306"]
key: "r4/pm-linear/linear-cycles-weekly-and-auto-assignment"
url: "https://linear.app/paperos/issue/PAP-693/enable-one-week-cycles-on-team-pap-assign-every-scheduled-issue-to-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:27.069Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-20"
cycle: null
---

# PAP-693: Enable one-week cycles on team PAP, assign every scheduled issue to the cycle of its execution-schedule start day, and make claim ordering prefer the active cycle

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Cycles are off (`cyclesEnabled: false`), so the day-by-day plan in the Execution Schedule exists only in a Markdown table and Linear's burndown, velocity and "carry over" views are dark. One-week cycles aligned to the schedule (Mon 09-15 to 09-21 partial, 09-22 to 09-28, 09-29 to 10-05) give Justin the native progress view and give the orchestrator a tie-breaker that matches the plan.

**Scope**

* In: `teamUpdate({ cyclesEnabled: true, cycleDuration: 1, cycleCooldownTime: 0, cycleStartDay: 1, cycleIssueAutoAssignStarted: true, cycleLockToActive: false })` in `configure-workspace.ts`; `ops/linear/assign-cycles.ts` mapping `docs/execution-schedule.md` section 2 start days (parsed from `round2/sched/*.json`) to cycles; `pickNext()` tie-break in PAP-281 (active cycle first); PAP-306 check `CYCLE_CARRYOVER`; docs section "Cycles".
* Out: sprint ceremonies, velocity targets as gates, the PM-module cycle mirror (PAP-100 has `pm_cycle`; sync is the deferred sync extension).

**Spec**

* Cycle assignment: issue's start half-day from the schedule model decides the cycle; deferred issues get no cycle; umbrellas take the cycle of their first child; issues with no schedule row default to the milestone target date's cycle.
* Auto-assign: `cycleIssueAutoAssignStarted` puts anything moved to In Progress into the active cycle so unplanned claims are visible as scope creep; `cycleLockToActive` stays off so Atlas can plan ahead.
* `pickNext()` order becomes: active-cycle issues first, then least slack, priority, age (PAP-99 keeps this order in `score()` as `cycleBonus`).
* PAP-306 gains `CYCLE_CARRYOVER` (issues carried over twice) and `CYCLE_SCOPE_CREEP` (unplanned additions above 20 percent of the cycle's points); Atlas's Monday project update (round-4 issue) quotes cycle completion.
* `linear-workspace.json` records cycle ids by week; the configure `--check` reports setting drift as `manual`.

**Interface contract**

* Provides: team cycle settings, `assign-cycles.ts`, cycle ids in `linear-workspace.json`, `cycleBonus` in ordering, PAP-306 codes.
* Consumes: PAP-91 configure script, the schedule model in `round2/sched/`, PAP-281 `pickNext`, PAP-99 `score()`, PAP-306 checks.

**Definition of done**

* Cycles enabled; three cycles exist with the right dates; every scheduled leaf issue is assigned; counts and a cycle view screenshot at 1280 px posted.
* Claim ordering test: an active-cycle P2 issue is picked before a next-cycle P1 issue of equal slack.
* `--check` clean; changelog; Linear comment with the assignment table.

**Test plan**

* Unit: start-day to cycle mapping across the boundary days, umbrella rule, deferred exclusion, ordering test.
* E2E: live enable and assignment on team PAP; auto-assign verified by moving a rehearsal issue to In Progress.

**Demo**

Open the team's Cycles page: the current week's burndown with points from the estimates issue; move a rehearsal issue to In Progress and see it join the cycle. Under one minute.

**Edge cases**

* Milestone dates move after re-simulation (Atlas nightly): `assign-cycles.ts --apply` re-runs idempotently and comments only on changed issues.
* Cycle ends with open issues: Linear carries them over; `CYCLE_CARRYOVER` counts it; nothing is moved by hand.
* Cooldown or lock accidentally enabled by a human: reported as drift, never changed silently.
* Basic plan limits on cycles: none known; documented if encountered.

**Dependencies**

Hard: PAP-91, PAP-692. Soft: PAP-281, PAP-99, PAP-306.

**Agent**

Builder: Atlas (Dispatcher). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/pm-linear/linear-estimates-and-size-labels` = PAP-692.
