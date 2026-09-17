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
children: []
blockedBy: ["PAP-114", "PAP-269", "PAP-279", "PAP-35"]
blocks: []
key: "spec-builder/data-section"
url: "https://linear.app/paperos/issue/PAP-119/specify-the-data-section-entities-queries-mutations-sync-mode-and"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-119: Specify the data section (entities, queries, mutations, sync mode) and generate typed hooks from it

**Goal**

Finalise the `data` section of a page spec so pages declare the entities, queries and mutations they need together with a sync mode, and a generator turns that declaration into typed React hooks backed by oRPC or Electric shapes. Agents stop hand-writing data plumbing and the spec stays the truth about what a page reads and writes.

**Scope**

In:
- Zod 4 `DataSection` in `packages/spec/src/schema/data.ts`:
  ```yaml
  data:
    entities: [invoice, customer]
    queries:
      invoices:
        entity: invoice
        filter: { all: [{ field: status, op: in, value: [open, overdue] }, { field: customerId, op: eq, param: route.customerId }] }
        sort: [{ field: dueAt, dir: asc }]
        fields: [id, number, total, status, dueAt, customer.name]
        sync: live          # live (Electric shape) | local (PGlite first) | server (oRPC only)
        page: 50
    mutations:
      markPaid: { entity: invoice, action: update, input: { id: uuid, paidAt: datetime }, optimistic: true, audit: true }
  ```
- Filter grammar shared with `tables/view-model-spec` (import its `FilterTree` type once it lands; until then identical shape in `packages/spec/src/schema/filter.ts` with a TODO).
- Generator `pnpm spec gen:data [id]` writing `apps/web/src/generated/<id>.data.ts`: `useInvoices(params)` returning `{ data, status, error, fetchNextPage, isStale }`, and `useMarkPaid()` returning `{ mutate, mutateAsync, status }` with optimistic cache update and rollback. `sync: server` uses TanStack Query 5 plus the oRPC client from `data-layer/api-layer`; `sync: live|local` uses `useShape` from `data-layer/local-first-sync` with the offline queue for mutations.
- Types resolved from `packages/api-contract` Zod schemas (generated from Drizzle) so `fields` are checked at generation time.
- Validator rules: `DATA_UNKNOWN_ENTITY`, `DATA_UNKNOWN_FIELD`, `DATA_PARAM_UNBOUND` (`param` not a route param, search param or `actor.*`), `DATA_MUTATION_WITHOUT_ACCESS` (no matching `access.actions`).
- Generated files carry a banner, are committed and drift-checked.

Out: the API and sync layers themselves, the view model for tables, server-side query compilation (`tables/query-compiler`).

**Spec**

- Access rows from `spec-builder/access-section` are merged into every query filter at generation time as an `all` node, so a page cannot request rows it may not see; server still enforces.
- Relation fields (`customer.name`) allowed one level deep; generator emits an oRPC `include` or a joined shape.
- `optimistic: true` requires the mutation input to include the entity id; generator emits a typed updater.
- `audit: true` sets the `reason` field requirement on the mutation input per `data-layer/audit-log`.
- Hook names are `use<PascalCase(queryName)>`; collisions with existing exports fail generation.
- Loading, empty and error states from `states` are exported as `dataStates` for codegen.

**Definition of done**

- Vitest: schema fixtures, each validator rule, generator snapshot for `server`, `live` and `local` modes, optimistic rollback behaviour with a mocked client.
- Example page `customer-invoices` generated hooks render a list from seeded Postgres in Playwright at 375 and 1280, with a mutation reflected in a second browser context within 1 s (live mode).
- Offline test: mutation queued with network off, applied on reconnect (Playwright `context.setOffline`).
- `docs/spec/data.md` with grammar and hook usage; CHANGELOG entry; Linear comment with screenshots and the generated file.
- Drift check passes in gate 1.

**Edge cases**

- Query with no filter on a multi-tenant table: generator injects tenant scope; validator warns `DATA_UNSCOPED` if the entity is tenant-scoped and no access row exists.
- `page` above 200: capped at 200 with a warning (API limit is 100 per request, hook paginates).
- Field renamed in Drizzle: generation fails at the field check, not at runtime.
- Two queries share a name across pages: fine, hooks are per file.
- `sync: live` on an entity without an Electric shape registered: generator falls back to `server` and warns.
- Route param type mismatch (uuid vs number): validator error using route `validateSearch` types.

**Dependencies**

`spec-builder/schema` (hard), `data-layer/api-layer` (hard for `server` mode). Soft: `data-layer/local-first-sync` (live and local modes), `spec-builder/access-section` (row merge), `tables/view-model-spec` (shared filter type). Unblocks `spec-builder/layout-codegen` state wiring and `spec-builder/conformance-tests`.

**Agent**

Built by Forge (Schema Wright) for the generator with Quill (Page Spec Writer) owning the YAML shape. Reviewed by Sentinel (Code Reviewer, Security Auditor for row scoping) and Nova.

**Size**

L: three sync modes, optimistic updates and typed generation against two backends.
