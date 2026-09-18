---
identifier: "PAP-767"
title: "Finance demo seed: twelve months of balanced journals, invoices, bills, subscriptions and payroll runs for the demo tenant and the conformance fixtures"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Docs"
priority: 2
surfaces: ["Developer"]
milestone: "Ledger and reports"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-175", "PAP-392", "PAP-395"]
blocks: ["PAP-183", "PAP-186", "PAP-487"]
key: "r4/business-core/finance-demo-seed"
url: "https://linear.app/paperos/issue/PAP-767/finance-demo-seed-twelve-months-of-balanced-journals-invoices-bills"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:16.129Z"
model: "claude-haiku-4-5"
effort: "low"
estimate: 2
dueDate: "2026-09-29"
cycle: null
---

# PAP-767: Finance demo seed: twelve months of balanced journals, invoices, bills, subscriptions and payroll runs for the demo tenant and the conformance fixtures

**Model / Effort:** Haiku 4.5 (`claude-haiku-4-5-20251001`) / low — Docs S

**Goal**

PAP-183 wants a textbook fixture, PAP-186 wants a seeded tenant, PAP-487 wants twelve golden transactions and PAP-208 seeds demo data, each separately. One seed profile produces all of them from a single YAML source so numbers agree across reports, dashboard and conformance.

**Scope**

In: `packages/finance/seed/demo-finance.yaml` (parties, chart `saas`, 12 months of dated business events), generator `pnpm db:seed --profile demo-finance` that replays events through `ledger.postEvent` and `documents.*` (never raw inserts), `test/fixtures/finance/textbook.json` with the expected P&L, balance sheet, cash flow, AR and AP aging per month on accrual and cash bases, and the twelve golden transactions plus expected journal lines exported for PAP-487.

Out: pack sample data (PAP-427), payroll provider sandbox data (mock adapter events only).

**Spec**

* Events: 40 customer invoices (three currencies, two partially paid, one voided, one credit note), 20 vendor bills, 24 Stripe-shaped platform events, 6 payroll runs through the mock adapter, 3 manual adjustments, one period close; every event carries a deterministic `source.id` so re-seeding is idempotent.
* Expected report values are computed by an independent 80-line script (plain arithmetic on the YAML) and committed; PAP-183 asserts equality to the cent.
* Seed runs in under 60 s on PGlite and Postgres; `--reset` rolls back by reversing entries (ledger immutability respected).
* Fixture names and amounts are obviously fictional; no real company names.

**Interface contract**

Provides: `demo-finance` seed profile, `textbook.json`, golden transactions for `@paperos/contract-business-core/fixtures`, `pnpm db:seed --profile demo-finance`. Consumes: finance model and seeds (PAP-175), posting (PAP-392, PAP-394), documents (PAP-395), demo seed conventions (PAP-208).

**Definition of done**

* Seed idempotent (second run creates zero entries); `verifyChain` green after seeding; expected values file committed with the generator script.
* PAP-183 and PAP-186 test suites consume the fixture (comment on both issues); PAP-487 fixtures folder points at the exported transactions.
* `docs/finance/demo-seed.md` lists every event; CHANGELOG.

**Test plan**

* Unit: generator determinism (same YAML, same ids), expected-value script against three hand-checked months.
* E2E: `pnpm db:seed --profile demo-finance && pnpm ledger verify demo` exits 0 and `/finance/reports/pnl` shows the September net income from `textbook.json`.

**Demo**

Reviewer seeds, opens the P&L and compares three lines with `textbook.json`. Under two minutes.

**Edge cases**

* Seed on a tenant with existing entries: refused unless `--tenant` is a fresh demo tenant.
* Chart subtype missing (custom chart): seed fails naming the subtype before writing.

**Dependencies**

Hard: PAP-175, PAP-392, PAP-395. Soft: PAP-394, PAP-208. Blocks PAP-183, PAP-186, PAP-487 (fixtures).

**Agent**

Builder: Ledger (Bookkeeper) with Quill. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
