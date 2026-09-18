---
identifier: "PAP-779"
title: "Disputes and fraud controls: Stripe Radar rules per tenant, dispute inbox with evidence assembly from documents and activity, deadlines, outcome postings"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Payroll adapter and cash dashboard"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-181", "PAP-397"]
blocks: []
key: "r4/business-core/disputes-radar-evidence"
url: "https://linear.app/paperos/issue/PAP-779/disputes-and-fraud-controls-stripe-radar-rules-per-tenant-dispute"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:12.613Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-779: Disputes and fraud controls: Stripe Radar rules per tenant, dispute inbox with evidence assembly from documents and activity, deadlines, outcome postings

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-181 posts `charge.dispute.*` to a reserve and stops there. Losing a dispute by missing the deadline is the most expensive thing a small business can do with cards; this adds the inbox, the evidence pack and the outcome accounting.

**Scope**

In: `fin_dispute (stripe_dispute_id, charge_id, document_id?, amount_minor, reason, status, evidence_due_by, submitted_at, outcome)` from connected webhooks; `/finance/disputes` inbox with countdown; evidence assembler pulling the invoice PDF, pay-page view log, receipt email, portal login history and support conversation (through `@paperos/contract-growth`, optional) into Stripe's evidence fields via `disputes.update`; submit action with confirmation; Radar rule presets per tenant (block on high risk score, require 3DS above an amount) written to the connected account's Radar rules where the API allows, else documented; postings on `won` (reserve back to `stripe_balance`) and `lost` (reserve to `disputes_expense`, fee to `fees`).

Out: chargeback insurance, manual card-not-present reviews, non-Stripe rails.

**Spec**

* Deadline alerts via PAP-136 at 7, 3 and 1 days before `evidence_due_by`; the inbox sorts by deadline.
* Evidence files are uploaded through Stripe `files.create` with `purpose: dispute_evidence`, never stored twice; the pack is content-addressed in PAP-37 for the audit trail.
* Submission requires `payments.manage`; agents may assemble, never submit.

**Interface contract**

Provides: `fin_dispute`, `disputes.list|assemble|submit`, posting rules `dispute.won|lost`, inbox route, notification kind `dispute.deadline`. Consumes: Connect webhooks and postings (PAP-181), documents and receipts (PAP-397, PAP-396), notifications (PAP-136), files (PAP-37), support conversations (`@paperos/contract-growth`, optional).

**Definition of done**

* Fixture disputes (`stripe trigger charge.dispute.created`) appear in the inbox with deadlines; evidence assembled and submitted in test mode, recorded; outcome postings balance.
* Screenshots at 375, 1024, 1920 in three themes; `docs/finance/disputes.md`; CHANGELOG.

**Test plan**

* Unit: deadline alert schedule, evidence field mapping, outcome postings, permission gate.
* E2E: trigger a dispute, open the inbox, assemble evidence, submit, trigger `charge.dispute.closed` won and see the reserve released.

**Demo**

Reviewer triggers a test dispute, watches it appear with a 7-day countdown, assembles the pack and submits it. Under two minutes.

**Edge cases**

* Dispute on a charge with no PaperOS document (imported history): evidence limited to Stripe data, flagged.
* Deadline passed: inbox shows 'expired', posting on `lost` when the webhook arrives.
* Partial dispute amount: reserve moves the disputed amount only.

**Dependencies**

Hard: PAP-181, PAP-397. Soft: PAP-136, PAP-37, PAP-396, growth support contract.

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor, Code Reviewer).

**Size**

S: half a session.
