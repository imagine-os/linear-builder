---
identifier: "PAP-394"
title: "Posting rule registry with the first five rules, /finance/journal UI, trial balance and rebuildBalances"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Ledger and reports"
state: "Backlog"
parent: "PAP-179"
children: []
blockedBy: ["PAP-393"]
blocks: ["PAP-180", "PAP-181", "PAP-183", "PAP-184", "PAP-185", "PAP-196", "PAP-206"]
key: "business-core/ledger/rules-ui-trialbalance"
url: "https://linear.app/paperos/issue/PAP-394/posting-rule-registry-with-the-first-five-rules-financejournal-ui"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:45.105Z"
---

# PAP-394: Posting rule registry with the first five rules, /finance/journal UI, trial balance and rebuildBalances

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
