---
identifier: "PAP-180"
title: "Implement invoices, quotes and receipts with PDF generation and Stripe payment links"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Ledger and reports"
state: "Backlog"
parent: null
children: ["PAP-765", "PAP-397", "PAP-396", "PAP-395"]
blockedBy: ["PAP-37", "PAP-177", "PAP-179", "PAP-394"]
blocks: ["PAP-182", "PAP-183"]
key: "business-core/invoicing"
url: "https://linear.app/paperos/issue/PAP-180/implement-invoices-quotes-and-receipts-with-pdf-generation-and-stripe"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:51:46.586Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-29"
cycle: null
---

# PAP-180: Implement invoices, quotes and receipts with PDF generation and Stripe payment links

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Let any tenant bill anyone: quotes that convert to invoices, invoices with lines, taxes and terms, receipts on payment, branded PDFs, a public pay page backed by Stripe, credit notes, and automatic ledger postings for receivables, revenue and cash. Umbrella for three children.

**Scope**

Children (M each, same milestone, Backlog):

* PAP-395 `fin_document` and lines, per-kind sequences, server-side totals, state machine, quote acceptance and conversion, void and credit notes.
* PAP-396 PDF rendering with the PAP-235 theme, `/pay/:token` and `/doc/:token`, Stripe Checkout on platform or connected account, receipts.
* PAP-397 Posting rules `invoice.*`, `credit_note.issued`, manual payments, reminders job, portal invoice list and email templates.

Work package 4 (below, M, built after the children on its own branch): recurring invoices and dunning, formerly the pending issue `gap/business-core/recurring-dunning`, folded into this issue on 2026-09-17 because Linear cannot create it (issue cap).

Out: inventory, multi-language templates beyond locale formatting, usage-based tenant billing, proration, contracts and e-signature.

**Spec**

Decisions binding all children:

* `fin_document (kind: quote|invoice|receipt|credit_note|bill, number formatted by fin_settings.invoice_number_format, party_id, status per kind, issue_date, due_date, currency, subtotal|discount|tax|total|paid|balance _minor, terms, notes, source_document_id, stripe_payment_intent_id?, stripe_checkout_session_id?, public_token, pdf_file_id, sent_at, viewed_at, metadata)`; `fin_document_line (line_no, description, quantity numeric(12,4), unit_price_minor, discount_pct, tax_rate_id?, tax_minor, amount_minor, revenue_account_id?, dimensions)`.
* Invoice statuses `draft|issued|sent|viewed|partial|paid|overdue|void`; transitions are the only writes to `status`.
* `documents.issue` freezes lines and number, posts `invoice.issued` (debit `ar`, credit revenue per line, credit `sales_tax_payable`), creates the Stripe session on the connected account when PAP-181 is enabled else on the platform account in test mode.
* Payment webhook posts `invoice.paid` (debit `cash` or `stripe_balance`, credit `ar`), issues a receipt, emails it; idempotent by `stripe_event.id`.
* PDFs via `@react-pdf/renderer` 4.x using `brandingToInlineCss` and the template kit from PAP-235, content-addressed in PAP-37.
* Reminders at due+3 and due+14 unless disabled; `overdue` set daily.

**Work package 4: recurring tenant invoices and dunning (was the pending issue** `gap/business-core/recurring-dunning`**, folded in on 2026-09-17, round-2 FIX-5)**

Give a clinic, agency or landlord billing its own customers monthly a recurring path in this document model: schedules that generate and send invoices, a dunning ladder with reminders and optional late fees, and payment retry for saved cards on the connected account. Tenant-to-customer billing, distinct from platform subscriptions (PAP-177). Build it after the three children on branch `PAP-180/wp4-recurring-dunning` (M) and report it in a comment on this issue.

* Tables `fin_recurring_schedule (party_id, template_document_id, cadence: weekly|monthly|quarterly|yearly, day_of_period, next_run_at, timezone, auto_send, auto_charge, status: active|paused|ended, ends_at?, occurrences?)` and `fin_dunning_policy (name, steps jsonb [{ offset_days, action: remind|late_fee|retry|escalate, template_id?, fee: { pct | fixed_minor, cap_minor } }], default)` with per-party override; the template is a draft document whose lines are copied with `{{period.start}}` and `{{period.end}}` substitutions.
* Generation job (PAP-43, hourly) creates the invoice from the template, issues it, sends it when `auto_send`, charges the saved method when `auto_charge` through a PaymentIntent on the connected account (PAP-181) or platform test mode; idempotent per `(schedule_id, period_start)`. The daily dunning job walks the steps for overdue documents and records each action as `crm_activity` and `document.event`; late fees create a `fee` line on a new document or the original (setting) posting through the rules above; retries follow Stripe smart-retry windows, capped at four; the pay page offers "save for future invoices" (Stripe SetupIntent) stored as `stripe_payment_method_id` on `fin_customer`, never raw.
* Interface: `recurring.create|update|pause|resume|preview`, `dunning.policies.*`, `dunning.run(documentId)`, events `recurring.generated`, `dunning.step_applied`, dataset `finance.recurring`, `/finance/recurring` page and per-party schedule editor, portal "Upcoming" list. Automations (PAP-174) may call `recurring.pause|resume`; escalations notify finance via PAP-136 core; reminder consent through PAP-187 work package 0 (soft: a party opted out of reminders still receives fees, sends nothing, and is flagged for manual contact).
* Edge cases: 31st-of-month cadence uses the last day of shorter months; template edits apply to future occurrences only; a payment during the retry window cancels pending retries; a restricted connected account skips charges but still generates invoices with bank instructions.
* Done when: unit tests for next-run computation across month ends and DST, substitution, idempotency key, late-fee maths with caps and retry windows; integration on a Stripe test clock: a monthly schedule generates three invoices over three simulated months, the second is left unpaid and receives remind, late fee and retry on the right days, a paused schedule skips a period, a saved-card charge succeeds and fails (`4000000000000341`); Playwright: create a schedule from an invoice, preview the next three dates, open the portal upcoming list, edit the dunning policy; screenshots at 375, 1024, 1920 in three themes for the schedule editor, dunning policy and portal list; `docs/finance/recurring-dunning.md`; CHANGELOG; Linear comment with demo link. Demo: turn a seeded invoice into a monthly schedule, preview three dates, advance the test clock a month, see the generated invoice, advance past due and watch the reminder and late fee appear in the activity; under two minutes. Out: usage-based tenant billing, proration, contracts and e-signature.

