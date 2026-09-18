---
identifier: "PAP-765"
title: "Recurring invoice schedules, dunning ladder with late fees and saved-card retry on the connected account"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Ledger and reports"
state: "Backlog"
parent: "PAP-180"
children: []
blockedBy: ["PAP-37", "PAP-43", "PAP-177", "PAP-179", "PAP-394", "PAP-395", "PAP-396", "PAP-397", "PAP-565", "PAP-791"]
blocks: ["PAP-182", "PAP-183", "PAP-186", "PAP-788", "PAP-789"]
key: "r4/business-core/recurring-invoices-dunning"
url: "https://linear.app/paperos/issue/PAP-765/recurring-invoice-schedules-dunning-ladder-with-late-fees-and-saved"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:40.106Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-765: Recurring invoice schedules, dunning ladder with late fees and saved-card retry on the connected account

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Give a clinic, agency or landlord that bills its own customers monthly a recurring path in the PAP-180 document model: schedules that generate and send invoices, a dunning ladder of reminders, late fees and card retries, and saved payment methods on the connected account. Formerly PAP-180 work package 4 (folded in 2026-09-17, FIX-5), now the fourth child so it is claimable on its own. Tenant-to-customer billing only; platform subscriptions stay in PAP-177.

**Scope**

In: `packages/finance/src/recurring/` (jobs `recurring.generate` hourly, `dunning.walk` daily), tables `fin_recurring_schedule (party_id, template_document_id, cadence: weekly|monthly|quarterly|yearly, day_of_period, next_run_at, timezone, auto_send, auto_charge, status: active|paused|ended, ends_at?)` and `fin_dunning_policy (name, steps jsonb [{ offset_days, action: remind|late_fee|retry|escalate, template_id?, fee }], is_default)` with per-party override, procedures `recurring.*` and `dunning.*`, `/finance/recurring` page, portal Upcoming list, `stripe_payment_method_id` on `fin_customer` via SetupIntent from the pay page.

Out: usage-based tenant billing (PAP-788), proration, contracts and e-signature, platform dunning (Stripe Billing handles PAP-177).

**Spec**

* Generation creates the next document from the template with `{{period.start}}` and `{{period.end}}` substitutions, issues it via `documents.issue`, sends when `auto_send`, charges the saved method when `auto_charge` through a PaymentIntent on the PAP-181 account (platform test mode otherwise); idempotent per `(schedule_id, period_start)`.
* `next_run_at` in the schedule timezone; the 31st uses the last day of shorter months; DST never skips or doubles a period.
* Dunning walks overdue documents through `steps` by `offset_days`, recording each action as a `document.event` (and `crm_activity` through `@paperos/contract-growth` when enabled); a late fee adds a `fee` line posted through PAP-397 rules; retries follow Stripe smart-retry windows, capped at four; a payment cancels pending steps.
* Reminders pass `canContact(contact, 'email', 'transactional')` from the growth consent centre when present; an opted-out party still accrues fees, receives nothing and is flagged for manual contact.
* All amounts are `Money`; fee caps and percentages use `Money.allocate`, never floats.
* Agents may create and pause schedules, never enable `auto_charge`; every charge is audited.

**Interface contract**

Provides: `recurring.*`, `dunning.policies.*`, `dunning.run(documentId)`, events `recurring.generated`, `dunning.step_applied` (v1), dataset `finance.recurring`, portal route `_portal/upcoming`, `finance.mrr` input for PAP-186. Consumes: documents and state machine (PAP-395), pay page and Checkout (PAP-396), posting rules and email templates (PAP-397), jobs and test clock (PAP-43), connected charges (PAP-181, optional), consent centre (PAP-791, soft), automations `recurring.pause|resume` (PAP-174, soft).

**Definition of done**

* Unit and integration suites green on the compose stack with a Stripe test clock; PAP-359 Semgrep rules pass.
* Playwright: schedule from an invoice, preview three dates, edit the dunning policy, portal Upcoming list; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/recurring-dunning.md`; CHANGELOG; Linear comment on PAP-180 with the test-clock replay.

**Test plan**

* Unit: next-run computation across month ends, leap years and DST; substitution; idempotency key; late-fee maths with caps; retry window selection; `canContact` refusal path.
* E2E: on a Stripe test clock a monthly schedule generates three invoices over three simulated months, the second stays unpaid and receives remind, late fee and retry on the right days; a paused schedule skips a period; saved-card charge succeeds (`4242`) and fails (`4000000000000341`).

**Demo**

Reviewer turns a seeded invoice into a monthly schedule, advances the test clock a month, sees the generated invoice, advances past due and watches the reminder and late fee appear. Under two minutes.

**Edge cases**

* Template edited: applies to future occurrences only; in-flight documents keep their lines.
* Restricted connected account: charges skipped, invoices still generated with bank-transfer instructions and a finance banner.
* Party archived mid-schedule: schedule `ended` with reason, no further sends.
* Concurrent resume by two admins: one generation per period (advisory lock on `schedule_id`).

**Dependencies**

Hard: PAP-395, PAP-396, PAP-397, PAP-43. Soft: PAP-181, PAP-174, PAP-791. Blocks PAP-186 (`finance.mrr`).

**Agent**

Builder: Ledger (Payments Integrator with Bookkeeper on fee postings). Reviewer: Sentinel (Security Auditor for saved-method handling, Edge Case Hunter for calendars).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/business-core/tenant-metered-billing` = PAP-788, `r4/growth/consent-compliance-centre` = PAP-791.
