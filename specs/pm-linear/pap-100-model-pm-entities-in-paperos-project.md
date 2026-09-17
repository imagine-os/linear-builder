---
identifier: "PAP-100"
title: "Model PM entities in PaperOS (project, issue, cycle, milestone, comment, label) mirroring Linear's schema"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Developer", "Staff"]
milestone: "PM module syncs both ways"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-33", "PAP-305"]
blocks: ["PAP-101", "PAP-102", "PAP-204", "PAP-372"]
key: "pm-linear/pm-data-model"
url: "https://linear.app/paperos/issue/PAP-100/model-pm-entities-in-paperos-project-issue-cycle-milestone-comment"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:01.144Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-100: Model PM entities in PaperOS (project, issue, cycle, milestone, comment, label) mirroring Linear's schema

**Goal**

Give PaperOS its own project-management tables shaped like Linear's model so issues, projects, cycles, milestones, comments and labels can be mirrored one-to-one today and owned outright after cutover. Output is a Drizzle schema in its own package, oRPC procedures, three page specs and a mapping document, not UI.

**Scope**

* In: `packages/pm` (schema, migrations, seeds, procedures, mapping doc); page specs `specs/pm/issue-detail.spec.yaml`, `issue-list.spec.yaml`, `project.spec.yaml`; `docs/pm/data-model.md`.
* Out: sync (PAP-101), views (PAP-102), anything in `packages/core` (the audit moved PM out of core; `packages/core` stays owned by app-shell).

**Spec**

* Tables: `pm_team`, `pm_workflow_state`, `pm_project`, `pm_milestone`, `pm_cycle`, `pm_issue`, `pm_issue_relation`, `pm_label`, `pm_issue_label`, `pm_comment`, `pm_attachment`, `pm_external_ref`, each with `tenant_id`, uuid v7 `id`, `created_at`, `updated_at`, `archived_at`, `created_by` (principal id from PAP-60).
* `pm_issue`: `identifier` unique per `(tenant_id, team_id)`, `number`, `title`, `description`, `priority 0-4`, `estimate`, `state_id`, `assignee_id`, `parent_id`, `project_id`, `cycle_id`, `milestone_id`, `due_date`, `sort_order`, `started_at`, `completed_at`, `canceled_at`, `extra jsonb`.
* `pm_external_ref(entity_type, entity_id, system, external_id, external_url, synced_at, external_updated_at)` unique on `(system, external_id)`.
* Invariants: `parent_id <> id`; relation type enum `blocks | related | duplicate`; trigger sets `completed_at` on completed state; milestone must belong to the issue's project.
* Procedures `pm.issues.{list,get,create,update,archive}`, `pm.projects.*`, `pm.comments.*` via the oRPC layer (PAP-35), cursor pagination, filters state, assignee, label, project.
* Seeds: team PAP, nine states, label groups and three sample issues.

**Interface contract**

* Provides: `@paperos/pm` exporting the Drizzle tables, Zod `PmIssue`, `PmProject`, `PmComment`, the `pm.*` router, and `mapping.ts` (Linear field to column table shared with PAP-101).
* Consumers: PAP-101 upserts through `pm_external_ref`; PAP-102 reads via the views engine data source `pm_issue`; PAP-204 (ClickUp import) writes `pm_issue` rows; PAP-113 links character badges to `assignee_id`.
* Requires: PAP-33 core entities, PAP-34 RLS helpers, PAP-35 procedures, PAP-114 spec schema (draft allowed with `status: draft`).

**Definition of done**

* Migration applies and rolls back on fresh Postgres 17; `pnpm db:check` passes.
* Cross-tenant RLS test proves tenant A issues invisible to B.
* Procedure tests for create, update, archive, list with filters and pagination.
* Three page specs validate (PAP-115).
* `docs/pm/data-model.md` with ER diagram; changelog; Linear comment with the mapping table.

**Test plan**

* Unit: Zod schemas, identifier derivation, mapping table completeness against Linear's `Issue` type fields.
* Integration (PGlite and Postgres): migrations, triggers, RLS harness from PAP-34, procedures with `callAs` from PAP-35.
* e2e: none; no UI in this issue.
* Visual: ER diagram renders in the docs page at 1280 px.

**Demo**

Run `pnpm db:migrate && pnpm db:seed pm`, then `pnpm api call pm.issues.list --as staff` and see the three seeded issues with states and labels; call as another tenant and get an empty list. One minute.

**Edge cases**

* Team key renamed: old identifiers kept as aliases in `pm_external_ref`.
* Issue moved between projects: milestone nulled by trigger if it belongs elsewhere.
* Label deleted while in use: soft delete, history retained.
* Description over 200 KB: API rejects with a clear error.
* Cycles disabled: `cycle_id` nullable, procedures return empty.

**Dependencies**

Blocked by PAP-33. Soft: PAP-34, PAP-35, PAP-114. Blocks PAP-101, PAP-102, PAP-204.

**Agent**

Built by Forge (Schema Wright sub-agent); reviewed by Sentinel and Quill (docs).

**Size**

M
