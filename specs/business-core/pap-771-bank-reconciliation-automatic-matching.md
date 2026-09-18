---
identifier: "PAP-771"
title: "Bank reconciliation: automatic matching rules, suggested matches, split and create-from-bank actions, reconciliation statement and month-end lock check"
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
blockedBy: ["PAP-394", "PAP-397", "PAP-770"]
blocks: []
key: "r4/business-core/bank-reconciliation-matching"
url: "https://linear.app/paperos/issue/PAP-771/bank-reconciliation-automatic-matching-rules-suggested-matches-split"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:41.081Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-771: Bank reconciliation: automatic matching rules, suggested matches, split and create-from-bank actions, reconciliation statement and month-end lock check

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Turn bank transactions into a reconciled cash account: match them to existing journal lines and documents automatically, let staff confirm, split or create entries from a bank line, and produce the reconciliation statement a period close needs.

**Scope**

In: `bank/match.ts` rules (exact amount and date within 3 days, Stripe payout ids, invoice number in description, vendor name via `pg_trgm`, learned vendor to account), `bank.suggest`, `bank.match`, `bank.unmatch`, `bank.split`, `bank.createEntry` (posts through PAP-394 rules `bank.payment|receipt|transfer|fee`), rules editor for tenant patterns, `/finance/bank/reconcile` two-pane page, reconciliation statement `finance.bankReconciliation` (opening, cleared, uncleared, ending) with PDF export, PAP-393 close hook refusing close when unreconciled items exceed a threshold unless overridden with reason.

Out: feed adapters and parsers (sibling), receipt OCR (PAP-185).

**Spec**

* Matching never posts on its own; suggestions carry `confidence` and `reason`; one-click confirm for confidence above 0.9, review list otherwise.
* A bank line may match many ledger lines and vice versa (many-to-many through `fin_bank_match`); sums must agree to the cent or a `fees|fx` remainder line is proposed.
* Transfers between two tenant bank accounts are detected by mirror amounts and post a single `transfer` entry.
* Excluding a line records a reason; excluded lines show on the statement.

**Interface contract**

Provides: matching procedures, `fin_bank_match`, rules editor, reconciliation dataset and statement, close hook `ledger.beforeClose`. Consumes: bank transactions (sibling), posting rules (PAP-394), document payments (PAP-397), period close (PAP-393), grid (PAP-165), PDF (PAP-235).

**Definition of done**

* Fixture month reconciles to zero difference with 85 percent auto-matched; unit and Playwright green; statement PDF snapshot.
* Screenshots at 375, 1024, 1920 in three themes; keyboard-only match flow.
* `docs/finance/reconciliation.md`; CHANGELOG.

**Test plan**

* Unit: each rule on fixtures, many-to-many sums, remainder proposal, transfer detection, threshold logic.
* E2E: confirm a suggestion, split one bank line across two invoices, create an entry from an unknown fee, export the statement, attempt a period close and read the unreconciled warning.

**Demo**

Reviewer opens Reconcile, confirms the green suggestions, splits one line and exports the statement showing a zero difference. Under two minutes.

**Edge cases**

* Same amount twice on one day: both suggestions shown at lower confidence, never auto-confirmed.
* Match to a line in a locked period: allowed (bank side only) with a note; ledger untouched.
* Unmatch after close: opens an adjustment in the current period, never edits history.

**Dependencies**

Hard: PAP-770, PAP-394, PAP-397. Soft: PAP-393, PAP-165, PAP-235.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Edge Case Hunter, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/business-core/bank-feed-port-and-statement-import` = PAP-770.
