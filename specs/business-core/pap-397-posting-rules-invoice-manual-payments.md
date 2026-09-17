---
identifier: "PAP-397"
title: "Posting rules invoice.*, manual payments, reminders job, customer portal invoice list and email templates"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "Ledger and reports"
state: "Backlog"
parent: "PAP-180"
children: []
blockedBy: ["PAP-179", "PAP-396"]
blocks: ["PAP-182", "PAP-183"]
key: "business-core/invoicing/postings-portal-emails"
url: "https://linear.app/paperos/issue/PAP-397/posting-rules-invoice-manual-payments-reminders-job-customer-portal"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:46.284Z"
---

# PAP-397: Posting rules invoice.*, manual payments, reminders job, customer portal invoice list and email templates

**Goal**

Close the accounting and communication loop: every document event posts to the ledger, customers see and pay invoices in the portal, and reminders and receipts go out automatically.

**Scope**

In: rules `invoice.issued|paid|voided`, `credit_note.issued`; `documents.recordPayment`; overdue and reminder job (due+3, due+14); portal "Invoices" page; email templates send, reminder, receipt via PAP-136 core and the PAP-235 theme. Out: recurring schedules and dunning (PAP-180 (work package 4)).

**Spec**

* `invoice.issued` debits `ar`, credits revenue per line account and `sales_tax_payable` per jurisdiction; `invoice.paid` debits `cash` or `stripe_balance`, credits `ar`; FX gain or loss when currencies differ; void posts the reversal.
* Reminders skip when disabled per document or party; `overdue` set daily.
* Portal list for parties with `portal_enabled`, access by `user_id` link; `document.read` own.

**Interface contract**

Provides: posting rules, `documents.recordPayment|send`, portal route `_portal/invoices`, notification kinds `document.sent|reminder|receipt`. Consumes: both siblings, posting (PAP-179), portal shell (PAP-64), notifications (PAP-136 core), theme (PAP-235), jobs (PAP-43).

**Definition of done**

* Rule fixtures balance; reminder job tests with a fixed clock; portal Playwright; emails snapshot-tested; screenshots at 375, 768, 1024, 1440, 1920.

**Test plan**

* Unit: rules, FX handling, reminder eligibility.
* E2E: issue, pay, see journal entries in the activity tab; portal customer pays and sees the receipt.

**Demo**

Issue an invoice, log in as the customer in the portal, pay it, read the receipt email in the outbox viewer.

**Edge cases**

* Manual partial payment sets `partial`; reminder to a party with `do_not_contact` skipped and logged.

**Dependencies**

Both siblings (hard), PAP-179, PAP-64, PAP-136 core, PAP-235, PAP-43.

**Agent**

Builder: Ledger (Bookkeeper and Payments Integrator). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
