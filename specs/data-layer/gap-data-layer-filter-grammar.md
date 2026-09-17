---
identifier: "PAP-279"
title: "Specify the shared filter and condition grammar (`packages/core/filter`): one Zod FilterTree with SQL and in-memory evaluators"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-116", "PAP-119", "PAP-163", "PAP-166", "PAP-174", "PAP-195", "PAP-227", "PAP-59"]
key: "gap/data-layer/filter-grammar"
url: "https://linear.app/paperos/issue/PAP-279/specify-the-shared-filter-and-condition-grammar-packagescorefilter-one"
source: "Linear snapshot 2026-09-17T06:03Z (round-2 issue)"
---

# PAP-279: Specify the shared filter and condition grammar (`packages/core/filter`): one Zod FilterTree with SQL and in-memory evaluators

**Goal**

Define the single filter and condition grammar that permissions `Condition` (PAP-59), the view model `FilterGroup` (PAP-161), the spec data section (PAP-119, currently a copy with a TODO), the filter builder (PAP-166), segments (PAP-195) and automations (PAP-174) all import instead of redefining. One Zod schema, one SQL compiler for Drizzle, one in-memory evaluator, proven equivalent by property tests.

**Scope**

In:

* `packages/core/src/filter/`: `FilterTree = Group | Condition`; `Group = { op: 'and'|'or'|'not', children }`; `Condition = { field, operator, value }` with operators per field type (`eq`, `neq`, `in`, `nin`, `lt`, `lte`, `gt`, `gte`, `contains`, `startsWith`, `isNull`, `isNotNull`, `between`, `has` for arrays, `matches` for jsonb path).
* Field typing via a `FieldSchema` map so `value` is validated per operator; variables `{ $var: 'principal.id' }` resolved at evaluation.
* `toSql(tree, table, ctx)` returning a Drizzle `SQL` fragment; `evaluate(tree, row, ctx)` in memory; `normalize(tree)` canonical form; `explain(tree)` human text.
* Property-based equivalence test between `toSql` on PGlite and `evaluate`.

Out: UI (PAP-166), full-text search operators (PAP-39), aggregation.

**Spec**

* Max depth 8, max 200 conditions; validation errors name the path.
* Case-insensitive text operators use `citext` or `ILIKE`; documented per type.
* Null semantics follow SQL (three-valued) in both evaluators; tests cover it.
* Serialised form is JSON; a compact URL encoding `encodeFilter`/`decodeFilter` for view links (PAP-172).
* Versioned `v: 1`; migrations for future versions.

**Interface contract**

Provides (from `@paperos/core/filter`): `FilterTree`, `filterTreeSchema`, `toSql`, `evaluate`, `normalize`, `explain`, `encodeFilter`, `decodeFilter`, `FieldSchema`, `Variables`. Consumed by PAP-59 (`Condition` becomes an alias), PAP-161 (`FilterGroup` alias), PAP-119, PAP-163 (compiler), PAP-166, PAP-172, PAP-174, PAP-195, PAP-35 list inputs. Consumes: Drizzle `sql` helper (PAP-32) and PGlite for tests (PAP-42); no runtime dependency on the database.

**Definition of done**

* Package merged with schema, both evaluators and 500-case property test green on PGlite.
* PAP-59, PAP-161 and PAP-119 owners comment approval and their specs reference this package.
* `docs/platform/filter.md` with the operator table per field type; ADR; CHANGELOG; Linear comment.

**Test plan**

* Unit: schema accepts and rejects fixtures (depth, count, operator versus type, variables); `normalize` idempotent; `explain` snapshots.
* Property: fast-check generates trees and rows; `evaluate` equals `toSql` result on PGlite for 500 cases including nulls.
* Type: `FieldSchema` narrows `value` types (`expectTypeOf`).
* Perf: `toSql` under 1 ms for a 50-condition tree.

**Demo**

Reviewer runs `pnpm --filter core test filter` and watches the property test pass, then `pnpm tsx examples/filter.ts` printing a tree, its SQL and its explanation in English. Under a minute.

**Edge cases**

* Unknown field: validation error with suggestions.
* `in` with empty list: always false, documented.
* jsonb `matches` on a non-jsonb field: rejected at validation.
* Variables unresolved at evaluation: throw, never default.

**Dependencies**

None hard (pure package on PAP-13 layout); PAP-42 for the PGlite test only. Ready now. Blocks PAP-59, PAP-161, PAP-119, PAP-166, PAP-174, PAP-195.

**Agent**

Specified and built by Forge (Platform Engineer) with Nova. Reviewed by Sentinel (Code Reviewer).

**Size**

M
