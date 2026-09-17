---
identifier: "PAP-95"
title: "Decompose PAP-5 (startup procedure inefficiency) into this master plan's projects and close it with a summary comment"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Docs"
priority: 2
surfaces: ["Agent"]
milestone: "Linear configured for the pipeline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-91"]
blocks: []
key: "pm-linear/pap5-decompose"
url: "https://linear.app/paperos/issue/PAP-95/decompose-pap-5-startup-procedure-inefficiency-into-this-master-plans"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:17.269Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-95: Decompose PAP-5 (startup procedure inefficiency) into this master plan's projects and close it with a summary comment

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Docs S

**Goal**

Close the loop on the issue that started everything without contradicting PAP-29: PAP-5 ("how quickly do we get from blank screen to electrons") is rewritten into a measurable scoreboard issue that links every project of this plan and stays open as the standing benchmark record; PAP-29 owns the weekly measurement and the eventual closure. Nothing is created twice and nothing is closed early.

**Scope**

* In: rewrite of the PAP-5 description (original title untouched, original text preserved in `Original notes`), a generated Decomposition table, `related` relations from PAP-5 to the first issue of each of the 17 projects, `docs/pm/pap5-decomposition.md`.
* Out: closing PAP-5, creating a benchmark child (PAP-29 records results directly on PAP-5), any project edits.

**Spec**

* New PAP-5 body in contract format: Goal restated as "time from `paperos create <app>` to a reviewed page on web and desktop under 4 hours wall-clock and under $150 of credits"; Scope: the 17 projects; Spec: how PAP-29 measures; Definition of done: PAP-29 reports three consecutive weekly runs under target; `Scoreboard` table appended by PAP-29 (date, stage timings, cost).
* Script `ops/linear/decompose-pap5.ts` reads `plan.json`, resolves projects by id from `linear-workspace.json`, renders the table (project, link, phase, contribution to startup time), updates PAP-5 with `issueUpdate`, creates `related` relations to each project's first milestone issue by `createdAt` (for example PAP-13 for app-shell) only if absent. Idempotent.
* Description under 4000 characters; the full table lives in the docs file and is linked.
* PAP-5 stays in `Backlog`, labelled `Phase/P2`, `Type/Review`, `Developer`, project app-shell (unchanged).

**Interface contract**

* Provides: `docs/pm/pap5-decomposition.md`, the `Scoreboard` table format `| date | clone | install | first page | PR | gates | demo URL | total | cost |` that PAP-29 appends to, the list `pap5.relatedIssues` in `linear-workspace.json`.
* Consumers: PAP-29 (writes scoreboard rows and closes PAP-5 when the target holds), PAP-112 handbook (links the origin story), the blueprint document.
* Requires: PAP-91 ids; plan.json in the orchestrator repo.

**Definition of done**

* PAP-5 passes `pnpm contract:audit PAP-5` with warnings only (PAP-93) while keeping the original title.
* 17 `related` relations exist; `issue.relations` output pasted in the comment.
* `Original notes` section preserves Justin's text verbatim.
* Docs file committed; changelog entry; screenshot of PAP-5 at 1280 px.
* No `Needs Justin` item raised; informational comment on PAP-5 explains that PAP-29 owns closure.

**Test plan**

* Unit: table rendering from a plan fixture; idempotency (second run plans zero mutations); character limit check.
* Integration: mocked SDK run creating relations only for missing pairs.
* e2e: live run, then `--check` prints no drift.
* No visual breakpoints beyond the Linear screenshot.

**Demo**

Run `pnpm pap5:decompose --check` (shows planned changes), `--apply`, then open PAP-5 in Linear and click two project links from the table. One minute.

**Edge cases**

* A project from plan.json is missing in Linear: exit non-zero before any update, list the missing names.
* Justin edited PAP-5 since the snapshot: diff and keep his additions under `Original notes`.
* Relation already exists: success, no duplicate.
* First issue of a project is in `Duplicate` state (PAP-6..12 strays): skip strays, choose the first canonical issue.
* Title over the Linear limit: never touched.

**Dependencies**

Blocked by PAP-91. Coordinates with PAP-29 (scoreboard owner).

**Agent**

Built by Quill (Changelog Scribe sub-agent); reviewed by Atlas.

**Size**

S
