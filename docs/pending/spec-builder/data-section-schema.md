---
key: "spec-builder/data-section/schema"
title: "Data section: Zod schema, shared FilterTree import and validator rules"
project: "spec-builder"
parent: "PAP-119"
phase: "P1"
type: "Spec"
priority: null
size: "S"
surfaces: ["Developer"]
milestone: null
intendedState: "Backlog"
blockedBy: []
blocks: ["spec-builder/data-section/generator", "spec-builder/data-section/example"]
source: "round2/agent2/new_spec.py"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-spec-builder-11-c314e290076b"
identifier: "PAP-311"
status: "created"
createdAt: "2026-09-17"
---

# Data section: Zod schema, shared FilterTree import and validator rules

**Goal**

Finalise the `data` section shape and its validator rules so the generator has a fixed target: entities, queries with the shared filter grammar, sort, fields, sync mode and paging, mutations with action, input, optimistic and audit flags, all checked against the app spec and the API contract at validation time.

**Scope**

* In: `packages/spec/src/schema/data.ts`, rules registered through PAP-115 `defineRule`, fixtures, `docs/spec/data.md` grammar section.
* Out: hook generation (`spec-builder/data-section/generator`), the example page (`spec-builder/data-section/example`).

**Spec**

* `DataSection = { entities: EntityId[], queries: Record<QueryName, Query>, mutations: Record<MutationName, Mutation> }`; `Query = { entity, filter?: FilterTree, sort?: { field, dir }[], fields: FieldPath[], sync: "live" | "local" | "server", page?: number (1-200) }`; `Mutation = { entity, action: "create" | "update" | "delete" | "custom", input: Record<string, ScalarType>, optimistic?: boolean, audit?: boolean }`.
* `FilterTree` imported from `@paperos/core/filter` (PAP-279); leaves may use `param: route.<name> | search.<name> | actor.<attr>` in place of `value`.
* `FieldPath` allows one relation hop (`customer.name`); names checked against the PAP-35 contract package when present, else against `entities[].fields` in the app spec with a warning.
* Rules: `DATA_UNKNOWN_ENTITY`, `DATA_UNKNOWN_FIELD`, `DATA_PARAM_UNBOUND`, `DATA_MUTATION_WITHOUT_ACCESS` (no matching `access.actions` entry), `DATA_UNSCOPED` (tenant-scoped entity, no access row, no tenant filter), `DATA_PAGE_RANGE` (warn), `DATA_OPTIMISTIC_NO_ID`.
* Names: `^[a-z][a-zA-Z0-9]*$`; hook names derived later must not collide (`DATA_HOOK_COLLISION` warn).

**Interface contract**

* Provides: `DataSectionSchema`, types `DataSection`, `Query`, `Mutation`, `FieldPath`, rule ids, `resolveFields(query, contract): ResolvedField[]`.
* Consumers: generator child, PAP-123 (`reads` and `writes` edges), PAP-124 form editor, PAP-116 (`rows` merge target), PAP-118 templates.
* Requires: PAP-114, PAP-279 `FilterTree`, PAP-115 rule API, PAP-35 contract types (soft), PAP-117 entities.

**Definition of done**

* Fixtures for every rule pass and fail; schema snapshot.
* Example spec sections for the three PAP-125 pages validate.
* Grammar documented; changelog; Linear comment.

**Test plan**

* Unit: schema and rule fixtures; `param` binding against a route with `$customerId` and a search schema.
* Integration: validator run with and without the contract package present.
* No UI.

**Demo**

Add `filter: { field: status, op: eq, param: route.status }` to a query on a route without `$status` and run `pnpm spec:validate`: `DATA_PARAM_UNBOUND` names the param and the route. Under one minute.

**Edge cases**

* Relation two hops deep: rejected with a hint to add a query.
* `sync: live` on a non-Electric entity: allowed here; generator falls back with a warning.
* Mutation `custom` without an oRPC procedure of that name: `DATA_UNKNOWN_PROCEDURE`.
* Filter referencing `actor.*` on a public page: error via PAP-116 interplay.
* Empty `fields`: error; at least the id.

**Dependencies**

Blocked by PAP-114, PAP-279 (through the parent). Blocks both sibling children.

**Agent**

Built by Quill (Page Spec Writer); reviewed by Forge (Schema Wright).

**Size**

S
