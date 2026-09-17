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
blocks: ["PAP-59", "PAP-116", "PAP-119", "PAP-163", "PAP-166", "PAP-174", "PAP-195", "PAP-227", "PAP-311", "PAP-335", "PAP-388"]
key: "gap/data-layer/filter-grammar"
url: "https://linear.app/paperos/issue/PAP-279/specify-the-shared-filter-and-condition-grammar-packagescorefilter-one"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:43:04.181Z"
model: "claude-fable-5-1"
effort: "high"
---

# PAP-279: Specify the shared filter and condition grammar (`packages/core/filter`): one Zod FilterTree with SQL and in-memory evaluators

**Goal**

Define the single filter and condition grammar that permissions `Condition` (PAP-59), the view model `FilterGroup` (PAP-161), the spec data section (PAP-119, currently a copy with a TODO), the filter builder (PAP-166), segments (PAP-195) and automations (PAP-174) all import instead of redefining. One Zod schema, one SQL compiler for Drizzle, one in-memory evaluator, proven equivalent by property tests.

**Read first.** Read before coding: [Blueprint](<https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1>) → [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) → your project's `Contract` section (Linear project content) → your character sheet ([Roster](<https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3>)) → [Execution Schedule](<https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795>) for your start day and the branch-start rule. Contracts §1 (the `FilterTree` bullet: permissions `Condition`, view `FilterGroup`, spec data section, segments and automations are aliases of this type) and §6 row `FilterTree` list every consumer; §4 fixes the list input `filter?: FilterTree`.

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

* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (the `FilterTree` bullet: permissions `Condition`, view `FilterGroup`, the spec data section, segments and automations are aliases of this one type; Zod 4 schema with generated JSON Schema); §4 (list procedures take `filter?: FilterTree`); §6 row "`FilterTree`" (provider: this issue; consumers PAP-59, PAP-161, PAP-119, PAP-163, PAP-166, PAP-172, PAP-174, PAP-195, PAP-268). This issue is the provider: any operator or shape change is an ADR.

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

None hard. Ready now. This is a pure Zod/TypeScript package with its own `package.json` under `packages/core/src/filter/`; it does not need the monorepo scaffold (PAP-13) to start. If PAP-13 is not merged when you begin, start from the PAP-13 PR branch (`feat/PAP-13`) or a bare `pnpm` workspace with the same layout and rebase when PAP-13 lands. The relation `PAP-13 blocks PAP-279` was removed on 2026-09-17 (FIX-2) for this reason; do not re-add it. Soft: PAP-42 for the PGlite property test only (if PAP-42 is absent, add `@electric-sql/pglite` as a dev dependency of this package and run the test in-process). Blocks (hard, relations exist): PAP-59, PAP-116, PAP-119, PAP-163, PAP-166, PAP-174, PAP-195. Soft consumer: PAP-161 imports the draft `FilterTree` from this issue's PR branch and is not blocked by it, so open the PR early and keep `FilterTree`, `filterTreeSchema` and `FieldSchema` exported from the first commit.

**Agent**

Specified and built by Forge (Platform Engineer) with Nova. Reviewed by Sentinel (Code Reviewer).

**Size**

M
