---
identifier: "PAP-448"
title: "Publish @paperos/contract-data-layer v0.1 with manifest"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-33", "PAP-279", "PAP-302", "PAP-303", "PAP-433"]
blocks: ["PAP-100", "PAP-175", "PAP-187", "PAP-347", "PAP-451", "PAP-454"]
key: "module/data-layer/contract"
url: "https://linear.app/paperos/issue/PAP-448/publish-paperoscontract-data-layer-v01-with-manifest"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:54:04.437Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-448: Publish @paperos/contract-data-layer v0.1 with manifest

**Model / Effort:** Opus 5 / high

**Goal**

Publish `@paperos/contract-data-layer` v0.1 and the `data-layer` module manifest so every other module codes against a versioned package instead of `packages/db, packages/api-contract, packages/api-client, packages/sync, packages/jobs, packages/files, packages/search, packages/email, packages/core/{types,filter,events}` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `critical`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/data-layer/` published as `@paperos/contract-data-layer` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-data-layer', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Forge', project: 'data-layer' }`, `swapRisk: 'critical'`, `kind: 'runtime core'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/data-layer.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-33, PAP-302, PAP-303, PAP-279 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* Pinned re-exports of contract-zero: `@paperos/core/types` (PAP-302), `core/filter` (PAP-279), `core/events` (PAP-303)
* `TenantContextPort` (`withTenant`, the RLS session variables of PAP-34) and `UnitOfWork`
* `RepositoryPort<T>` base interface (`get`, `list` with `FilterTree`, `create`, `update`, `archive`, `restore`) that every module repository extends
* `EventBusPort` (`publish`, `subscribe`, outbox drain), `JobsPort` (`defineJob`, `enqueue`, `schedule`; PAP-43), `FilesPort` (PAP-37), `SearchPort` (`registerSearchable`; PAP-39), `AuditPort` (PAP-38)
* `SyncPort` (shape registry, `useShape`, outbox status; PAP-270 to PAP-272), `EmailPort` (PAP-370), `IdempotencyPort` and rate-limit descriptors (PAP-304)
* API conventions as types: `ApiErrorBody`, list input and output, headers, procedure naming (PAP-267, PAP-268)

Events declared with `defineTopic()` (payload schemas, version 1): `record.created|updated|deleted`, `file.ready|failed`, `job.finished|failed`, `sync.conflict`.

Requires (manifest `requires[]`): \* `@paperos/contract-identity` ^0.1 (`Principal` in request scope)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-data-layer@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.data-layer`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-33 (Model core platform entities: tenant, workspace, user, membe), PAP-302 (Specify shared value types and wire encodings in `packages/c), PAP-303 (Specify the domain event contract: envelope, topic catalogue), PAP-279 (Specify the shared filter and condition grammar (`packages/c). Consumed by: PAP-100 (PM entities), PAP-175 (finance model), PAP-187 (CRM model), PAP-347 (import connector), PAP-129 (prompt log store) and every module repository, and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (twenty envelope samples (valid, unregistered topic, wrong version), six `FilterTree` queries with expected SQL, four job payloads, three file lifecycle traces, two tenant contexts (one missing, fails closed)); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Sentinel confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/data-layer.md` generated; short ADR `docs/adr/00xx-contract-data-layer.md` recording what was pinned.
* Comments on PAP-100, PAP-175, PAP-187, PAP-347 that their Interface contract sections now import from `@paperos/contract-data-layer`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-33, PAP-302, PAP-303, PAP-279. Blocks PAP-100, PAP-175, PAP-187, PAP-347, `module/data-layer/conformance` and `module/data-layer/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Forge (Data Layer & Database owner). Reviewed by Sentinel and Atlas (contract ownership).

**Size**

M

**Demo**

Reviewer opens `docs/platform/contracts/data-layer.md` (generated) and sees every port with its Zod schema; runs `pnpm conformance data-layer --impl memory` and watches the in-memory doubles pass the repository, event bus and jobs suites without Postgres. Under two minutes.
