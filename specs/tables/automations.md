---
identifier: "PAP-174"
title: "Build table automations: triggers (record change, schedule, form, inbound webhook), filter-tree conditions and actions (update record, notify, outbound webhook, connector call, create Linear issue) with a run log"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff", "Customer"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-121", "PAP-166", "PAP-279", "PAP-38", "PAP-43"]
blocks: []
key: "tables/automations"
url: "https://linear.app/paperos/issue/PAP-174/build-table-automations-triggers-record-change-schedule-form-inbound"
source: "plan/specs/gaps.json (round-1 canonical spec JSON)"
---

# PAP-174: Build table automations: triggers (record change, schedule, form, inbound webhook), filter-tree conditions and actions (update record, notify, outbound webhook, connector call, create Linear issue) with a run log

**Goal**

Justin asked for a table system with every feature Airtable, Notion and ClickUp have. All three ship automations, and `tables/feature-parity-audit` will list them, but no issue builds them: when a record enters a view, on a schedule, when a form is submitted or a webhook arrives, run conditions and actions without code. Automations also give every business template a way to encode its own workflow (send the reminder, move the deal, post to Slack), which is what "adapts to every type of business" needs in practice.

**Scope**

In:
- Schema `packages/views/src/automations/schema.ts`: `automation` (`tenant_id`, `name`, `enabled`, `trigger jsonb`, `conditions jsonb` (the filter tree from `tables/view-model-spec`), `actions jsonb[]`, `owner_id`, `run_limit_per_day`), `automation_run` (`status`, `trigger_payload`, `steps jsonb`, `error`, `duration_ms`, `cost_units`).
- Triggers: `record.created|updated|deleted` on a table, `record.entersView(viewId)` (evaluated by diffing view membership through `tables/query-compiler`), `schedule` (cron in tenant timezone), `form.submitted` (`tables/gallery-list-form`), `webhook.received` (per-automation URL with HMAC secret), `button.clicked` (a button field type added to `tables/field-types`).
- Conditions: reuse the filter builder UI and compiler; template variables `{{record.field}}`, `{{trigger.*}}`, `{{now}}` with a small expression language shared with `tables/formula-engine` when it lands.
- Actions: `record.update`, `record.create` (same or related table), `record.delete` (soft), `notify` (via `collab/notifications`: in-app, email, Slack), `webhook.send` (signed POST with retry), `connector.call` (an integration from `spec-builder/integrations-section` registry: Stripe payment link, Linear issue create, Notion page, Google Drive file), `agent.run` (enqueue a scoped character task through `agents/handoffs`, approval-gated), `delay` (up to 30 days), `branch` (condition-based).
- Runtime: each run is a `data-layer/jobs-queue` job (`automations.run`), idempotent per `(automation_id, trigger_event_id)`, with per-tenant daily limits and a circuit breaker after 20 consecutive failures.
- UI: automation builder page (spec under `specs/pages/tables/automations.page.spec.yaml`): trigger picker, condition editor, action list with drag reorder (`input/drag-drop`), test-run with a sample record, run log grid with replay; permission `automations.manage` scoped to the table's editors.
- Import hooks so `migration/airtable` and `migration/clickup-linear` can map source automations to this schema where semantics match, and list the rest as manual follow-ups.

Out: a general workflow canvas (use the canvas view for visualising, not editing), AI-generated automations beyond templated suggestions, cross-tenant automations, running arbitrary code (no script action in v1; `connector.call` and `agent.run` cover it safely).

**Spec**

- Triggers on record changes come from Postgres `LISTEN/NOTIFY` emitted by the audit triggers in `data-layer/audit-log`, debounced 500 ms per record so bulk edits fire once per record.
- Loop protection: a run that updates a record which would re-trigger the same automation is allowed once, then stopped with a `loop_guard` status; automations can opt into chaining depth up to 3.
- Every action declares a scope class (`read`, `write`, `destructive`) per `libraries/mcp-servers`; destructive actions require explicit enablement by a tenant admin and are excluded from templates.
- Run log retention 90 days; runs and steps visible in `data-layer/audit-log` with `actor_kind = 'automation'`.
- Costed: `agent.run` and `connector.call` record units for `pm-linear/credit-metering` style per-tenant budgets.
- Templates: five starter automations shipped with `migration/business-templates` (appointment reminder, deal stage notification, overdue invoice nudge, new lead assignment, weekly digest).

**Definition of done**

- Parity matrix in `docs/tables/automations.md` against Airtable, Notion and ClickUp trigger and action lists from `tables/feature-parity-audit`, with gaps marked.
- Playwright flow: create an automation "when status becomes Done, notify owner and post webhook", test-run, real run from a grid edit, run log shows both steps (screenshots at 1280 and 375).
- Schedule trigger fires in tenant timezone across a DST boundary (unit test with fixed clocks).
- Loop guard test; circuit breaker test; daily limit test.
- Webhook receiver rejects unsigned and replayed payloads (test).
- Accessibility: builder operable by keyboard alone (`input/screen-reader` sub-check).
- `CHANGELOG.md`, page specs merged, Linear comment with demo video.

**Edge cases**

- Trigger table deleted: automations referencing it disabled with a visible reason.
- Notification target user removed from tenant: `notify` step skipped with a warning, run continues.
- Outbound webhook target returns 5xx for an hour: retry schedule from the jobs package, then failed step with resend button.
- Thousands of records imported at once (`migration/import-framework`) matching a `record.created` trigger: imports run with `automations: paused` by default and a post-import choice to run for imported rows.
- Time zone missing on tenant: schedules default to UTC with a banner until set.
- Offline client edits synced later (`realtime/offline-queue`): triggers fire on server apply time, not on client edit time; the run log shows both timestamps.

**Dependencies**

`tables/filter-sort-group-ui` (condition editor and filter tree), `data-layer/jobs-queue` (runtime), `spec-builder/integrations-section` (connector registry). Soft: `collab/notifications`, `data-layer/audit-log`, `tables/formula-engine`, `tables/gallery-list-form`, `input/drag-drop`, `agents/handoffs`. Consumed by `migration/business-templates`, `growth/segments`, `business-core/invoicing` (overdue nudges).

**Agent**

Built by Nova (Views Engineer) with Forge for the LISTEN/NOTIFY plumbing. Reviewed by Sentinel (Security Auditor for webhooks and scope classes, Edge Case Hunter for loops and limits).

**Size**

L: a small rules engine plus UI; two to three sessions, after the views engine is stable.
