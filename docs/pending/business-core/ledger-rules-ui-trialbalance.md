---
key: "business-core/ledger/rules-ui-trialbalance"
title: "Posting rule registry with the first five rules, /finance/journal UI, trial balance and rebuildBalances"
project: "business-core"
parent: "PAP-179"
phase: "P2"
type: "Build"
priority: 1
size: "M"
surfaces: []
milestone: "Ledger and reports"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-business-core-11-7c8c2526b3c9"
identifier: "PAP-394"
status: "created"
createdAt: "2026-09-17"
---

# Posting rule registry with the first five rules, /finance/journal UI, trial balance and rebuildBalances

**Goal**

Connect business events to the ledger through pure, testable posting rules and give finance staff a journal screen and trial balance.

**Scope**

In: `definePostingRule`, rules `payment.succeeded`, `refund.created`, `fee.charged`, `adjustment`, `transfer`; `ledger.postEvent`; `ledger.list|trialBalance|rebuildBalances`; `/finance/journal` grid with line panel, manual entry form, period list. Out: invoice, payroll and expense rules (their issues).

**Spec**

* Rules resolve accounts by `subtype`, never code; `postEvent(tx)` idempotent by `(source_type, source_id)`; registry exported for docs.
* Manual entry form with running balance; Post disabled until balanced; reverse action with reason; period list with close and lock.
* `rebuildBalances(tenantId)` recomputes `fin_account_balance` in one transaction; trial balance sums it per period.

**Interface contract**

Provides: `definePostingRule`, `ledger.postEvent|list|trialBalance|rebuildBalances`, dataset `finance.journal`, event `ledger.entry.posted`, route `/finance/journal`. Consumes: both siblings, grid (PAP-165), `fin_transaction` (PAP-175), `can()` (PAP-227).

**Definition of done**

* Rule fixtures balance; idempotency test; Playwright draft, post, reverse, close; screenshots at 375, 1024, 1920 in three themes; `docs/finance/ledger.md` rule catalogue.

**Test plan**

* Unit: each rule against fixture transactions; duplicate `postEvent` no-op.
* E2E: the manual entry flow above; trial balance matches brute force.

**Demo**

Create a two-line entry in `/finance/journal`, post it, reverse it, open the trial balance.

**Edge cases**

* Rule for an unknown subtype fails loudly at registration; agents draft but cannot post.

**Dependencies**

Both siblings (hard), PAP-165, PAP-227.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
