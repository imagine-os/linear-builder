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
children: ["PAP-392", "PAP-393", "PAP-394"]
blockedBy: ["PAP-175", "PAP-303"]
blocks: ["PAP-180", "PAP-181", "PAP-183", "PAP-184", "PAP-185", "PAP-196", "PAP-206", "PAP-397", "PAP-400", "PAP-408", "PAP-423"]
key: "business-core/ledger"
url: "https://linear.app/paperos/issue/PAP-179/build-a-double-entry-ledger-accounts-journal-entries-periods-in"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:12.458Z"
model: null
effort: null
---

# PAP-179: Build a double-entry ledger (accounts, journal entries, periods) in Postgres with immutability guarantees

**Goal**

Build the double-entry ledger PaperOS owns: balanced journal entries against the chart of accounts, period controls, immutability of posted entries with reversals instead of edits, a tamper-evident hash chain, posting rules that translate business events into entries, and balances fast enough for reports. Every money-moving feature posts here. Umbrella for three children.

**Scope**

Children (M each, same milestone, Backlog):

* PAP-392 Journal tables, balance trigger, immutability trigger, gapless per-tenant numbering, `fin_account_balance` maintenance.
* PAP-393 Hash chain with nightly `verifyChain`, `ledger.reverse`, period close and lock workflow.
* PAP-394 Posting rule registry with the first five rules, `/finance/journal` UI, trial balance and `rebuildBalances`.

Out: report layouts (PAP-183), consolidation, inventory costing.

**Spec**

Decisions binding all children:

* `fin_journal_entry (id uuidv7, tenant_id, entry_number bigint per tenant, period_id, posted_at, effective_date, memo, status: draft|posted|reversed, source_type, source_id, transaction_id?, reversal_of_id?, reversed_by_id?, created_by, posted_by, prev_hash, hash, dimensions)`; `fin_journal_line (entry_id, line_no, account_id, party_id?, debit_minor, credit_minor, currency, fx_rate numeric(18,8), functional_minor, memo, dimensions)` with `CHECK ((debit_minor > 0) <> (credit_minor > 0))`.
* Posting runs in one SQL function under a per-tenant advisory lock: balance check on `functional_minor` (`UNBALANCED`), minimum two lines, active tenant accounts, next `entry_number`, `hash = sha256(prev_hash || canonical_json(entry, lines))`, incremental balance update.
* `BEFORE UPDATE OR DELETE` on posted rows raises `IMMUTABLE_ENTRY`; the only path is `ledger.reverse`.
* Periods: `closed` needs `ledger.reopen`, `locked` rejects everything; close requires no drafts and a verified chain.
* `definePostingRule({ event, build(tx, ctx) => JournalDraft })` resolving accounts by `subtype`, never code; `ledger.postEvent(tx)` idempotent by `(source_type, source_id)`.
* Writes need `ledger.post`; agents may draft, not post, unless the character carries `ledger:post`.

**Interface contract**

Provides: `ledger.createDraft|post|reverse|list|trialBalance|verifyChain|rebuildBalances|postEvent`, `definePostingRule`, `JournalDraft` type, `AccountSubtype` usage rules, dataset `finance.journal`, event `ledger.entry.posted { entryId, sourceType, sourceId }`, error codes `UNBALANCED`, `IMMUTABLE_ENTRY`, `PERIOD_LOCKED`. Consumes: accounts, periods, transactions, `Money` (PAP-175), RLS (PAP-34), audit (PAP-38), grid (PAP-165), `can()` (PAP-227), observability for chain alerts (PAP-40). Consumed by PAP-180, PAP-181, PAP-182, PAP-183, PAP-184, PAP-185, PAP-196, PAP-206.

**Definition of done**

* All three children Done.
* Concurrency: 50 parallel posts keep `entry_number` gapless and the chain valid.
* Playwright: draft, post, reverse, close period; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/ledger.md` with the rule catalogue and invariants; ADR on immutability and hash chain; CHANGELOG; Linear comment with `verifyChain` output.

**Test plan**

Umbrella `ledger.e2e.test.ts` on Postgres: post 10k random balanced entries across two currencies from 50 workers; assert gapless numbering, balances equal a brute-force sum per account and period, `verifyChain` passes; tamper one row as superuser and assert the first mismatch is reported; reverse an entry and assert mirrored lines and both statuses; close a period and assert `PERIOD_LOCKED` on a backdated post; run every registered rule against its fixture transaction and assert the draft balances.

**Demo**

Reviewer opens `/finance/journal`, creates a two-line manual entry (Post disabled until balanced), posts it, tries to edit and sees the immutability error, reverses it with a reason, then runs `pnpm ledger verify demo` printing the chain result. Under two minutes.

**Edge cases**

* Multi-currency entry balances in functional currency; rounding remainder posts to `fx_gain_loss`.
* Three-way split uses `Money.allocate`, never off by a cent.
* Reversal of a reversal allowed, both linked.
* Import backdating into a closed period: rejected with an offer to post on period start.
* Tenant hard delete: ledger rows move to an archive schema for the retention period.

**Dependencies**

PAP-175 (hard), PAP-34, PAP-38, PAP-165 (journal UI), PAP-59 children. Blocks PAP-180, PAP-181, PAP-183, PAP-184, PAP-185, PAP-196, PAP-206.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Security Auditor for immutability, Code Reviewer), Forge (Schema Wright) for triggers.

**Size**

L, split into three M children plus a dedicated adversarial review.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [business-core](<https://linear.app/paperos/document/round-2-pending-issues-business-core-11-7c8c2526b3c9>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
