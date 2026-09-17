---
identifier: "PAP-384"
title: "SQL compiler, formula_cache fallback job and the dependency graph"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: "PAP-171"
children: []
blockedBy: ["PAP-383"]
blocks: []
key: "tables/formula/sql-cache"
url: "https://linear.app/paperos/issue/PAP-384/sql-compiler-formula-cache-fallback-job-and-the-dependency-graph"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:42.311Z"
---

# PAP-384: SQL compiler, formula_cache fallback job and the dependency graph

**Goal**

Run formulas server-side where Postgres can, and materialise the rest so every formula field can be filtered, sorted and aggregated.

**Scope**

In: `formula/{sql,cache,graph}.ts`, `compiler/ops/formula.ts` integration in PAP-163, refresh job. Out: UI.

**Spec**

* `compile(ast) => SQL | Unsupported`; text, maths, logic and most date functions map to Postgres (`date_trunc`, `to_char` with a token translator, `regexp_*`, jsonb array functions); volatile functions excluded from indexes.
* Unsupported formulas write `record.formula_cache jsonb` via a PAP-43 job in batches of 500 when dependencies change; `records.update` enqueues affected ids.
* Dependency graph per dataset with cycle detection; `convertFieldType` and deletion consult it.

**Interface contract**

Provides: `compile`, `dependencyGraph`, `refreshFormulaCache(job)`, `formula` op module for PAP-163. Consumes: parser child, evaluator child (parity tests), PAP-163, PAP-43.

**Definition of done**

* TS versus SQL parity on a 1,000-record fixture for every SQL-capable function; cache refresh within one job cycle; unsupported list published.

**Test plan**

* Unit: compile snapshots; graph cycles.
* Integration: filter and sort by formula through `views.query`; stale cache refresh timing.

**Demo**

Filter the grid by a formula result and run `pnpm tsx scripts/formula-sql.ts` to print the generated SQL.

**Edge cases**

* Formula referencing a rollup of a formula resolves in dependency order; 500 nested IFs compile or fall back gracefully.

**Dependencies**

Parser and evaluator children (hard), PAP-163, PAP-43.

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor on SQL).

**Size**

M: one session.
