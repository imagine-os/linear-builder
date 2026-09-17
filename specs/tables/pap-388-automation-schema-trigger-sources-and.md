---
identifier: "PAP-388"
title: "Automation schema, trigger sources and the run runtime with idempotency, loop guard, limits and circuit breaker"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: "PAP-174"
children: []
blockedBy: ["PAP-38", "PAP-43", "PAP-279"]
blocks: ["PAP-389"]
key: "tables/automations/model-triggers"
url: "https://linear.app/paperos/issue/PAP-388/automation-schema-trigger-sources-and-the-run-runtime-with-idempotency"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:44.007Z"
---

# PAP-388: Automation schema, trigger sources and the run runtime with idempotency, loop guard, limits and circuit breaker

**Goal**

Store automations and fire them reliably from record changes, view membership, schedules, forms, webhooks and buttons, with the guards that keep a rules engine safe.

**Scope**

In: `automations/{schema,triggers/*,runtime}.ts`, `button` field type, webhook route, `automation_run` writes. Out: actions (sibling), UI (sibling).

**Spec**

* Tables per the parent; record triggers from PAP-38 `LISTEN/NOTIFY` debounced 500 ms; `record.entersView` diffs membership through PAP-163; cron in tenant timezone; `form.submitted` from PAP-169; HMAC webhooks with replay protection; `button.clicked`.
* Runs are PAP-43 jobs idempotent per `(automation_id, trigger_event_id)`; loop guard, chaining depth up to 3, daily limit, circuit breaker after 20 failures; imports run with automations paused.

**Interface contract**

Provides: `defineTrigger`, `enqueueRun`, `automations.*` CRUD, webhook route, `button` type. Consumes: audit NOTIFY (PAP-38), jobs (PAP-43), compiler (PAP-163), `form.submitted` (PAP-169), PAP-164 registry.

**Definition of done**

* Unit tests for every guard; DST schedule test; webhook replay rejected; runs visible in audit.

**Test plan**

* Unit: debounce, loop guard, breaker, limits.
* Integration: grid edit produces exactly one run; 1,000-row import with automations paused produces none.

**Demo**

Create an automation via the API, edit a record and watch `automation_run` rows appear.

**Edge cases**

* Trigger table deleted disables with a reason; missing timezone defaults to UTC with a banner.

**Dependencies**

PAP-38, PAP-43, PAP-163 (hard), PAP-169 (soft). Blocks siblings.

**Agent**

Builder: Nova with Forge on NOTIFY. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: runtime guards.
