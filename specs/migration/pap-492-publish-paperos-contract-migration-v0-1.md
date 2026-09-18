---
identifier: "PAP-492"
title: "Publish @paperos/contract-migration v0.1 with manifest"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Import framework and CSV"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-198", "PAP-433"]
blocks: ["PAP-414", "PAP-417", "PAP-420", "PAP-426", "PAP-494", "PAP-496"]
key: "module/migration/contract"
url: "https://linear.app/paperos/issue/PAP-492/publish-paperoscontract-migration-v01-with-manifest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:00.110Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 2
dueDate: "2026-09-28"
cycle: null
---

# PAP-492: Publish @paperos/contract-migration v0.1 with manifest

**Model / Effort:** Sonnet 5 / high

**Goal**

Publish `@paperos/contract-migration` v0.1 and the `migration` module manifest so every other module codes against a versioned package instead of `packages/import` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `low`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/migration/` published as `@paperos/contract-migration` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-migration', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Scout', project: 'migration' }`, `swapRisk: 'low'`, `kind: 'runtime'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/migration.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-198 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* `SourceConnector` interface (`discover`, `stream`, `auth`, `capabilities`; PAP-347) and `MappingModel` (source field to `FieldDef`, two-pass relations; PAP-415)
* `ImportRun` state machine (dry run, commit, rollback; PAP-348) and `ExternalIdMap` (PAP-201)
* `ExportArchive` format v1.0 (manifest, JSON Schemas, tables, docs, files, ledger; PAP-420) and the round-trip `paperos` connector contract (PAP-422)
* `TemplatePack` schema and applier contract (PAP-426), `MigrationInterview` output for the migration agent (PAP-208)

Events declared with `defineTopic()` (payload schemas, version 1): `import.started|finished|rolled_back`, `export.finished`, `template.applied`.

Requires (manifest `requires[]`): \* `@paperos/contract-tables` ^0.1 (datasets, fields)

* `@paperos/contract-data-layer` ^0.1 (jobs, files)
* `@paperos/contract-collab` ^0.1 (docs import)
* `@paperos/contract-business-core` ^0.1 (finance import; optional)
* `@paperos/contract-pm-linear` ^0.1 (PM import; optional)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-migration@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.migration`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-198 (Catalog export formats and API limits of Airtable, Notion, C). Consumed by: PAP-414 (Airtable connector), PAP-417 (Notion connector), PAP-420 (export archive), PAP-426 (template packs), PAP-413 (Monday and HubSpot), PAP-423 (Stripe and QuickBooks), and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (three source snapshots (CSV, Airtable metadata, Notion database) with expected mappings, two import runs (commit, rollback), one export archive that round-trips, one template pack); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Nova confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/migration.md` generated; short ADR `docs/adr/00xx-contract-migration.md` recording what was pinned.
* Comments on PAP-414, PAP-417, PAP-420, PAP-426 that their Interface contract sections now import from `@paperos/contract-migration`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-198. Blocks PAP-414, PAP-417, PAP-420, PAP-426, `module/migration/conformance` and `module/migration/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Scout (Migration & Import Tools owner). Reviewed by Nova and Atlas (contract ownership).

**Size**

S

**Demo**

Reviewer runs `pnpm contract:show migration` and streams the CSV fixture through the reference connector in `conformance/`, seeing the inferred `FieldDef`s. Under a minute.
