---
identifier: "PAP-848"
title: "Specify the workflow model: definitions, versions, steps, runs, tasks and waits; event-bus triggers; the boundary with table automations"
project: "workflows"
projectName: "Workflows, Approvals, Forms, Documents & E-Signature"
phase: "P2"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Workflow contract and approvals"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-279", "PAP-302", "PAP-303", "PAP-388", "PAP-389", "PAP-556"]
blocks: ["PAP-847", "PAP-849", "PAP-851", "PAP-854", "PAP-856"]
key: "r4/workflows/workflow-model"
url: "https://linear.app/paperos/issue/PAP-848/specify-the-workflow-model-definitions-versions-steps-runs-tasks-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:16.200Z"
model: "claude-fable-5-1"
effort: "max"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-848: Specify the workflow model: definitions, versions, steps, runs, tasks and waits; event-bus triggers; the boundary with table automations

**Model / Effort:** Fable 5.1 (`claude-fable-5-1`) / max — Spec M

**Goal**

Write the one document that keeps workflows, table automations and approvals from becoming three engines: the workflow definition and run model, how a run is triggered by any PAP-303 event or by an automation action, what a step is, how human tasks and waits pause a run durably, how versions coexist, and the rule that a workflow orchestrates existing actions and never re-implements them.

**Scope**

In: `docs/workflows/model.md` (ADR style) and Zod schemas in the contract package: `WorkflowDefinition` (`id`, `tenant_id`, `name`, `version`, `trigger: { kind: 'event'|'manual'|'schedule'|'automation'|'form'|'api', topic?, filter: FilterTree }`, `steps: StepDefinition[]`, `inputs` schema, `status draft|published|retired`), `StepDefinition` (`id`, `kind`, `config`, `next`, `onError`, `timeout`), `WorkflowRun` (`definition_version`, `status`, `context jsonb`, `current_steps[]`, `started_by ActorRef`, `correlation EntityRef?`), `RunStep` (attempt log), `Task` (`kind human|approval`, `assignees`, `due`, `form?`, `decision`). Trigger semantics: exactly-once run creation per `(definition, event id)` through the outbox consumer with an idempotency key; schedule triggers use the recurrence engine (PAP-908) and PAP-43 cron; `automation` trigger means a PAP-389 action `workflow.start`. Boundary rule with PAP-174: automations are single-table, stateless reactions; anything with a wait, a human, a branch across modules or more than five actions is a workflow; the automation builder offers 'convert to workflow'. Versioning: runs pin the definition version; publishing a new version affects new runs only; `migrateRuns` is an explicit, logged operation with a step-id map.

Out: Engine implementation. UI. Forms, documents and signatures (own issues; the model only defines the step kinds that reference them).

**Spec**

* Every step kind is declared with `defineStepKind({ kind, config: zod, execute | suspend, resume?, compensate? })`; suspending kinds (human task, approval, wait, signature) persist a `RunStep` with a resume token; no step blocks a worker
* Context is a JSON document under a size limit (256 KB) with `EntityRef`s, never row copies; expressions use the PAP-389 template language over context and trigger payload
* Errors: per-step retry policy inherits PAP-43 defaults; `onError: fail | continue | compensate | goto`; compensation runs registered `compensate` handlers in reverse order
* Permissions: a definition runs with the identity of its `runAs` (the starter, a service principal, or a named role) declared at publish and checked by PAP-59; steps that write records are audited with `reason = workflow:<runId>`
* Observability: every run has a timeline (steps, attempts, waits, decisions) exposed through `workflows.runs.get` and rendered on the record panel tab

**Interface contract**

Provides: `docs/workflows/model.md`, schemas `WorkflowDefinition`, `StepDefinition`, `WorkflowRun`, `RunStep`, `Task`, the trigger and versioning rules, the automation boundary rule (also appended to PAP-174). Consumes: event envelope and topics (PAP-303), automation runtime and actions (PAP-388, PAP-389), `FilterTree` (PAP-279), `Money` and `EntityRef` (PAP-302). Consumed by: every issue in this project; PAP-174 (convert-to-workflow), PAP-94 (approval semantics), migration packs (`workflows[]` in `pack.yaml`).

**Definition of done**

* Document merged with ADR; schemas exported; the boundary paragraph added to PAP-174 by comment; migration for the five tables with RLS and harness enrolment
* Three worked examples in the doc: expense approval, proposal-to-project, patient intake, each as a definition JSON that validates
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: schema fixtures (valid and invalid per table); trigger idempotency key derivation; version pinning rules.
* Review: Sentinel checks the `runAs` model against PAP-59 and the threat model (a workflow is a way to act with borrowed authority).

**Demo**

Walk through the proposal-to-project example: event `signature.completed` starts a run that creates a project, drafts an invoice, waits for a manager approval and posts a comment; show the definition JSON validating.

**Edge cases**

* Trigger event replayed after an outage: idempotency on `(definition, eventId)` prevents a second run; the replay is logged
* Definition retired while runs are suspended: suspended runs finish on their pinned version; new triggers are ignored with a warning event

**Dependencies**

PAP-303 (hard), PAP-388 and PAP-389 (hard: reuse), PAP-279 and PAP-302 (hard), PAP-908 (soft: schedule triggers).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/data-layer/recurrence-engine` = PAP-908.
