---
identifier: "PAP-119"
title: "Specify the data section (entities, queries, mutations, sync mode) and generate typed hooks from it"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: ["PAP-311", "PAP-312", "PAP-313"]
blockedBy: ["PAP-35", "PAP-114", "PAP-269", "PAP-279"]
blocks: ["PAP-362"]
key: "spec-builder/data-section"
url: "https://linear.app/paperos/issue/PAP-119/specify-the-data-section-entities-queries-mutations-sync-mode-and"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:16.403Z"
model: null
effort: null
---

# PAP-119: Specify the data section (entities, queries, mutations, sync mode) and generate typed hooks from it

**Goal**

Finalise the `data` section so pages declare the entities, queries and mutations they need together with a sync mode, and a generator turns that declaration into typed React hooks backed by oRPC or Electric shapes. Agents stop hand-writing data plumbing and the spec stays the truth about what a page reads and writes. Umbrella for three children.

**Scope**

* Children (build in order):
  * PAP-311: data section schema and validator rules.
  * PAP-312: hook generator for server, live and local modes.
  * PAP-313: example page end to end with offline test.
* Out: the API and sync layers (PAP-35, PAP-36), table view models (PAP-161), server-side query compilation (PAP-163).

**Spec**

* Shape: `entities[]`, `queries: Record<name, { entity, filter: FilterTree, sort[], fields[], sync: live | local | server, page }>`, `mutations: Record<name, { entity, action: create | update | delete | custom, input, optimistic, audit }>`.
* `FilterTree` imported from `@paperos/core/filter` (PAP-279); no local copy.
* Access rows from PAP-116 are merged into every query filter as an `all` node at generation time; the server still enforces.
* Generated `apps/web/src/generated/<id>.data.ts`: `use<PascalCase(query)>()` returning `{ data, status, error, fetchNextPage, isStale }`, `use<PascalCase(mutation)>()` returning `{ mutate, mutateAsync, status }` with optimistic update and rollback; `server` uses TanStack Query and the PAP-35 client, `live | local` use `useShape` from PAP-36 with the offline outbox.
* Types resolved from the PAP-35 contract package so `fields` are checked at generation time; hook name collisions fail generation; files carry a banner and are drift-checked.

**Interface contract**

* Provides: `DataSectionSchema`, type `DataSection`, `pnpm spec gen:data [id] [--all] [--check]`, generated hooks, `dataStates` export for PAP-120, rules `DATA_UNKNOWN_ENTITY`, `DATA_UNKNOWN_FIELD`, `DATA_PARAM_UNBOUND`, `DATA_MUTATION_WITHOUT_ACCESS`, `DATA_UNSCOPED`.
* Consumers: PAP-120 imports hooks and `dataStates`; PAP-122 mocks `../generated/<id>.data`; PAP-123 derives `reads` and `writes` edges; PAP-124 form editor edits this shape; PAP-125 examples.
* Requires: PAP-114 schema, PAP-35 client and contract package (hard for `server`), PAP-279 `FilterTree`, PAP-116 rows, PAP-36 (`live | local`), PAP-38 audit `reason` field.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (query `where` clauses are `FilterTree` from `@paperos/core/filter` (PAP-279); the local copy with a TODO is removed); §4 (generated hooks call the procedure shape `{ cursor?, limit<=100, filter?: FilterTree, sort?: { field, dir }[] }` returning `{ items, nextCursor }`, and mutations send `Idempotency-Key` and `X-PaperOS-Reason` for agents); §6 rows "`FilterTree`", "Routers, client, pagination" and "Page and app spec schema".

**Definition of done**

* All three children Done.
* Umbrella: `customer-invoices` hooks render a list from seeded Postgres in Playwright at 375 and 1280 px; a mutation appears in a second browser context within 1 s in `live` mode; offline mutation queues and applies on reconnect.
* `docs/spec/data.md`; drift check in gate 1; changelog; Linear comment with screenshots and the generated file.

**Test plan**

* Umbrella e2e (Playwright): two contexts, `context.setOffline`, list render at 375 and 1280 px.
* Generator snapshots for all three modes (child 2); rule fixtures (child 1).
* Visual: the example list at 375 and 1280 px in light and dark through gate 3.

**Demo**

Add a `sort` to the `invoices` query in the example spec, run `pnpm spec gen:data customer-invoices`, open the page and see the order change; toggle the browser offline, mark an invoice paid, go online and watch it sync. Two minutes.

**Edge cases**

* Unscoped query on a tenant table: generator injects tenant scope; warning if no access row.
* `page` above 200: capped with warning; hook paginates.
* Field renamed in Drizzle: generation fails, not runtime.
* `sync: live` without a registered shape: falls back to `server` with a warning.
* Route param type mismatch: validator error from `validateSearch` types.

**Dependencies**

Blocked by PAP-114, PAP-35, PAP-279. Soft: PAP-36, PAP-116, PAP-38. Consumed by PAP-120, PAP-122.

**Agent**

Built by Forge (Schema Wright) for the generator with Quill (Page Spec Writer) on the schema; reviewed by Sentinel.

**Size**

L (umbrella; children S, M, M)
