---
identifier: "PAP-174"
title: "Build table automations: triggers (record change, schedule, form, inbound webhook), filter-tree conditions and actions (update record, notify, outbound webhook, connector call, create Linear issue) with a run log"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: ["PAP-388", "PAP-389", "PAP-390"]
blockedBy: ["PAP-38", "PAP-43", "PAP-121", "PAP-166", "PAP-279", "PAP-303"]
blocks: []
key: "tables/automations"
url: "https://linear.app/paperos/issue/PAP-174/build-table-automations-triggers-record-change-schedule-form-inbound"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:13.975Z"
---

# PAP-174: Build table automations: triggers (record change, schedule, form, inbound webhook), filter-tree conditions and actions (update record, notify, outbound webhook, connector call, create Linear issue) with a run log

**Goal**

Give every table Airtable, Notion and ClickUp class automations without code: triggers (record change, enters view, schedule, form, webhook, button), conditions from the shared filter builder, and actions (update or create records, notify, outbound webhook, connector call, scoped agent task, delay, branch) with a run log. This is how business templates encode their own workflows. Umbrella for three children.

**Scope**

Children (M each, same milestone, Backlog):

* PAP-388 Schema, trigger sources, run runtime on PAP-43 jobs with idempotency, loop guard, daily limits and circuit breaker.
* PAP-389 Action catalogue with scope classes, template expressions, `connector.call`, `agent.run`, `delay`, `branch`, signed `webhook.send`.
* PAP-390 Builder page from `automations.page.spec.yaml`, test run, run log grid with replay, five starter templates, import hooks.

Out: workflow canvas editing, arbitrary code actions, cross-tenant automations.

**Spec**

Decisions binding all children:

* `automation (tenant_id, name, enabled, trigger jsonb, conditions jsonb: FilterTree, actions jsonb[], owner_id, run_limit_per_day)`; `automation_run (status, trigger_payload, steps jsonb, error, duration_ms, cost_units)`.
* Record triggers come from `LISTEN/NOTIFY` emitted by PAP-38 audit triggers, debounced 500 ms per record; `record.entersView` diffs membership through PAP-163; schedules run in the tenant timezone; webhook URLs carry an HMAC secret with replay protection.
* Runs are `automations.run` jobs idempotent per `(automation_id, trigger_event_id)`; loop guard allows one self-retrigger then stops (`loop_guard`), chaining depth opt-in up to 3; circuit breaker after 20 consecutive failures.
* Every action declares `read|write|destructive`; destructive actions need admin enablement and are excluded from templates.
* Template expressions `[record.field]`, `[trigger.*]`, `[now]` share the PAP-171 expression subset.
* Run log retained 90 days and mirrored to audit with `actor_kind = 'automation'`.

**Interface contract**

Provides: `defineTrigger`, `defineAction({ key, scope, schema, run })`, procedures `automations.*`, `automationRuns.*`, event `automation.run.finished`, `button` field type (registered into PAP-164), webhook route `/api/automations/:id/webhook`, starter templates JSON consumed by PAP-208. Consumes: `FilterBuilder` and `FilterTree` (PAP-166, PAP-279), jobs (PAP-43), audit NOTIFY (PAP-38), connector registry (PAP-121), notifications (PAP-136 or its core), handoffs (PAP-108), `form.submitted` (PAP-169), signed outbound webhooks helper (PAP-222).

* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §3 (LISTEN/NOTIFY is only a wake-up hint and this issue debounces it; the outbox is the delivery path; record triggers subscribe to `record.created|updated|deleted` and register `automation.run.finished` with `defineTopic`; subscribers are idempotent on `event.id`, ordering is per `subject` only, delivery at-least-once); §1 (conditions are `FilterTree` from PAP-279, never a local grammar); §6 rows "Domain event envelope" and "RLS session-variable contract" (runs execute under `app.actor_kind='system'` with the triggering actor in `app.reason`).

**Definition of done**

* All three children Done.
* Parity matrix in `docs/tables/automations.md` against the PAP-162 trigger and action lists.
* Builder keyboard-operable (PAP-158 checklist); screenshots at 375 and 1280 in three themes; page spec merged.
* CHANGELOG; Linear comment with demo video.

**Test plan**

Umbrella `automations.e2e.spec.ts`: create "when Status becomes Done, notify owner and POST webhook" in the builder; test-run with a sample record; edit a grid cell and assert one run with two successful steps within 5 s; replay a webhook payload and assert rejection; fire a schedule across a DST boundary with a fixed clock; create a self-updating automation and assert `loop_guard`; fail a webhook 20 times and assert the breaker; import 1,000 rows with automations paused and assert zero runs.

**Demo**

Reviewer opens the automation builder, picks a trigger, adds a condition with the filter builder and two actions, presses "Test run" on a sample record, then edits that record in the grid and watches the run log fill in. Under two minutes.

**Edge cases**

* Trigger table deleted: automation disabled with a visible reason.
* Notify target removed from tenant: step skipped with warning, run continues.
* Webhook target 5xx for an hour: job retry schedule, then failed step with resend.
* Missing tenant timezone: UTC with a banner.
* Offline edits synced later: triggers fire at server apply time; log shows both timestamps.

**Dependencies**

PAP-166 (hard), PAP-43 (hard), PAP-38 (hard, NOTIFY source), PAP-121 (hard, connectors), PAP-279. Soft: PAP-136, PAP-171, PAP-169, PAP-155, PAP-108, PAP-222. Consumed by PAP-208, PAP-195 and PAP-180 (its work package 4, recurring invoices and dunning, exposes `recurring.pause|resume` as automation actions; soft, nothing here waits on it).

**Agent**

Builder: Nova (Views Engineer) with Forge on LISTEN/NOTIFY. Reviewer: Sentinel (Security Auditor for webhooks and scopes, Edge Case Hunter for loops and limits).

**Size**

L, split into three M children; start after the grid and filter builder are stable.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document [tables](<https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded (see PAP-91, NJ-1).
