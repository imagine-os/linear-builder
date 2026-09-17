---
key: "tables/automations/actions"
title: "Action catalogue with scope classes, template expressions, connector.call, agent.run, delay and branch"
project: "tables"
parent: "PAP-174"
phase: "P2"
type: "Build"
priority: 2
size: "M"
surfaces: []
milestone: "View sharing, formulas, dashboards"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc"
status: "pending"
---

# Action catalogue with scope classes, template expressions, connector.call, agent.run, delay and branch

**Goal**

Give automations something to do: a typed action catalogue with safe defaults, templated values and integrations through the connector registry.

**Scope**

In: `automations/actions/*.ts`, expression rendering shared with PAP-171, signed `webhook.send`. Out: triggers and UI (siblings).

**Spec**

* `defineAction({ key, scope: read|write|destructive, schema, run })`; `record.update|create|delete`, `notify`, `webhook.send` (signed, retried through jobs), `connector.call` (PAP-121 registry), `agent.run` (PAP-108 handoff, approval-gated), `delay` up to 30 days, `branch`.
* Destructive actions need admin enablement and are excluded from templates; `agent.run` and `connector.call` record cost units.
* Expressions ``record.field``, ``trigger.*``, ``now`` through the PAP-171 evaluator subset.

**Interface contract**

Provides: `defineAction`, `actions` registry, `renderTemplate`. Consumes: runtime child, notifications (PAP-136 core), connectors (PAP-121), handoffs (PAP-108), signed webhooks helper (PAP-222), PAP-171 evaluator (fallback to a minimal interpolation until it lands).

**Definition of done**

* Every action unit-tested with fixtures; scope enforcement test; webhook signature verified by a sample receiver.

**Test plan**

* Unit: each action's schema and run; destructive gating.
* Integration: notify and webhook steps from a real run; `delay` resumes after the clock advance.

**Demo**

Run an automation with notify plus webhook against a local receiver and read both step results in the run.

**Edge cases**

* Removed notify target skipped with warning; 5xx webhook retried on the jobs schedule.

**Dependencies**

Runtime child (hard), PAP-121, PAP-136 core, PAP-108, PAP-222 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.
