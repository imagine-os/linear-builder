---
identifier: "PAP-163"
title: "Build the view query compiler from view model to SQL and Electric shapes with server-side pagination"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-161", "PAP-228", "PAP-229", "PAP-269", "PAP-279", "PAP-35", "PAP-59"]
blocks: ["PAP-165", "PAP-167", "PAP-168", "PAP-169", "PAP-170", "PAP-194", "PAP-195"]
key: "tables/query-compiler"
url: "https://linear.app/paperos/issue/PAP-163/build-the-view-query-compiler-from-view-model-to-sql-and-electric"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-163: Build the view query compiler from view model to SQL and Electric shapes with server-side pagination

**Goal**

Turn any `ViewSpec` into an efficient, RLS-respecting Postgres query and, where possible, an Electric shape, so views render server-paginated pages of rows, groups and aggregates without every view component writing SQL. This is the engine every view kind calls.

**Scope**

In:
- `packages/views/src/compiler/` with `compileView`, `compileFilter`, `compileSort`, `compileGroups`, `compileAggregates`.
- oRPC procedures `views.query`, `views.count`, `views.groups`, `views.distinct` in `packages/views/src/api.ts`.
- Electric shape registration for simple views (`data-layer/local-first-sync`).
- Client hook `useViewQuery(spec, { pageSize })` with infinite pagination.

Out: filter UI (`tables/filter-sort-group-ui`), formula evaluation (`tables/formula-engine`; compiler treats formula fields as opaque until then), full-text search ranking (`data-layer/search`).

**Spec**

- Input `compileView(spec: ViewSpec, ctx: { actor, tenantId, dataset: ResolvedDataset, cursor?, limit, groupPath?: GroupKey[] })` returns `{ rows: SQL, count: SQL, groups?: SQL, aggregates?: SQL, shape?: ShapeDef }` using Drizzle `sql` fragments. Never string-concatenate user values; all literals are bound parameters.
- Dataset resolution: entity datasets compile to real columns; custom datasets compile `record.data -> 'fieldKey'` with casts chosen from the field type (`::numeric`, `::timestamptz`, `::boolean`, `::text[]`). Custom datasets get a GIN index on `data` and expression indexes created on demand for fields used in sorts (`views.ensureIndex` job, capped at 10 per dataset).
- Filters: each `FilterOp` has a compile function per field type in `compiler/ops/<type>.ts`; relative dates resolve on the server in the actor's timezone; `{ ref: 'currentUser' }` resolves to `ctx.actor.id`. Relations compile to `EXISTS` subqueries; lookups/rollups compile to lateral joins.
- Sorting: keyset pagination using the sort fields plus `id` as tiebreaker; cursor is base64url JSON of the last row's sort values, signed with HMAC so clients cannot forge it. `limit` capped at 200; default 50.
- Grouping: `views.groups` returns group keys, counts and aggregates for a `groupPath` prefix (level-by-level, so 3-level grouping is three cheap queries); `views.query` with `groupPath` returns rows in one leaf group. Multi-select grouping uses `unnest` when `expandMulti` is set.
- Aggregates use `count`, `sum`, `avg`, `min`, `max`, `percentile_cont(0.5)`, `count(distinct)`, empty/filled via `count(*) filter (where ...)`.
- Permission predicate from `identity/rbac-abac` `toPredicate(actor, '<entity>.list', type)` is ANDed into every query; RLS remains the backstop.
- Electric shape emitted only when filters are a flat AND of `is|isAnyOf|isEmpty` on indexed columns and there are no groups; otherwise `shape` is undefined and the client uses server pagination. Shapes register in the sync shape registry with server-set `where`.
- Explain guard: in tests, `EXPLAIN (FORMAT JSON)` must show index usage for sorted queries over the 100k-row fixture; sequential scans over `record` fail the test.
- `useViewQuery` returns `{ pages, fetchNextPage, groups, aggregates, isStale }`, invalidates on `record` mutations via the Electric change stream when a shape exists, else on mutation success.

**Definition of done**

- Unit tests per op per type (table-driven) and golden SQL snapshots for the 10 fixture views.
- Integration test against Postgres with a 100k-row seed: p95 under 150 ms for filtered, sorted, paginated queries; measured in CI with `vitest bench` and recorded in the PR.
- Cursor tamper test returns `VALIDATION`.
- Cross-tenant test from `data-layer/rls-tenancy` extended with view queries.
- `docs/views/query-compiler.md` explains compile pipeline, cursor format, shape eligibility.
- CHANGELOG entry; Linear comment with benchmark table and link to the docs page.

**Edge cases**

- Sort on a field with all nulls: `nullsLast` respected, keyset cursor handles null boundaries.
- Filtering a relation field by a record the actor cannot see: `EXISTS` inherits RLS so the row simply does not match.
- Group key with 10k distinct values: `views.groups` paginates groups (`limit` 100) and the UI shows "load more groups".
- Field type changed after a cursor was issued: cursor version mismatch returns `CONFLICT`, client restarts from page one.
- Aggregate `sum` on currency fields with mixed currencies: return per-currency map, never a blind sum.
- Timezone differing between actor and tenant for "today": actor timezone wins; documented.

**Dependencies**

- `tables/view-model-spec` (types); `data-layer/api-layer` (oRPC conventions, error codes); `data-layer/local-first-sync` (shape registry); `identity/rbac-abac` (`toPredicate`); `data-layer/rls-tenancy`.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Reviewer and Security Auditor for injection and cursor forgery) plus Forge (Schema Wright) on index strategy.

**Size**

L: broad op-by-type matrix plus performance work; expect two sessions.
