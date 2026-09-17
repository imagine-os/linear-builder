---
identifier: "PAP-484"
title: "Publish @paperos/contract-business-core v0.1 with manifest"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Stripe billing live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-175", "PAP-433"]
blocks: ["PAP-178", "PAP-391", "PAP-407", "PAP-423", "PAP-487", "PAP-490"]
key: "module/business-core/contract"
url: "https://linear.app/paperos/issue/PAP-484/publish-paperoscontract-business-core-v01-with-manifest"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:00:32.576Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-484: Publish @paperos/contract-business-core v0.1 with manifest

**Model / Effort:** Sonnet 5 / high

**Goal**

Publish `@paperos/contract-business-core` v0.1 and the `business-core` module manifest so every other module codes against a versioned package instead of `packages/finance` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `high`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/business-core/` published as `@paperos/contract-business-core` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-business-core', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Ledger', project: 'business-core' }`, `swapRisk: 'high'`, `kind: 'runtime'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/business-core.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-175 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* Finance model types (customers, vendors, employees, accounts, transactions, journal; PAP-175) with `Money` from contract-zero
* `LedgerPort`: `postEvent(tx)` idempotent on `(source_type, source_id)`, `reverse`, `balances`, `closePeriod`; `PostingRule` registry (PAP-179, PAP-392 to PAP-394)
* `BillingProviderPort` (products, prices, subscriptions, portal, webhooks; Stripe adapter PAP-177), `PaymentsPort` (Connect; PAP-181), `TaxPort` (PAP-182)
* `PayrollProviderPort` (PAP-184, PAP-398) with idempotency keys and webhook status transitions; `DocumentPort` (invoice, quote, receipt lifecycle and PDF; PAP-180)
* `EntitlementPort` mapping plans to permissions (PAP-178) and `UsageMeterPort` (PAP-391); slot fills `shell.settings.sections:billing`, `dashboard.blocks:cashflow`

Events declared with `defineTopic()` (payload schemas, version 1): `invoice.issued|paid|voided`, `payment.succeeded|failed|refunded`, `subscription.updated`, `payroll.run.approved|paid`, `ledger.entry.posted|reversed`.

Requires (manifest `requires[]`): \* `@paperos/contract-data-layer` ^0.1 (`Money`, jobs, files, idempotency)

* `@paperos/contract-identity` ^0.1 (entitlements into `can`)
* `@paperos/contract-tables` ^0.1 (reports as views)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-business-core@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.business-core`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-175 (Specify the finance data model: customers, vendors, employee). Consumed by: PAP-178 (entitlements), PAP-391 (metering), PAP-407 (referral payouts), PAP-423 (Stripe import), PAP-186 (cash dashboard), PAP-196 referral program, and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (twelve business transactions with expected journal lines and balances (including JPY and a reversal), three Stripe webhook payloads, one Connect payout, two payroll runs (approved, failed), one invoice lifecycle to paid); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Sentinel confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/business-core.md` generated; short ADR `docs/adr/00xx-contract-business-core.md` recording what was pinned.
* Comments on PAP-178, PAP-391, PAP-407, PAP-423 that their Interface contract sections now import from `@paperos/contract-business-core`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-175. Blocks PAP-178, PAP-391, PAP-407, PAP-423, `module/business-core/conformance` and `module/business-core/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Ledger (Business Core: Payments, Finance & Payroll owner). Reviewed by Sentinel and Atlas (contract ownership).

**Size**

M

**Demo**

Reviewer runs `pnpm contract:show business-core` and posts the twelve transaction fixtures through the reference ledger in `conformance/`, seeing balanced entries and the reversal. Under a minute.
