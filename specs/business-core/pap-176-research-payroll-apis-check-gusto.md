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
blocks: ["PAP-184", "PAP-398"]
key: "business-core/payroll-research"
url: "https://linear.app/paperos/issue/PAP-176/research-payroll-apis-check-gusto-embedded-deel-rippling-for"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T05:24:42.837Z"
---

# PAP-176: Research payroll APIs (Check, Gusto Embedded, Deel, Rippling) for embeddability and pricing; write ADR

**Goal**

Choose the first embedded payroll provider by scoring Check, Gusto Embedded, Deel and Rippling on embeddability, API completeness, sandbox access, pricing, geography and compliance ownership, and record it as an ADR that fixes the `PayrollProvider` interface PAP-184 implements.

**Scope**

In: `docs/finance/payroll-research.md` (scored rubric with evidence links and access dates); ADR `docs/adr/00xx-payroll-provider.md`; draft interface `packages/finance/src/payroll/provider.ts` (types only); one Needs Justin item with exact sandbox signup steps and expected cost.

Out: integration code, contract negotiation, non-US payroll beyond a coverage note.

**Spec**

* Rubric weights: API embeddability 25 (companies, employees, onboarding, schedules, runs, paystubs, filings, webhooks, embeddable components); sandbox without a sales call 15; pricing model and floor 15; compliance ownership 15 (filings, W-2/1099, state registrations); geography 10; developer experience 10 (TypeScript SDK, idempotency, errors, rate limits); time to first sandbox payroll 10. Score 1 to 5 with URLs.
* Method: official docs, pricing pages, status pages and changelogs via WebFetch; note quote-only pricing; record whether a sandbox key is obtainable within a day.
* Interface draft: `PayrollProvider { id; capabilities(): Capabilities; companies: { create, get, onboardingLink }; employees: { upsert, onboardingLink, list }; contractors?; paySchedules: { list, create }; payrolls: { preview, create, approve, cancel, list, get }; paystubs: { list, pdfUrl }; taxes: { filings }; webhooks: { verify(sig, body), parse(body): PayrollEvent } }` plus the `payroll.approved` event shape (gross, employer taxes, withholdings, net, fees per employee).
* Decision rule: highest score with sandbox access inside the build window; document runner-up and switch conditions (price per employee above X, missing state coverage, no TypeScript SDK).
* List what PaperOS builds regardless of provider: employee sync from `fin_employee`, pay-period calendar, approval flow, ledger posting, paystub portal.

**Interface contract**

Provides: `PayrollProvider`, `Capabilities`, `PayrollEvent` types (compiled, no implementation), the ADR decision and reopen criteria, the Needs Justin sandbox request. Consumes: `fin_employee` shape (PAP-175), rubric format (PAP-210), license policy (PAP-211). Consumed by PAP-184 (implements the interface) and PAP-186 (upcoming payroll block reads `payroll_run`, shaped here).

**Definition of done**

* Research doc with the scored table and at least four evidence links per provider.
* ADR merged as `accepted` or `proposed` pending Justin's sandbox approval, naming choice, runner-up and reopen criteria.
* `provider.ts` compiles under strict TypeScript and is acknowledged by the PAP-184 builder in a PR comment.
* Needs Justin issue filed with signup steps, cost and the test-mode-only scope.
* Registry entry drafted for PAP-215; CHANGELOG (docs); Linear comment with the score table.

**Test plan**

* Unit: `pnpm tsc --noEmit` on `provider.ts`; a Vitest type test asserting a mock adapter satisfies `PayrollProvider` and that `Capabilities` gates optional members.
* Review: rubric arithmetic checked by a 10-line script from `results.json`; every evidence URL returns 200 in a link-check step.
* E2E and visual: none (research deliverable).

**Demo**

Reviewer opens the ADR, reads the decision paragraph and the score table, then opens `provider.ts` and the Needs Justin issue listing the three signup steps. Under two minutes.

**Edge cases**

* Signed agreement required before sandbox: score it, mark "blocked for build window".
* Pricing behind sales: estimate from partner case studies, flag low confidence.
* Mixed EOR and software products (Deel): evaluate the embedded software only.
* Docs contradicting on webhook signing: record both, plan a verification spike in PAP-184.
* International contractors: capability flag, not a blocker.

**Dependencies**

None hard; starts now (moved to Ready for Claude per the round-2 audit). Uses PAP-175 for the employee shape and PAP-210 rubric if merged. Blocks PAP-184.

**Agent**

Builder: Scout (Library Evaluator) with Ledger (Payroll Adapter) co-authoring the interface. Reviewer: Ledger lead and Atlas for the decision.

**Size**

S: one time-boxed session plus ADR; the interface is the lasting artefact.
