---
identifier: "PAP-424"
title: "QuickBooks Online and Xero connectors: chart of accounts, opening balances on a conversion date, optional journal and invoice history"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Business migrations"
state: "Backlog"
parent: "PAP-206"
children: []
blockedBy: ["PAP-179", "PAP-394", "PAP-423", "PAP-769"]
blocks: ["PAP-425", "PAP-828"]
key: "child/PAP-206/1"
url: "https://linear.app/paperos/issue/PAP-424/quickbooks-online-and-xero-connectors-chart-of-accounts-opening"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:24.416Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 3
dueDate: null
cycle: null
---

# PAP-424: QuickBooks Online and Xero connectors: chart of accounts, opening balances on a conversion date, optional journal and invoice history

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Import a chart of accounts and opening balances from QuickBooks Online or Xero into the double-entry ledger so reports are correct from the conversion date, with optional history after it.

**Scope**

In: `connectors/quickbooks/` (OAuth 2 via `intuit-oauth`, `Account`, `JournalEntry`, `Customer`, `Vendor`, `Invoice`, `Bill`, `Payment`, CDC incremental) and `connectors/xero/` (`xero-node` 6.x, `Accounts`, `Contacts`, `Invoices`, `ManualJournals`, `BankTransactions`, `If-Modified-Since`); `mapping/coa.ts` account type and subtype (or Xero class and type) -> ledger `kind`, `code`, `name`, `parent`, `currency`, `is_active`; opening journal on the conversion date; history import of journals and invoices after it.

Out: Stripe (child 1), wizard (child 3).

**Spec**

* Missing or disabled codes: mapped by name, flagged, codes generated in a reserved range.
* Tracking categories and classes become ledger dimensions when PAP-179 supports them, else tags with a note.
* Conversion date interpreted in tenant timezone.

**Interface contract**

Provides: `registerConnector('quickbooks', ...)`, `registerConnector('xero', ...)`, `mapChartOfAccounts(accounts): LedgerAccountSpec[]`, `openingJournal(balances, date)`. Consumes: PAP-199 child 1, PAP-179 accounts and journals, PAP-175 customers and vendors, PAP-201. Chart output also consumed by PAP-207 packs for code conflict handling.

**Definition of done**

* QuickBooks sandbox company and Xero demo company both import; balance sheet from PAP-183 on the conversion date matches the source report within rounding (tables attached).
* `docs/migration/finance-imports.md` section on conversion dates and history.

**Test plan**

* Vitest: account mapping for every QuickBooks type and subtype and every Xero class; opening journal balances; CDC and `If-Modified-Since` cursors.
* Integration: recorded API responses in CI; live sandbox and demo runs from the test-accounts issue.
* Conformance suite passes for both connectors.

**Demo**

Reviewer connects the QuickBooks sandbox, picks a conversion date, and sees the chart of accounts mapped with kinds and an opening journal whose debits equal credits. Under two minutes.

**Edge cases**

* Historical journal referencing an unimported account: dry run stops with the dependency listed.
* Account exists in the tenant with the same code: offered as a match.
* Xero demo company resets monthly: fixtures pinned in the repo.

**Dependencies**

PAP-199 child 1 (hard), PAP-179 (hard), PAP-175, PAP-201, test-accounts issue. Blocks child 3.

**Agent**

Built by Scout (Import Mapper) with Ledger (Bookkeeper). Reviewed by Sentinel (Security Auditor) and Ledger.

**Size**

M
