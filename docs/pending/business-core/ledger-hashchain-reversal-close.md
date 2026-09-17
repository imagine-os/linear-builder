---
key: "business-core/ledger/hashchain-reversal-close"
title: "Hash chain with nightly verification, ledger.reverse and the period close and lock workflow"
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
status: "pending"
---

# Hash chain with nightly verification, ledger.reverse and the period close and lock workflow

**Goal**

Make the ledger tamper-evident and auditable: a per-tenant hash chain verified nightly, reversals as the only correction path, and period close and lock with checks.

**Scope**

In: `prev_hash` and `hash` computation inside `ledger_post`; `ledger.verifyChain`; `ledger.reverse`; `ledger.closePeriod|lockPeriod|reopenPeriod`; nightly job and observability alert. Out: rules and UI (sibling).

**Spec**

* `hash = sha256(prev_hash || canonical_json(entry, lines))` in `entry_number` order under the tenant lock; `verifyChain(tenantId)` recomputes and returns the first mismatch; nightly PAP-43 job posts a metric and alerts (PAP-40) on failure.
* `ledger.reverse({ id, reason, effectiveDate })` posts mirrored lines, sets `status = reversed`, `reversed_by_id` and `reversal_of_id`; reversal of a reversal allowed.
* Close requires zero drafts and a verified chain, snapshots balances; `closed` needs `ledger.reopen` to post; `locked` rejects all with `PERIOD_LOCKED`.

**Interface contract**

Provides: `ledger.reverse|verifyChain|closePeriod|lockPeriod|reopenPeriod`, error `PERIOD_LOCKED`, metric `ledger.chain.valid`. Consumes: journal child, jobs (PAP-43), observability (PAP-40), `can()` (PAP-227).

**Definition of done**

* Tamper test (superuser edit) detected; reversal mirror test; period state machine tests; ADR on immutability and chain.

**Test plan**

* Integration: chain valid after 10k entries; first mismatch located; backdated post into locked period rejected; close blocked by a draft.

**Demo**

Run `pnpm ledger verify demo`, tamper a row with `psql`, run again and read the mismatch.

**Edge cases**

* Import backdating into a closed period offered a post on period start with memo; reopen audited with reason.

**Dependencies**

Journal child (hard), PAP-43, PAP-40.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.
