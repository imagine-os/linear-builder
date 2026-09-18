---
identifier: "PAP-707"
title: "Extend the PM data model with initiatives, project updates and health, cycle assignment rules, estimate roll-ups and SLA fields so the native PM module can replace every Linear feature the pipeline now uses"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "PM module syncs both ways"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-100"]
blocks: ["PAP-708"]
key: "r4/pm-linear/pm-model-initiatives-updates-cycles-rollups"
url: "https://linear.app/paperos/issue/PAP-707/extend-the-pm-data-model-with-initiatives-project-updates-and-health"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:25.345Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-707: Extend the PM data model with initiatives, project updates and health, cycle assignment rules, estimate roll-ups and SLA fields so the native PM module can replace every Linear feature the pipeline now uses

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by round 4 (not claimable before 2026-10-01; NJ-14 can reinstate). PAP-100 mirrors issues, projects, cycles, milestones, comments and labels. Round 4 turns on estimates, cycles, due dates, initiatives, project updates, triage and attachments in Linear, so the cutover promise ("Linear wins until cutover") only holds if the PM module can hold those too. This issue extends the schema and procedures; the sync extension is the sibling.

**Scope**

* In: `packages/pm` additions: `pm_initiative`, `pm_initiative_project`, `pm_project_update(health, body, posted_by, at)`, `pm_project.health|lead_id|priority|target_date`, `pm_cycle` auto-assignment rule and `pm_issue.cycle_id` trigger, estimate roll-up view `pm_progress` (points by project, milestone, cycle, state), `pm_issue.triage_state` and `pm_sla_breach`, `pm_attachment` kinds; procedures `pm.initiatives.*`, `pm.projectUpdates.*`, `pm.progress()`, `pm.sla.breaches()`; page specs `specs/pm/initiatives.spec.yaml`, `project-updates.spec.yaml`; `docs/pm/data-model.md` update.
* Out: the sync (sibling), rendering beyond specs (PAP-102 adds views later), Linear-specific fields (kept in `extra`).

**Spec**

* Initiatives: `pm_initiative(id, tenant_id, name, description, status, target_date, owner_id)` and the join table; health enum `onTrack|atRisk|offTrack` with `health_reason` on projects and updates.
* Progress: materialised view refreshed on `pm_issue` changes summing `estimate` for leaves (issues without children) by project, milestone, cycle and state type; umbrellas contribute nothing themselves (same rule as the Linear estimates issue).
* Cycles: `pm_cycle(start, end, number)` per team; trigger assigns `cycle_id` to the active cycle when an issue enters a started state and has none; carry-over count column.
* Triage: `pm_workflow_state.type` gains `triage`; `pm_issue` intake fields `source`, `source_ref`; SLA table mirrors the orchestrator's `sla_breaches`.
* Procedures follow PAP-35 conventions with cursor pagination and RLS; every new table has `tenant_id`, uuid v7, timestamps.

**Interface contract**

* Provides: new tables, `pm_progress` view, procedures above, page specs, mapping additions in `mapping.ts` for the sync sibling.
* Consumes: PAP-100 schema and mapping, PAP-34 RLS, PAP-35 procedures, PAP-114 spec schema, the orchestrator's `sla_breaches` and `issue_slack` shapes.

**Definition of done**

* Migrations apply and roll back; RLS harness green on new tables; `pm_progress` matches a hand count on the seeded team.
* Procedure tests for initiatives, project updates and progress; two page specs validate; docs; changelog.

**Test plan**

* Unit: roll-up arithmetic with umbrellas, cycle trigger, health enum, mapping completeness against Linear's Initiative and ProjectUpdate types.
* E2E: none; no UI in this issue.

**Demo**

Run `pnpm api call pm.progress --project quality` and read points by milestone and state; create a project update through `pm.projectUpdates.create` and see `health` on the project. Under one minute.

**Edge cases**

* Estimate changed on a Done issue: roll-up recomputes; history kept in `pm_issue_history`.
* Cycle boundaries edited: carry-over recount job.
* Initiative spanning tenants: forbidden; initiatives are per tenant.

**Dependencies**

Hard: PAP-100. Soft: PAP-34, PAP-35, PAP-114, PAP-102.

**Agent**

Builder: Forge (Schema Wright). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
