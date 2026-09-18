---
identifier: "PAP-850"
title: "Build the My Tasks inbox: human tasks and approvals across workflows as a saved view with SLAs, bulk actions, live updates and a dashboard block"
project: "workflows"
projectName: "Workflows, Approvals, Forms, Documents & E-Signature"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Workflow contract and approvals"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-169", "PAP-172", "PAP-381", "PAP-386", "PAP-600", "PAP-620", "PAP-624", "PAP-849"]
blocks: []
key: "r4/workflows/task-inbox"
url: "https://linear.app/paperos/issue/PAP-850/build-the-my-tasks-inbox-human-tasks-and-approvals-across-workflows-as"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:26.667Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-10-01"
cycle: null
---

# PAP-850: Build the My Tasks inbox: human tasks and approvals across workflows as a saved view with SLAs, bulk actions, live updates and a dashboard block

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Give every person one list of what is waiting on them: human tasks and approval requests from every workflow and module, as a saved list view with due dates and SLA badges, live updates, bulk complete, a portal variant for customer-facing tasks (sign this, upload that) and a dashboard block.

**Scope**

In: Dataset `tasks` registered with PAP-161 unifying `task` and `approval_request` rows assigned to the principal (or their roles); route `/tasks` on the list view (PAP-169) with default sort by due, group by kind; `?r=` opens the task drawer with the form or decision UI. Portal route `/portal/tasks` limited to `audience: customer` tasks (signature requests, form completions, document uploads) with the PAP-62 shell. Live updates via `useLiveEvents('workflow.task.*')` (PAP-381); bulk complete for tasks without required fields; snooze (re-due) with a reason. Dashboard block `tasks.mine` for PAP-386 with count and next due; notification kinds `task.assigned`, `task.due_soon` (24 h) through PAP-136.

Out: Task creation UI beyond workflows and the assistant. PM issues (PAP-100 remain separate; a workflow step may create one).

**Spec**

* A task is visible to its assignees, the run starter and roles with `tasks.manage`; completing requires the assignee or a delegate; every completion writes the `Task.decision` or form payload to the run context
* SLA badge states: on track, due soon (25 percent of SLA left), overdue; colours from PAP-66 semantic tokens with text labels for a11y
* Bulk complete never applies to approvals above the policy's `bulkLimit` or to tasks with required form fields
* Reassignment is allowed to anyone the policy would have allowed; the run timeline records it

**Interface contract**

Provides: `tasks` dataset and `/tasks`, `/portal/tasks` pages, task drawer, dashboard block, notification kinds `task.*`. Consumes: approvals framework, list view and saved views (PAP-169, PAP-172), live events (PAP-381), dashboard blocks (PAP-386), notifications (PAP-136), portal shell (PAP-62). Consumed by: workflows run engine (human task step), commerce (work-order tasks), engagement (customer signature and intake tasks), assistant (notes to tasks).

**Definition of done**

* Demo tenant shows mixed tasks and approvals for a manager; portal shows a signature task for a customer; live update proven across two windows
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: SLA state math across timezones; bulk eligibility; visibility predicate.
* E2E: complete a task with a required form, snooze another, approve from the drawer; phone width list and drawer.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

As a manager, open `/tasks`, approve one expense and complete an onboarding checklist task; open the portal as a customer and see the signature task waiting.

**Edge cases**

* Task assigned to a role with no current members: shown to `tasks.manage` holders with an "unassigned" badge and escalated after the SLA
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-849 (hard), PAP-169 and PAP-172 (hard), PAP-381 and PAP-386 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/workflows/approvals-framework` = PAP-849.
