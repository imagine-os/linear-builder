---
identifier: "PAP-698"
title: "Atlas posts a Linear project update every Monday per project with health (on track, at risk, off track) computed from slack, cycle completion and spend, and sets project lead, priority and target dates"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "PM module syncs both ways"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-98", "PAP-306", "PAP-694", "PAP-695"]
blocks: []
key: "r4/pm-linear/project-updates-and-health-by-atlas"
url: "https://linear.app/paperos/issue/PAP-698/atlas-posts-a-linear-project-update-every-monday-per-project-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:28.448Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-698: Atlas posts a Linear project update every Monday per project with health (on track, at risk, off track) computed from slack, cycle completion and spend, and sets project lead, priority and target dates

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Zero project updates, no project health, no leads and no priorities: Linear's project pages are inert. The weekly re-audit (PAP-306) already computes everything a project update needs. This issue renders it as a native `projectUpdate` per project with a health value, keeps `lead`, `priority` and `targetDate` filled from the plan, and rolls into the initiatives so Justin sees eighteen coloured dots instead of reading a report.

**Scope**

* In: `src/reports/project-update.ts` in the orchestrator (Monday 06:30 UTC after PAP-306, and `pnpm pm:project-update --project <key> [--dry-run]`), health rule, `projectUpdateCreate` with body from `templates/project-update.md`, `projectUpdate` of `lead` (bot user of the owner agent from `plan.json`), `priority` (P0 projects Urgent, P1 High, P2 Medium) and `targetDate` (last milestone), initiative update for the release initiative summarising the eighteen, docs section.
* Out: the audit checks (PAP-306), the burn report (PAP-98), changing milestones (Atlas by hand), tenant-facing reports (PAP-102 shows the same data in-app later).

**Spec**

* Health: `offTrack` when any zero-slack chain in the project has negative slack or the project's remaining points exceed capacity to the target at the current landing rate; `atRisk` when slack under one day on the critical path or spend over 115 percent of the project's plan line; else `onTrack`; the rule and inputs are printed in the update.
* Body under 2000 characters: health line and why, milestones with points done and remaining, this week's landed PRs (from PAP-97 events), next week's planned claims (from the schedule and promotion candidates), risks (top three by slack), Needs Justin items touching the project, spend versus plan line.
* Initiative update for `PaperOS Core Platform v0.1.0 (Oct 1)`: one table of eighteen projects with health, points remaining and the RC checkpoint status.
* Project fields set idempotently: `lead` bot user per owner agent (falls back to the admin user when bots cannot lead), `priority` from phase, `targetDate` from the latest milestone; drift reported, never fought over with Justin (his edits win for a week).
* Dry run prints the updates; apply posts them and records ids in `project_updates_sent` for dedupe.

**Interface contract**

* Provides: `projectHealth(project): { health, reasons[] }`, weekly `projectUpdate` posts, initiative update, `pnpm pm:project-update`, the health rule documented for PAP-102 to render.
* Consumes: PAP-306 findings and snapshot, PAP-98 spend per project, `issue_slack` from the due-dates issue, PAP-97 landed-PR events, initiative ids, `plan.json` owners.

**Definition of done**

* Eighteen updates posted for a rehearsal week with health values matching a hand check on three projects (table); initiative update posted; screenshots at 1280 px and on a phone.
* Leads, priorities and target dates set on every project; `--check` reports no drift.
* Dry run and dedupe tested; docs; changelog; Linear comment with screenshots.

**Test plan**

* Unit: health rule on fixture inputs (slack, points, spend), body length cap, dedupe by week.
* E2E: rehearsal week on the live workspace with `--dry-run` reviewed by Atlas before `--apply`.

**Demo**

Open the Initiatives page and see eighteen health dots; click Quality Pipeline and read Monday's update with the reasons for `atRisk`. Under one minute.

**Edge cases**

* PAP-306 failed that morning: the update posts with `audit: unavailable` and health from slack and spend only.
* Justin changes a project's health by hand: respected for the week; the next update explains the computed value beside his.
* Project with no open issues: `onTrack` with `complete` note; deferred-only projects report `deferred`.
* Update body over 2000 characters: risks truncated to three with a link to the audit report.

**Dependencies**

Hard: PAP-306, PAP-98, PAP-694. Soft: PAP-97, PAP-102, PAP-695.

**Agent**

Builder: Atlas (Dispatcher). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/pm-linear/due-dates-slack-and-risk-alerts` = PAP-694, `r4/pm-linear/linear-initiatives-rollup` = PAP-695.
