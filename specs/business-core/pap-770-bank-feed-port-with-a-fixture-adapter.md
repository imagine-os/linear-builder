---
identifier: "PAP-770"
title: "Bank feed port with a fixture adapter and statement import (CSV, OFX, CAMT.053) into bank accounts and bank transactions"
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
blockedBy: ["PAP-37", "PAP-175", "PAP-347", "PAP-348", "PAP-392"]
blocks: ["PAP-771"]
key: "r4/business-core/bank-feed-port-and-statement-import"
url: "https://linear.app/paperos/issue/PAP-770/bank-feed-port-with-a-fixture-adapter-and-statement-import-csv-ofx"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:52.807Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-770: Bank feed port with a fixture adapter and statement import (CSV, OFX, CAMT.053) into bank accounts and bank transactions

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Books are only trustworthy when the `cash` account agrees with the bank. This issue brings bank data in: a `BankFeedPort` with a deterministic fixture adapter first (Plaid, GoCardless Bank Account Data and Stripe Financial Connections as later adapters behind the same port) and statement file import so every tenant can reconcile even without a feed provider.

**Scope**

In: `packages/finance/src/bank/` with tables `fin_bank_account (party-less, ledger_account_id with subtype cash, institution, mask_last4, currency, feed_connection_id?, feed_status)`, `fin_bank_transaction (bank_account_id, external_id unique per account, posted_at, amount_minor, currency, description, counterparty, category_hint, raw jsonb, matched_entry_id?, status: unmatched|matched|excluded)`; `BankFeedPort { connect(), listAccounts(), sync(cursor), disconnect() }` with `fixture` adapter (committed 90-day statement) and the adapter registry entry for `plaid` and `gocardless` (dryRun stubs only, credentials are an NJ item); parsers for CSV (bank presets), OFX/QFX and ISO 20022 CAMT.053 via the PAP-199 import framework as a `bank-statement` connector.

Out: matching and reconciliation UI (sibling), payments initiation, card feeds beyond Stripe balance (PAP-181).

**Spec**

* Statement import uses `SourceConnector` so dry run, dedupe by `external_id` or `(posted_at, amount, description hash)` and rollback come free (PAP-347, PAP-348, PAP-201).
* Sync is incremental by provider cursor; duplicates across feed and file import collapse on the same hash; amounts are `Money`.
* Feed credentials are stored through PAP-353 `encrypted()`; account numbers never stored beyond `mask_last4`.
* Events `bank.transaction.imported` (`defineTopic`, v1); dataset `finance.bankTransactions` for the grid.

**Interface contract**

Provides: `BankFeedPort`, `bankFeeds[id]` registry, tables, connector `bank-statement`, dataset, `bank.accounts.*`, `bank.sync`. Consumes: cash accounts (PAP-175), ledger (PAP-392), files (PAP-37), import framework (PAP-347, PAP-348, PAP-201), encryption (PAP-353), jobs (PAP-43).

**Definition of done**

* Fixture adapter and three statement formats import 90 days with zero duplicates on rerun; Vitest and integration green offline.
* Bank accounts page screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/bank-feeds.md` with the provider activation checklist (NJ item template); CHANGELOG.

**Test plan**

* Unit: each parser on five real-shaped fixtures (dates, negative formats, multi-currency), hash dedupe, cursor resume, mask.
* E2E: upload an OFX file, see transactions listed as unmatched, rerun and see zero new rows.

**Demo**

Reviewer connects the fixture bank, syncs, uploads a CSV for the same period and sees the duplicates collapsed. Under two minutes.

**Edge cases**

* Pending transactions that later post with a new id: matched by amount and date within two days, old row superseded.
* Statement in a currency different from the account: rejected with the currency named.
* Feed revoked by the bank: `feed_status: reauth_required`, banner, file import still works.

**Dependencies**

Hard: PAP-175, PAP-392, PAP-37, PAP-347, PAP-348. Soft: PAP-201, PAP-353. Blocks PAP-771.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Security Auditor for credentials, Edge Case Hunter for parsers).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/business-core/bank-reconciliation-matching` = PAP-771.
