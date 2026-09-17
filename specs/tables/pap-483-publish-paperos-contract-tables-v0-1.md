---
identifier: "PAP-483"
title: "Publish @paperos/contract-tables v0.1 with manifest"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-161", "PAP-162", "PAP-433"]
blocks: ["PAP-102", "PAP-183", "PAP-189", "PAP-333", "PAP-486", "PAP-489"]
key: "module/tables/contract"
url: "https://linear.app/paperos/issue/PAP-483/publish-paperoscontract-tables-v01-with-manifest"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:00:32.576Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-483: Publish @paperos/contract-tables v0.1 with manifest

**Model / Effort:** Sonnet 5 / high

**Goal**

Publish `@paperos/contract-tables` v0.1 and the `tables` module manifest so every other module codes against a versioned package instead of `packages/views` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `high`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/tables/` published as `@paperos/contract-tables` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-tables', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Nova', project: 'tables' }`, `swapRisk: 'high'`, `kind: 'runtime'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/tables.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-161, PAP-162 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* `ViewSpec`, `FieldDef`, `DatasetRef` and the ten view kinds enum (PAP-161); `registerDataset()` registration contract for code datasets
* `ViewQueryPort`: `compile(view) -> { sql, shape? }`, `execute(view, cursor)`, signed keyset cursors shared with PAP-268 (PAP-335 to PAP-337)
* `ViewRendererRegistry` (`registerViewKind`) and `FieldTypePlugin` interface (`parse`, `format`, `filterOps`, `cellRenderer` id; PAP-338 to PAP-340)
* `FormulaPort` (`parse`, `typeCheck`, `evaluate`, `compileSql`; PAP-171) and `AutomationTriggerPort` (PAP-388)
* `RecordPort` (detail, trash, bulk; PAP-333, PAP-334); slot exposes `view.toolbar`, `record.panel.tabs`; fills `dashboard.blocks:view`

Events declared with `defineTopic()` (payload schemas, version 1): `view.shared`, `record.created|updated|deleted` (filtered by dataset), `automation.run.finished`.

Requires (manifest `requires[]`): \* `@paperos/contract-data-layer` ^0.1 (`FilterTree`, cursors, repositories)

* `@paperos/contract-identity` ^0.1 (`can`, SQL predicate)
* `@paperos/contract-design-system` ^0.1 (cell renderer ids)
* `@paperos/contract-input` ^0.1 (drag-and-drop, keyboard)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-tables@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.tables`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-161 (Specify the view model: data source, fields, filters, sorts,), PAP-162 (Audit Airtable, Notion, ClickUp, Baserow and NocoDB view fea). Consumed by: PAP-102 (PM boards), PAP-183 (finance reports as views), PAP-189 (CRM views), PAP-333 (record features), PAP-347 import mapping, PAP-207 template packs, PAP-113 org chart, and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (ten golden `ViewSpec`s (one per kind) over two datasets with expected rows, cursors and aggregates; twelve field type samples; six formulas with expected types and SQL; two automation triggers); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Forge confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/tables.md` generated; short ADR `docs/adr/00xx-contract-tables.md` recording what was pinned.
* Comments on PAP-102, PAP-183, PAP-189, PAP-333 that their Interface contract sections now import from `@paperos/contract-tables`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-161, PAP-162. Blocks PAP-102, PAP-183, PAP-189, PAP-333, `module/tables/conformance` and `module/tables/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Nova (Table & Views Engine owner). Reviewed by Forge and Atlas (contract ownership).

**Size**

M

**Demo**

Reviewer runs `pnpm contract:show tables`, validates the ten golden views and sees the compile fixtures' expected SQL rendered side by side. Under a minute.
