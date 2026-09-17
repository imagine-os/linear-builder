---
key: "child/PAP-206/1"
title: "QuickBooks Online and Xero connectors: chart of accounts, opening balances on a conversion date, optional journal and invoice history"
project: "migration"
parent: "PAP-206"
phase: "P2"
type: "Build"
priority: 3
size: "M"
surfaces: ["Staff"]
milestone: "Business migrations"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent5/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6"
identifier: "PAP-424"
status: "created"
createdAt: "2026-09-17"
---

# QuickBooks Online and Xero connectors: chart of accounts, opening balances on a conversion date, optional journal and invoice history

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
