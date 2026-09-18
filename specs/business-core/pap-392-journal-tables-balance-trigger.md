---
identifier: "PAP-392"
title: "Journal tables, balance trigger, immutability trigger, gapless numbering and account balances"
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
blockedBy: ["PAP-175"]
blocks: ["PAP-393", "PAP-767", "PAP-769", "PAP-770"]
key: "business-core/ledger/journal-constraints"
url: "https://linear.app/paperos/issue/PAP-392/journal-tables-balance-trigger-immutability-trigger-gapless-numbering"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:16.110Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-392: Journal tables, balance trigger, immutability trigger, gapless numbering and account balances

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Lay the ledger's foundation in Postgres: journal entry and line tables whose constraints make an unbalanced or edited posted entry impossible, with gapless per-tenant numbering and incrementally maintained balances.

**Scope**

In: `fin_journal_entry`, `fin_journal_line`, `fin_account_balance`; posting SQL function `ledger_post(entry_id)`; triggers `UNBALANCED`, `IMMUTABLE_ENTRY`; `ledger.createDraft` and `ledger.post` procedures. Out: hash chain, reversals, periods workflow, rules and UI (siblings).

**Spec**

* Tables per the parent; `CHECK ((debit_minor > 0) <> (credit_minor > 0))`; minimum two lines; accounts active and tenant-owned.
* `ledger_post` runs under `pg_advisory_xact_lock(hashtext(tenant_id))`: balance check on `functional_minor`, next `entry_number` from a per-tenant counter row, status to `posted`, balance rows upserted per `(account_id, period_id)`.
* `BEFORE UPDATE OR DELETE` trigger on posted entries and their lines raises `IMMUTABLE_ENTRY` except for the columns the reversal sibling whitelists.
* Drafts editable; `ledger.createDraft` validates with Zod and `Money`.

**Interface contract**

Provides: tables, `ledger_post`, `ledger.createDraft|post`, `JournalDraft` type, error codes `UNBALANCED`, `IMMUTABLE_ENTRY`. Consumes: accounts, periods, `Money` (PAP-175), RLS (PAP-34), audit (PAP-38).

**Definition of done**

* SQL and Vitest tests: unbalanced rejected, posted update rejected, 50 parallel posts gapless, balances equal brute-force sums after 10k entries.

**Test plan**

* Unit: draft validation; `Money` functional conversion.
* Integration (Postgres): the constraint tests above; RLS harness on the three tables.

**Demo**

Run `pnpm tsx scripts/ledger-post-demo.ts` posting a balanced and an unbalanced draft and printing the results.

**Edge cases**

* Multi-currency lines balance in functional currency with an `fx_gain_loss` remainder line; deactivated account named in the failure.

**Dependencies**

PAP-175 (hard), PAP-34, PAP-38. Blocks siblings.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Forge (Schema Wright), Sentinel (Security Auditor).

**Size**

M: invariants must be airtight.
