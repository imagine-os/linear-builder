---
identifier: "PAP-176"
title: "Research payroll APIs (Check, Gusto Embedded, Deel, Rippling) for embeddability and pricing; write ADR"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P1"
type: "Research"
priority: 2
surfaces: ["Staff"]
milestone: "Stripe billing live"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-184"]
key: "business-core/payroll-research"
url: "https://linear.app/paperos/issue/PAP-176/research-payroll-apis-check-gusto-embedded-deel-rippling-for"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-176: Research payroll APIs (Check, Gusto Embedded, Deel, Rippling) for embeddability and pricing; write ADR

**Goal**

Choose the first embedded payroll provider by evaluating Check, Gusto Embedded, Deel and Rippling against embeddability, API completeness, sandbox access, pricing, geography and compliance ownership, and record the decision as an ADR that defines the provider interface `business-core/payroll-adapter` will implement.

**Scope**

In:
- Research doc `docs/finance/payroll-research.md` with a scored rubric and evidence links.
- ADR `docs/adr/00xx-payroll-provider.md` (context, options, decision, consequences, reopen criteria).
- Draft `PayrollProvider` interface (TypeScript, no implementation) in `packages/finance/src/payroll/provider.ts` derived from the intersection of provider capabilities.
- Sandbox access request written as a Needs Justin item with the exact signup steps.

Out: any integration code, contract negotiation, non-US payroll beyond noting coverage.

**Spec**

- Rubric (weights): API-first embeddability (25): REST coverage for companies, employees, onboarding, pay schedules, payroll runs, paystubs, tax filings, webhooks; embeddable UI components for onboarding and tax setup. Sandbox availability without sales call (15). Pricing model and floor (15): per-employee-per-month, platform fees, revenue share. Compliance ownership (15): who is employer of record for filings, W-2/1099 generation, state registrations. Geography (10): US states, contractors international. Developer experience (10): docs, SDKs (TypeScript), idempotency, error model, rate limits. Time-to-first-payroll in sandbox (10). Score each 1-5 with evidence URLs and access dates.
- Method: `WebFetch` official docs and pricing pages; note where pricing is quote-only; check status pages and changelogs for cadence; record whether a sandbox key can be obtained in under a day.
- Interface draft: `PayrollProvider { id; capabilities(): Capabilities; companies: { create, get, onboardingLink }; employees: { upsert, onboardingLink, list }; contractors?: {...}; paySchedules: { list, create }; payrolls: { preview, create, approve, cancel, list, get }; paystubs: { list, pdfUrl }; taxes: { filings: list }; webhooks: { verify(sig, body), parse(body): PayrollEvent } }` with a `Capabilities` bitmap so the adapter can degrade features per provider. Include the ledger event shapes the adapter must emit (`payroll.approved` with wages, employer taxes, employee withholdings, net pay, provider fees per employee).
- Decision criteria: pick the highest score that offers sandbox access within the build window; document the runner-up and the exact conditions that would switch (pricing above X per employee, missing state coverage, no TypeScript SDK).
- Also record what PaperOS must build regardless of provider: employee record sync from `fin_employee`, pay-period calendar, approval flow, ledger posting, paystub access in the customer portal for employees.

**Definition of done**

- Research doc with scored table and at least 4 evidence links per provider.
- ADR merged with status `accepted` or `proposed` awaiting Justin's sandbox approval, stating the choice and reopen criteria.
- `provider.ts` interface compiles and is reviewed by the adapter builder.
- Needs Justin issue created with signup steps, expected cost and what he must approve (test-mode only).
- Parity note in `docs/views/parity.md` cross-links nothing; instead link the ADR from `libraries/registry`.
- CHANGELOG entry (docs); Linear comment summarising scores in a table.

**Edge cases**

- A provider requires a signed agreement before sandbox: score it but mark "blocked for build window".
- Pricing hidden behind sales: estimate from public partner case studies and flag as low-confidence.
- Provider APIs mixing employer-of-record and software models (Deel): evaluate the embedded software product only.
- Docs contradicting each other on webhook signing: record both and plan a verification spike in the adapter issue.
- International contractors needed by a future tenant: capture as a capability flag, not a blocker.

**Dependencies**

- `business-core/finance-data-model` for the employee entity shape; `libraries/eval-rubric` for the shared rubric format; feeds `business-core/payroll-adapter`.

**Agent**

Builder: Scout (Library Evaluator) with Ledger (Payroll Adapter) co-authoring the interface. Reviewer: Ledger lead and Atlas for the decision.

**Size**

S: one time-boxed research session plus ADR; the interface draft is the only artefact with lasting weight.
