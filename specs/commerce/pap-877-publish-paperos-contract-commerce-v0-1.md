---
identifier: "PAP-877"
title: "Publish @paperos/contract-commerce v0.1 with manifest"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Commerce contract and catalog"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-264", "PAP-279", "PAP-302", "PAP-303", "PAP-305", "PAP-433", "PAP-556", "PAP-878"]
blocks: ["PAP-879", "PAP-880", "PAP-883", "PAP-884", "PAP-891", "PAP-892"]
key: "r4/commerce/contract-publish"
url: "https://linear.app/paperos/issue/PAP-877/publish-paperoscontract-commerce-v01-with-manifest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:18.103Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-877: Publish @paperos/contract-commerce v0.1 with manifest

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec M

**Goal**

Publish `@paperos/contract-commerce` v0.1 and the `commerce` module manifest so every other module codes against a versioned package instead of `packages/commerce, apps/web/src/commerce, packs/*` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays in the project's Build issues. Swap risk is declared `medium` and kind `runtime`, which decides how much of the swap playbook a rewrite must follow. This is a new module: the contract is written before the implementation, so the Build issues in this project consume it from day one rather than being retrofitted.

**Scope**

In: `packages/contracts/commerce/` published as `@paperos/contract-commerce` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`. `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-commerce', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Ledger', project: 'commerce' }`, `swapRisk: 'medium'`, `kind: 'runtime'`, plus the generated `module.manifest.json`. `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/commerce.md` (a `typedoc` stub until the docs generator PAP-445 lands). A `## Module boundary` paragraph on this project's model or umbrella issue naming the contract version each Build issue implements.

Out: Runtime behaviour, React, Drizzle tables, network calls. The conformance suite and the kernel binding (own issues). Changing contract-zero types; anything missing there is filed against PAP-302, PAP-279 or PAP-303.

**Spec**

* Ports and schemas exported at v0.1: `CatalogPort` (`products`, `variants`, `priceLists`, `resolvePrice`) with `Product`, `Variant`, `PriceList`; `InventoryPort` (`stock`, `move`, `reserve`, `release`, `count`) with `StockLocation`, `StockMovement`; `OrderPort` (`create`, `pay`, `fulfil`, `return`, `refund`) with `Order`, `OrderLine`, `Fulfilment`, `Return`; `ShippingLabelPort`; `PosPort` (`session`, `sale`, `tender`, `closeShift`) and `TerminalPort`; `PurchasingPort` (`po`, `receive`, `bill`, `match`, `schedulePayment`); `ProjectsPort` (`projects`, `timeEntries`, `timer`, `invoiceFromTime`) and `HrPort` (`directory`, `timeOff`, `shifts`, `timesheets`, `toPayroll`); `AssetsPort` (`assets`, `schedules`, `workOrders`), `SubscriptionsPort`, `MarketplacePort` (`vendors`, `listings`, `split`, `payouts`); `PackPort` (`apply`, `lint`, `conformance`) with the `pack.yaml` extensions (`services`, `resources`, `workflows`, `documents`, `characters`, `smoke`); slots `portal.orders`, `record.panel.tabs.stock`, `dashboard.blocks.commerce`, `pos.tender.methods`, `shell.header.actions` (timer)
* Events declared with `defineTopic()` (payload schemas, version 1): `product.updated`, `stock.moved`, `stock.low`, `order.created`, `order.paid`, `order.fulfilled`, `order.returned`, `order.refunded`, `pos.sale.completed`, `pos.shift.closed`, `po.issued`, `po.received`, `bill.approved`, `bill.paid`, `time.entry.logged`, `timesheet.approved`, `timeoff.approved`, `shift.published`, `workorder.created`, `workorder.completed`, `subscription.customer.activated`, `subscription.customer.cancelled`, `vendor.payout.created`
* Requires (manifest `requires[]`): `@paperos/contract-business-core` ^0.1 (finance model, ledger, posting rules, documents, Checkout, Connect, Tax, payroll); `@paperos/contract-tables` ^0.1 (datasets, views, field types, calendar, Gantt); `@paperos/contract-data-layer` ^0.1 (jobs, idempotency, files, audit, recurrence, offline outbox); `@paperos/contract-identity` ^0.1 (`Principal`, audiences incl. `vendor`, attribute predicates); `@paperos/contract-workflows` ^0.1 (approvals, forms, e-sign; optional); `@paperos/contract-engagement` ^0.1 (availability shape, loyalty tenders; optional); `@paperos/contract-app-shell` ^0.1 (kiosk mode, native scanner and camera); `@paperos/contract-migration` ^0.1 (pack format and applier)
* Rules: Zod 4 only, JSON Schema generated and committed; no `z.bigint()` on wire schemas (PAP-302 `Money` codec); one sentence of doc and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`, never hand-written
* Every port method that mutates money, sends a message or signs a document carries `Idempotency-Key` semantics from PAP-304 in its signature (`{ idempotencyKey }` option) so adapters cannot forget it
* Error codes reuse the contracts document catalogue (`NOT_FOUND`, `FORBIDDEN`, `CONFLICT`, `MODULE_DISABLED`, `RATE_LIMITED`); module-specific codes are listed in `errors.ts` with user-facing copy keys (PAP-368)

**Interface contract**

Provides: `@paperos/contract-commerce@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.commerce`. Consumes: the manifest schema and validator (PAP-433), contract-zero (`@paperos/core/types|filter|events`, PAP-302, PAP-279, PAP-303), the base manifest shape (PAP-264) and the ownership map (PAP-305). Consumed by: business-core reports (PAP-183), growth (order and subscription activity), engagement (loyalty earn, shifts), assistant (order and stock tools), platform-ops (commerce metrics), migration (gallery and importers), and this module's conformance and wire issues.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; `pnpm modules:validate` and `pnpm gen:dep-map` green with the new module present
* Generated JSON Schema, `typedoc` stub and ownership entry committed; `compat-matrix.json` (PAP-440) shows every `requires` resolving
* Sentinel confirms no implementation leaked into the package (no React, no Drizzle, no fetch)
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (a 50-product catalog with 300 variants and 500 movements across two locations, twelve orders across the status machine with posting traces, one POS shift with mixed tenders and an offline replay, a PO-receipt-bill match trio, two projects with forty time entries and a retainer, a two-week schedule with clock events and a payroll export, ten assets with a maintenance schedule and three work orders, two customer subscriptions with webhook fixtures, a three-vendor split order, and sixteen pack manifests); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Sentinel reads the package top to bottom against `docs/module-system.md` section 2 and the contracts document; every port method has a fixture.

**Demo**

`pnpm modules:validate` prints the `commerce` manifest with its provides and requires, `pnpm gen:dep-map` shows the new node with only declared edges, and `docs/platform/contracts/commerce.md` renders the port list.

**Edge cases**

* A port needed by a Build issue but missing at v0.1 is added as a minor bump (`0.2.0`) with a fixture, never as a direct import of the implementation
* A type that two contracts both want (for example a scheduling `TimeRange`) goes to contract-zero via PAP-302, not into this package, to avoid a dependency between contracts

**Dependencies**

PAP-433 manifest schema (hard), contract-zero PAP-302, PAP-279, PAP-303 (hard), PAP-264 and PAP-305 (soft, shape only). Unblocks every other issue in this project.

**Agent**

Builder: Ledger. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
