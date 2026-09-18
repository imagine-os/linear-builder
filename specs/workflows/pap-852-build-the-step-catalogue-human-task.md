---
identifier: "PAP-852"
title: "Build the step catalogue: human task, approval, wait, branch, for-each, sub-workflow, automation action, agent step, webhook, notify, generate document, request signature"
project: "workflows"
projectName: "Workflows, Approvals, Forms, Documents & E-Signature"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Developer"]
milestone: "Forms builder and document templates"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-136", "PAP-291", "PAP-389", "PAP-725", "PAP-851"]
blocks: ["PAP-853"]
key: "r4/workflows/step-catalogue"
url: "https://linear.app/paperos/issue/PAP-852/build-the-step-catalogue-human-task-approval-wait-branch-for-each-sub"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:34.463Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-852: Build the step catalogue: human task, approval, wait, branch, for-each, sub-workflow, automation action, agent step, webhook, notify, generate document, request signature

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Give workflows their vocabulary: twelve step kinds built with `defineStepKind`, each with a Zod config, an execute or suspend handler, a compensation where meaningful and a config form, reusing the PAP-389 action catalogue for anything that touches records or connectors so a workflow step and an automation action are the same code.

**Scope**

In: Kinds: `human.task` (assignees, form ref, due), `approval` (policy key, amount expression), `wait.duration|until|event` (event with `FilterTree` match), `branch` (conditions), `forEach` (over a context array or a view query, parallel with limit), `subWorkflow`, `action` (any PAP-389 action by id), `agent` (assistant `ActionPort` with a prompt, tool allow-list and confirmation policy; optional module), `webhook.send` (signed, PAP-389), `notify` (kind + recipients), `document.generate` (template id → file into context), `signature.request` (suspends until signed). Config forms generated from the Zod schemas with PAP-233 adapters and expression fields with autocomplete over the run context. Compensations: `action` delegates to the action's undo when present; `document.generate` deletes the generated file; `notify` sends a retraction only when configured.

Out: Custom code steps (never in v0.2; the `action` step and connectors are the extension points). Editor.

**Spec**

* `forEach` fan-out is bounded (default 500 items, plan-limited) and each item is its own idempotent step attempt; partial failure policy `continue | stopAll`
* `agent` steps never execute `send` or `money` tools; those produce approval requests through the approvals framework automatically
* `wait.event` registers a lightweight subscription row so the engine wakes only the runs that match, evaluated with the PAP-279 in-memory evaluator
* Every kind ships a fixture pair (valid, invalid config) and a conformance case; the docs generator (PAP-445) lists kinds per module
* `subWorkflow` passes a mapped input and receives a mapped output; recursion depth capped at 5

**Interface contract**

Provides: the twelve step kinds registered in `StepKindRegistry`, config forms, compensation handlers, fixtures. Consumes: run engine, action catalogue and template expressions (PAP-389), agent execution and assistant `ActionPort` (PAP-291, optional), notifications (PAP-136), forms and documents and signatures ports (own issues, soft). Consumed by: PAP-853, business packs, commerce and engagement processes.

**Definition of done**

* Each kind exercised in an integration test; the three model examples rebuilt from catalogue kinds only; docs page lists every kind with its config schema
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: config validation per kind; expression resolution with missing context keys; forEach bounds.
* Integration: agent step proposing a `money` tool produces an approval request, never an execution; wait.event wakes exactly the matching run.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Compose "new signed proposal → create project → for each line item create a task → notify owner → wait 7 days → if unpaid send reminder" from catalogue kinds and run it against the demo tenant.

**Edge cases**

* Action removed from the catalogue after publish: the step fails with `ACTION_GONE` at execute time and the definition is flagged in the editor
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-851 (hard), PAP-389 (hard), PAP-291 (soft), PAP-136 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/workflows/canvas-editor` = PAP-853, `r4/workflows/run-engine` = PAP-851.
