---
identifier: "PAP-701"
title: "Workspace views as code: create the pipeline views (ready by slack, in review awaiting gates, stuck sessions, per character, at risk, triage inbox, deferred v0.2, critical path) with the `Pipeline:` prefix, create-only"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P1"
type: "Infra"
priority: 3
surfaces: ["Staff"]
milestone: "Linear configured for the pipeline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-91"]
blocks: []
key: "r4/pm-linear/pipeline-views-as-code"
url: "https://linear.app/paperos/issue/PAP-701/workspace-views-as-code-create-the-pipeline-views-ready-by-slack-in"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:28.825Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 2
dueDate: "2026-09-20"
cycle: null
---

# PAP-701: Workspace views as code: create the pipeline views (ready by slack, in review awaiting gates, stuck sessions, per character, at risk, triage inbox, deferred v0.2, critical path) with the `Pipeline:` prefix, create-only

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Infra S

**Goal**

Six custom views exist, all generic (Bugs, High Priority, My Work). The pipeline's real questions (what is Ready and tightest on slack, what sits In Review waiting on gates, which sessions are stuck, what is deferred) have no saved answer, so Justin builds filters on his phone. The deny list forbids agents from touching existing views; this issue creates new ones only, prefixed and idempotent.

**Scope**

* In: `ops/linear/views.yaml` (name, description, icon, colour, `filterData`, `projectFilterData`, grouping and ordering hints) and `configure-workspace.ts --views` using `customViewCreate` (never `customViewUpdate` or delete), eight initial views, ids in `linear-workspace.json.views`, a `docs/pm/views.md` page with a screenshot per view, an Insights note describing the charts Justin can pin (estimate by state, cycle burndown, health by initiative).
* Out: editing or deleting any existing view (Threat Model section 4), Linear Insights configuration (UI only; documented), in-app PM views (PAP-102).

**Spec**

* Views: `Pipeline: Ready by slack` (state Ready for Claude, ordered by due date then priority), `Pipeline: In Review awaiting gates` (In Review, no `gate/…` green comment in 2 h, via label `gates-pending` set by PAP-97), `Pipeline: Stuck sessions` (In Progress and label `stuck` from PAP-288), `Pipeline: Needs Justin` (state, oldest first), `Pipeline: At risk` (due within 3 days or `slack-risk` label from the due-dates issue), `Pipeline: Triage inbox` (state Triage), `Pipeline: Deferred v0.2` (label Deferred), `Pipeline: Critical path` (label `critical-path` applied nightly to the five zero-slack chains), plus one per character `Pipeline: <Character>` once the `Character/*` group exists (PAP-91).
* Labels the views rely on (`gates-pending`, `stuck`, `slack-risk`, `critical-path`) are created by the same script and set by the named issues; the views file documents which issue maintains each label.
* Create-only: a view with the same name already present is recorded and left untouched; `--check` lists views in the file that do not exist.
* Sharing: all views `shared: true`, owner the admin user; icons and colours from the file.

**Interface contract**

* Provides: `views.yaml` schema, `Pipeline:` naming convention, label set for view filters, view ids in `linear-workspace.json`.
* Consumes: PAP-91 script, labels from PAP-97 (`gates-pending`), PAP-288 (`stuck`), the due-dates issue (`slack-risk`, `critical-path`), `Character/*` group.

**Definition of done**

* Eight views plus nine character views exist; screenshots at 1280 px and on a phone; no existing view changed (before and after listing).
* `--check` clean; docs page; changelog; Linear comment with the screenshots.

**Test plan**

* Unit: filter serialisation per view against Linear's `filterData` shape, create-only guard.
* E2E: live create; re-run no-op; deny-list test that `customViewUpdate` is never called.

**Demo**

Open `Pipeline: Ready by slack` on a phone and read the top three issues with due dates; open `Pipeline: Stuck sessions` and see it empty. Under one minute.

**Edge cases**

* A label a view depends on does not exist yet: view still created; the filter returns empty until the label appears; documented per view.
* Justin renames a `Pipeline:` view: `--check` reports the missing name; nothing recreated unless `--apply --recreate-view <name>`.
* View limit on the plan: documented; character views are optional and created last.

**Dependencies**

Hard: PAP-91. Soft: PAP-97, PAP-288, PAP-694.

**Agent**

Builder: Atlas (Dispatcher). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/pm-linear/due-dates-slack-and-risk-alerts` = PAP-694.
