---
identifier: "PAP-179"
title: "Build a double-entry ledger (accounts, journal entries, periods) in Postgres with immutability guarantees"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Ledger and reports"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-175"]
blocks: ["PAP-180", "PAP-181", "PAP-183", "PAP-184", "PAP-185", "PAP-196", "PAP-206"]
key: "business-core/ledger"
url: "https://linear.app/paperos/issue/PAP-179/build-a-double-entry-ledger-accounts-journal-entries-periods-in"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-179: Build a double-entry ledger (accounts, journal entries, periods) in Postgres with immutability guarantees

**Goal**

Build the double-entry ledger PaperOS owns: journal entries with balanced lines against the chart of accounts, period controls, immutability of posted entries with reversals instead of edits, a tamper-evident hash chain, posting rules that translate business events into entries, and balance materialisation fast enough to drive reports. Every money-moving feature posts here.

**Scope**

In:
- Tables `fin_journal_entry`, `fin_journal_line`, `fin_account_balance`; triggers and constraints; oRPC `ledger.*`.
- Posting rule registry and the first rules for `payment`, `refund`, `fee`, `adjustment`, `transfer` (invoice, payroll and expense rules ship with their issues).
- Manual journal entry UI (`/finance/journal`) and entry detail view; trial balance endpoint.
- Period close/lock workflow.

Out: reports layout (`business-core/finance-reports`), multi-entity consolidation, inventory costing.

**Spec**

- `fin_journal_entry`: `id uuidv7, tenant_id, entry_number bigint (per-tenant sequence), period_id, posted_at timestamptz, effective_date date, memo, status: draft|posted|reversed, source_type, source_id, transaction_id? (fin_transaction), reversal_of_id?, reversed_by_id?, created_by (user or agent), posted_by, prev_hash bytea, hash bytea, dimensions jsonb`. `fin_journal_line`: `id, entry_id, line_no, account_id, party_id?, debit_minor bigint default 0, credit_minor bigint default 0, currency, fx_rate numeric(18,8) (to functional currency), functional_minor bigint, memo, dimensions jsonb`; `CHECK ((debit_minor > 0) <> (credit_minor > 0))`.
- Balance trigger on posting: sum of `functional_minor` debits equals credits per entry or `RAISE EXCEPTION 'UNBALANCED'`; minimum two lines; all accounts active and belonging to the tenant.
- Immutability: `BEFORE UPDATE OR DELETE` trigger on `posted` entries and their lines raises `IMMUTABLE_ENTRY`; the only allowed change is setting `status = reversed` and `reversed_by_id` through the `ledger.reverse` function. Drafts are editable until posted.
- Hash chain: `hash = sha256(prev_hash || canonical_json(entry + lines))` per tenant in `entry_number` order, computed in the posting function under a per-tenant advisory lock; `ledger.verifyChain(tenantId)` recomputes and reports the first mismatch; runs nightly and surfaces in observability (`data-layer/observability`).
- Periods: posting into a `closed` period requires `ledger.reopen` permission; `locked` periods reject all postings; closing runs checks (no drafts, chain verified) and snapshots balances.
- `fin_account_balance (tenant_id, account_id, period_id, opening_minor, debit_minor, credit_minor, closing_minor, currency)` maintained incrementally by the posting function and rebuilt by `ledger.rebuildBalances` in a transaction; trial balance is a sum over it.
- Posting rules: `definePostingRule({ event: 'payment.succeeded', build: (tx: FinTransaction, ctx) => JournalDraft })` where the rule resolves accounts by `subtype` (`cash`, `ar`, `fees`, `revenue`), never by code; `ledger.postEvent(tx)` is idempotent by `(source_type, source_id)`; rules are pure and unit-tested with fixtures. Registry lists rules for docs.
- API: `ledger.createDraft`, `ledger.post`, `ledger.reverse({ id, reason, effectiveDate })`, `ledger.list` (dataset for grid view), `ledger.trialBalance({ periodId })`, `ledger.verifyChain`. All writes require `ledger.post` permission (staff finance role); agents may create drafts but not post unless the character has `ledger:post` scope.
- UI: journal grid via `tables/grid-view` with a line-level expanded panel; manual entry form with running balance indicator that blocks Post until balanced; reverse action with reason; period list with close/lock buttons.

**Definition of done**

- Vitest and pgTAP-style SQL tests: unbalanced rejected, update of posted rejected, reversal produces mirrored lines, chain verification detects a tampered row (done via superuser in test), balances match a brute-force sum after 10k random entries.
- Concurrency test: 50 parallel posts keep `entry_number` gapless and the chain valid.
- Playwright: create draft, post, reverse, close period; screenshots at 375, 1024, 1920 in three themes.
- `docs/finance/ledger.md` with posting rule catalogue and the invariants; ADR on immutability and hash chain.
- CHANGELOG entry; Linear comment with demo link and the chain verification output.

**Edge cases**

- Multi-currency entry: lines in USD and EUR balance in functional currency; FX gain/loss line auto-added when rounding leaves a remainder (account subtype `fx_gain_loss`).
- Rounding when allocating a 3-way split: largest-remainder via `Money.allocate`, never off by a cent.
- Reversal of a reversal: allowed, chain links both.
- Backdated entry into a closed period by an import: rejected; import offers to post on period start date with a memo.
- Account deactivated while a draft references it: post fails with the account named.
- Tenant deletion: ledger rows retained for the legal retention period even after tenant hard delete (moved to an archive schema), documented.

**Dependencies**

- `business-core/finance-data-model` (accounts, periods, transactions, Money), `data-layer/rls-tenancy`, `data-layer/audit-log`, `tables/grid-view` for the journal UI, `identity/rbac-abac`.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Security Auditor for immutability, Code Reviewer) and Forge (Schema Wright) for triggers.

**Size**

L: the invariants must be airtight; budget two sessions and a dedicated adversarial review.
