---
identifier: "PAP-306"
title: "Run a weekly plan re-audit: snapshot Linear, detect dependency drift, cycles, stale In Progress sessions, issues without specs; post the report to Linear"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P1"
type: "Review"
priority: 2
surfaces: ["Agent", "Staff"]
milestone: "PM module syncs both ways"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-93", "PAP-99", "PAP-105", "PAP-439"]
blocks: []
key: "pm-linear/weekly-reaudit"
url: "https://linear.app/paperos/issue/PAP-306/run-a-weekly-plan-re-audit-snapshot-linear-detect-dependency-drift"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:11:28.611Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-306: Run a weekly plan re-audit: snapshot Linear, detect dependency drift, cycles, stale In Progress sessions, issues without specs; post the report to Linear

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Review

**Goal**

Keep the plan honest while twenty sessions change it daily: every Monday an Atlas skill snapshots Linear, checks structure (cycles, phase inversions, milestone date inversions, orphan issues, missing relations stated in prose), health (stale `In Progress` sessions, issues bounced three times, budget vs plan) and quality (issues failing the contract, L issues that should split), then posts a Markdown report and files fixes as Backlog issues.

**Scope**

* In: skill `.claude/skills/plan-audit/` (SKILL.md plus `scripts/snapshot.ts`, `scripts/checks.ts`, `scripts/report.ts`), scheduled workflow `.github/workflows/plan-audit.yml` (Monday 05:00 UTC and `workflow_dispatch`), the pinned `Plan audit` issue, auto-filed fix issues capped at five per run.
* Out: fixing structure automatically (only proposes), the one-off audit this round produced, per-PR review (quality project).

**Spec**

* Snapshot: same query shape as `round2/snapshot.py`, stored under `docs/pm/audits/YYYY-MM-DD/snapshot.json` (issues, relations, projects, milestones, states, labels).
* Checks reuse `buildGraph` from PAP-99 and `validateIssue` from PAP-93: `CYCLE`, `PHASE_INVERSION` (P0 blocked by P1/P2), `MILESTONE_INVERSION`, `ORPHAN` (no project or milestone), `PROSE_DEP` (description names `PAP-n` as hard dependency without a relation), `STALE_SESSION` (`In Progress` with no heartbeat for 2 hours per PAP-288), `BOUNCED` (three `retry-*` labels), `CONTRACT_FAIL`, `SPLIT_CANDIDATE` (Size L and blocks three or more), `BUDGET_DRIFT` (area spend off plan share by 10 points, from PAP-98).
* Report `docs/pm/audits/YYYY-MM-DD/report.md`: counts, deltas since last week, top ten findings with links, under 4000 characters in the Linear comment with the full report linked.
* Fixes: up to five Backlog issues per run in contract format (Type Review, Character Atlas), deduped by finding hash; anything needing Justin goes as one decision card (PAP-94).

**Interface contract**

* Provides: `docs/pm/audits/<date>/{snapshot.json, report.md, findings.json}`, `Finding = { code, issues[], severity, suggestion }`, the `plan-audit` skill id in `skills.json`.
* Consumers: Justin (report), PAP-113 (finding badges optional), PAP-112 handbook links the latest report, PAP-29 drill reads `BUDGET_DRIFT`.
* Requires: PAP-93 validator, PAP-99 graph, PAP-105 skill format and `linear-update`, PAP-98 spend, PAP-288 heartbeats, Linear read access.

**Definition of done**

* Skill lint passes; workflow runs on schedule and on dispatch.
* First report posted covers every check with real numbers and finds the known-good state clean after round 2 (zero cycles, zero inversions).
* A seeded cycle on a `rehearsal` pair of issues is detected and a fix issue filed, then the pair is cleaned up.
* Docs section in the playbook; changelog; Linear comment with the report.

**Test plan**

* Unit: each check against the round-2 snapshot fixture with injected faults (cycle, inversion, prose dep, stale session).
* Integration: report renderer snapshot; dedupe of fix issues across two runs.
* e2e: dispatch run on staging with the rehearsal cycle.
* Visual: report comment at 375 px in the Linear mobile app.

**Demo**

Trigger `workflow_dispatch`, wait for the comment on the `Plan audit` issue, open the linked report and click one finding to its issue. Two minutes.

**Edge cases**

* Snapshot fails midway (rate limit): resume from cursor; partial report labelled `partial`.
* More than five fixes: file five, list the rest.
* Finding already has an open fix issue: comment on it instead of a new one.
* Justin marks a finding `wontfix` via reply grammar: suppressed for four weeks.
* PAP-6..PAP-12 strays: excluded.

**Dependencies**

Blocked by PAP-93, PAP-105, PAP-99. Soft: PAP-98, PAP-288.

**Agent**

Built by Atlas (lead); reviewed by Sentinel.

**Size**

M
