---
identifier: "PAP-395"
title: "Document model, lines, sequences, server-side totals, state machine, quote conversion, void and credit notes"
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
blockedBy: ["PAP-175"]
blocks: ["PAP-396"]
key: "business-core/invoicing/model-statemachine"
url: "https://linear.app/paperos/issue/PAP-395/document-model-lines-sequences-server-side-totals-state-machine-quote"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:49.175Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-395: Document model, lines, sequences, server-side totals, state machine, quote conversion, void and credit notes

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Model quotes, invoices, receipts, credit notes and bills with exact totals, gapless numbering and a strict state machine, before any rendering or payment is attached.

**Scope**

In: `fin_document`, `fin_document_line`, `fin_tax_rate`, sequences; `documents.create|update|issue|accept|void|creditNote|list|get`; `computeTotals`. Out: PDFs, pay page, postings, portal, emails (siblings).

**Spec**

* Schema per the parent; per-kind sequences formatted from `fin_settings.invoice_number_format`, allocated inside `issue` under a tenant lock.
* `computeTotals(lines, currency)` with `Money`: per-line rounding then sum, discounts, multi-rate tax (manual rates or PAP-182 evidence), quantity precision 4.
* Transitions are the only writes to `status`; `issue` freezes lines and number; `accept` from a quote stores signature name and time and creates an invoice draft; `void` only without payments; credit notes apply to paid balances; expiry job for quotes.

**Interface contract**

Provides: types `FinDocument`, `DocumentLine`, procedures above, `computeTotals`, `documentStateMachine`, dataset `finance.documents`. Consumes: `Money`, parties, settings (PAP-175), tax evidence (PAP-182, optional), jobs (PAP-43).

**Definition of done**

* Totals tests to the cent; state machine table tests; sequence gapless under 20 concurrent issues; dataset renders in a grid.

**Test plan**

* Unit: rounding policy, discounts, multi-rate tax, illegal transitions `CONFLICT`.
* Integration: concurrent issue; quote to invoice conversion; credit note application.

**Demo**

Run `pnpm tsx scripts/invoice-demo.ts` creating a quote, accepting it and printing the invoice totals and number.

**Edge cases**

* Number format change mid-year continues from the max; credit note larger than balance rejected.

**Dependencies**

PAP-175 (hard), PAP-43, PAP-182 (optional). Blocks siblings.

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
