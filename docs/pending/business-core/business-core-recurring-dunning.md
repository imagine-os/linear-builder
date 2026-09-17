---
key: "gap/business-core/recurring-dunning"
title: "Build recurring tenant invoices and dunning: schedules, automatic reminders, late fees, payment retry for tenant-to-customer billing"
project: "business-core"
parent: null
phase: "P2"
type: "Build"
priority: 3
size: null
surfaces: []
milestone: "Payroll adapter and cash dashboard"
intendedState: "Backlog"
blockedBy: ["PAP-180", "PAP-43"]
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-business-core-11-7c8c2526b3c9"
identifier: null
status: "folded"
into: "PAP-180"
---

# Build recurring tenant invoices and dunning: schedules, automatic reminders, late fees, payment retry for tenant-to-customer billing

> **FOLDED.** Folded into PAP-180 as work package 4 (FIX-5). Do not create; text kept for reference.

**Goal**

Give a clinic, agency or landlord billing its own customers monthly a recurring path in PAP-180's document model: schedules that generate and send invoices, a dunning ladder with reminders and optional late fees, and payment retry for saved cards on the connected account. This is tenant-to-customer billing, distinct from platform subscriptions (PAP-177).

**Scope**

In: tables `fin_recurring_schedule`, `fin_dunning_policy`; procedures `recurring.*`, `dunning.*`; generation job; dunning job; saved payment method capture on the pay page; `/finance/recurring` page and per-party schedule editor; portal "Upcoming" list. Out: usage-based tenant billing, proration, contracts and e-signature.

**Spec**

* `fin_recurring_schedule (party_id, template_document_id, cadence: weekly|monthly|quarterly|yearly, day_of_period, next_run_at, timezone, auto_send, auto_charge, status: active|paused|ended, ends_at?, occurrences?)`; the template is a draft document whose lines are copied with ``period.start`` and ``period.end`` substitutions in descriptions.
* Generation job (PAP-43, hourly) creates the invoice from the template, issues it, sends it when `auto_send`, and charges the saved method when `auto_charge` through a PaymentIntent on the connected account (PAP-181) or platform test mode; idempotent per `(schedule_id, period_start)`.
* `fin_dunning_policy (name, steps jsonb [{ offset_days, action: remind|late_fee|retry|escalate, template_id?, fee: { pct | fixed_minor, cap_minor } }], default)`; per-party override; the daily job walks steps for overdue documents and records each action as `crm_activity` and `document.event`.
* Late fees create a `fee` line on a new document or the original (setting), posting through the PAP-180 rules; retries follow Stripe smart retry windows, capped at four.
* Saved cards: pay page offers "save for future invoices" (Stripe SetupIntent), stored as `stripe_payment_method_id` on `fin_customer`; never stored raw.
* Automations (PAP-174) may call `recurring.pause|resume`; escalations notify finance via PAP-136 core.

**Interface contract**

Provides: `recurring.create|update|pause|resume|preview`, `dunning.policies.*`, `dunning.run(documentId)`, events `recurring.generated`, `dunning.step_applied`, dataset `finance.recurring`, portal upcoming list. Consumes: documents and rules (PAP-180), Stripe client (PAP-177), connected charges (PAP-181, optional), jobs (PAP-43), notifications (PAP-136 core), automations hook (PAP-174, soft), consent for reminders (`gap/growth/consent-centre`, soft).

**Definition of done**

* Vitest, integration and Playwright below green.
* Screenshots at 375, 1024, 1920 in three themes for schedule editor, dunning policy and portal list.
* `docs/finance/recurring-dunning.md`; CHANGELOG; Linear comment with demo link.

**Test plan**

* Unit: next-run computation across month ends and DST, substitution, idempotency key, late fee maths with caps, retry windows.
* Integration (test clock): a monthly schedule generates three invoices over three simulated months; the second is left unpaid and receives remind, late fee and retry steps on the right days; a paused schedule skips a period; saved-card charge succeeds and fails (`4000000000000341`).
* E2E: create a schedule from an invoice, preview the next three dates, open the portal upcoming list; edit the dunning policy.
* Visual: matrix above.

**Demo**

Reviewer turns a seeded invoice into a monthly schedule, previews the next three dates, advances the test clock a month, sees the generated invoice, advances past due and watches the reminder and late fee appear in the activity. Under two minutes.

**Edge cases**

* 31st of the month cadence: last day of shorter months.
* Party opted out of reminders: dunning still applies fees but sends nothing, flagged for manual contact.
* Template edited: applies to future occurrences only.
* Customer pays during the retry window: pending retries cancelled.
* Connected account restricted: charges skipped, invoices still generated with bank instructions.

**Dependencies**

PAP-180 (hard), PAP-43 (hard), PAP-177, PAP-181 (optional), PAP-136 core, PAP-174 (soft). Blocks nothing.

**Agent**

Builder: Ledger (Payments Integrator with Bookkeeper on fees). Reviewer: Sentinel (Edge Case Hunter for calendars and retries, Code Reviewer).

**Size**

M: schedules and a step ladder over the existing document model.
