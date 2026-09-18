---
identifier: "PAP-694"
title: "Set due dates from milestone targets, compute remaining critical path and slack per issue nightly, and post due-date risk comments and a Slack-at-risk view for chains that will miss"
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
blockedBy: ["PAP-91", "PAP-99"]
blocks: ["PAP-306", "PAP-698"]
key: "r4/pm-linear/due-dates-slack-and-risk-alerts"
url: "https://linear.app/paperos/issue/PAP-694/set-due-dates-from-milestone-targets-compute-remaining-critical-path"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:27.277Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-22"
cycle: null
---

# PAP-694: Set due dates from milestone targets, compute remaining critical path and slack per issue nightly, and post due-date risk comments and a Slack-at-risk view for chains that will miss

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Zero issues carry a due date, so Linear's overdue indicators, due-soon filters and the mobile app's reminders are unused, and the schedule's zero-slack chains are visible only in a document. This issue sets `dueDate` from the milestone target on every issue, computes remaining critical path and slack per issue from sizes and the `blocks` graph every night, and turns negative slack into a comment on the issue and a row in an at-risk view, so the promotion order, Atlas's project update and Justin's phone all read the same risk.

**Scope**

* In: `ops/linear/set-due-dates.ts` (milestone target to `dueDate`, idempotent), `src/scheduler/slack.ts` in the orchestrator (`criticalPath(issue)`, `slackHours(issue)` from `buildGraph` (PAP-99) and Size durations), nightly job writing `issue_slack(issue_id, remaining_hours, slack_hours, chain_json, at)`, risk comment template `templates/slack-risk.md` (one per issue per day, edited in place), `/status.slack` block, `docs/pm/scheduling.md`.
* Out: moving milestone dates (Atlas decides; PAP-306 proposes), per-issue due dates set by hand (respected, never overwritten), the PM-module mirror (`pm_issue.due_date` exists in PAP-100).

**Spec**

* Due date rule: `dueDate = milestone.targetDate` for every non-deferred issue lacking a hand-set date (hand-set means `dueDate` differs from the milestone and the last actor is Justin); umbrellas inherit their latest child; deferred issues get 2026-10-15 as a placeholder for the v0.2 milestone (NJ-19).
* Slack model (Execution Schedule section 1): S 0.5 day, M 1 day, L 2 days; sessions start 03:30Z and 15:30Z; remaining critical path of an issue is the longest chain of open work from it to the end of its milestone's dependents; `slack = milestone target minus (now plus remaining path)`; branch-start rule credits an In Review blocker as done for path purposes.
* Nightly at 05:30 UTC and on demand (`pnpm scheduler:slack --dry-run`): recompute for all open issues, upsert `issue_slack`, comment on issues whose slack turned negative or fell under one half-day (`slack-risk: -1.5 days; chain PAP-25 -> PAP-96 -> PAP-97; option: soften PAP-x or move milestone`), edit the same comment on later nights, remove nothing.
* Ordering: `promote()` and `pickNext()` read `slack_hours` as the first key (least slack first), replacing the interim milestone-date rule.
* Views: a workspace view `Pipeline: at risk` (filter `dueDate < +3d AND state not completed`) created by the views-as-code issue; `/status.slack` lists the ten tightest chains for PAP-113 and the Monday project update.

**Interface contract**

* Provides: `dueDate` on every issue, `issue_slack` table, `slackHours()`, `/status.slack`, comment template, the placeholder v0.2 date convention.
* Consumes: PAP-91 ids and milestones, PAP-99 `buildGraph` and `score()`, PAP-281 `pickNext`, promotion pass, PAP-97 `linearComment`, `round2/sched/` model for calibration.

**Definition of done**

* Every open issue has a due date equal to its milestone target unless hand-set; before and after counts posted; `--check` reports drift.
* Slack computed for the live graph matches the Execution Schedule's zero-slack chains (orchestrator, API and sync, permissions, gates, tables) within one half-day (table).
* Seeded slip (fixture blocker moved two days) turns three downstream issues negative and posts three comments once; the second night edits, not duplicates.
* `pickNext()` prefers the tighter chain (test); docs; changelog; Linear comment with the at-risk table and a phone screenshot of an overdue badge.

**Test plan**

* Unit: path and slack arithmetic on fixture graphs with cycles rejected, hand-set date detection, comment idempotency.
* E2E: nightly job on staging against the live snapshot; seeded slip fixture.

**Demo**

Run `pnpm scheduler:slack --dry-run` and read the ten tightest chains; open one issue in the Linear mobile app and see its due date and the `slack-risk` comment. Under one minute.

**Edge cases**

* Milestone without a target date: issues keep no due date and the job lists the milestone for Atlas.
* Justin sets a due date earlier than the milestone: respected; slack is computed against his date.
* Graph edit creates a cycle: slack job skips the cycle members and PAP-99 reports it once.
* Twenty comments would be posted in one night: capped at ten; the rest go to the Plan audit issue.

**Dependencies**

Hard: PAP-91, PAP-99. Soft: PAP-281, PAP-97, PAP-306, PAP-691.

**Agent**

Builder: Atlas (Dispatcher). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/pm-linear/orchestrator-promotion-pass` = PAP-691.