**Interface contract**

Provides: `documents.create|update|issue|send|accept|void|recordPayment|creditNote|list|get`, `renderDocumentPdf(id)`, routes `/pay/:token`, `/doc/:token`, events `document.issued|paid|voided`, dataset `finance.documents` (AR aging for PAP-183), `bill` kind for PAP-185. Consumes: Stripe client and `stripe_event` (PAP-177), posting (PAP-179), connected charges (PAP-181, optional), tax calculation (PAP-182, optional), files (PAP-37), email templates and theme (PAP-235, PAP-136 core), portal shell (PAP-64), `Money` (PAP-175). Consumed by PAP-183, PAP-185, PAP-196 statements and work package 4 (which adds `recurring.*`, `dunning.*`, `finance.recurring` on top).

* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (`Money` from PAP-175: `amountMinor` bigint at runtime, string on the wire, never floats in totals or tax lines); §3 (the catalogue names these topics `invoice.issued|paid|voided` and `payment.succeeded|failed|refunded`; register the `document.*` events above under those topic names with `defineTopic`, payloads carry ids and changed fields only, `subject` is the `EntityRef` of the invoice); §2 row "File" (PDFs go through PAP-37's `file` table and per-request download URLs); §6 rows "Finance model and ledger posting" and "Design tokens and branding" (PDF theme from PAP-235).

**Definition of done**

* All three children Done and work package 4 merged.
* PDF snapshot tests (rasterised with `pdf-to-img`) for invoice, quote, receipt at two brands with visual diff in CI.
* Playwright: editor, public pay page at 375 and 1024, portal list; screenshots at 375, 768, 1024, 1440, 1920 in three themes.
* `docs/finance/invoicing.md`; CHANGELOG; Linear comment with a live test-mode pay link and replay.

**Test plan**

Umbrella `invoicing.e2e.test.ts`: create a quote with three lines including 0.3333 quantity and two tax rates, accept it from the public page, issue the invoice and assert the ledger lines to the cent, pay through Stripe test mode via `stripe trigger`, assert `paid`, receipt document, `invoice.paid` posting and the emailed receipt in the outbox; void a fresh invoice and assert the reversal; issue a credit note against a paid invoice; run 20 concurrent issues and assert a gapless sequence.

**Demo**

Reviewer creates an invoice in the editor, clicks Issue, opens the pay link in a private window, pays with `4242`, and returns to see the invoice paid with a receipt PDF and the journal entries listed in the activity tab. Under two minutes.

**Edge cases**

* Partial bank-transfer payment recorded manually sets `partial`.
* Currency differs from functional: FX at issue and payment, gain or loss posted.
* Voided invoice pay link shows "Voided", no Pay button.
* Number format changed mid-year: sequence continues from the max.
* Duplicate webhook after receipt: idempotent.

**Dependencies**

PAP-179 (hard), PAP-177 (hard), PAP-37 (hard, PDFs), PAP-235 (soft, theme: render PDFs with the invoice's own template first and switch to `packages/ui-print` when it lands; the `blocks` relation from PAP-235 was removed on 2026-09-17, round-2 FIX-1), PAP-181 and PAP-182 (optional), PAP-136 core, PAP-64. Work package 4 additionally needs PAP-43 (hard, jobs and test clock), PAP-177 Stripe client, PAP-181 (optional) and PAP-187 work package 0 (soft, reminder consent); PAP-174 automations call `recurring.pause|resume` (soft, PAP-174 does not depend on it). Blocks PAP-182, PAP-183.

**Agent**

Builder: Ledger (Payments Integrator with Bookkeeper on rules). Reviewer: Sentinel (Security Auditor for the public route, Visual Inspector for PDFs).

**Size**

L, split into three M children plus work package 4 (M) on branch `PAP-180/wp4-recurring-dunning`.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [business-core](<https://linear.app/paperos/document/round-2-pending-issues-business-core-11-7c8c2526b3c9>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
