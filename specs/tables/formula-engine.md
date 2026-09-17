---
identifier: "PAP-171"
title: "Build a formula engine compatible with common Airtable and Notion functions"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-162", "PAP-164"]
blocks: []
key: "tables/formula-engine"
url: "https://linear.app/paperos/issue/PAP-171/build-a-formula-engine-compatible-with-common-airtable-and-notion"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-171: Build a formula engine compatible with common Airtable and Notion functions

**Goal**

Build a formula engine so `formula` fields compute values users already know how to write, compatible with the most-used Airtable and Notion functions, with static type checking, an evaluator in TypeScript for editors and previews, and SQL compilation for the subset that can run inside the query compiler so formulas can be filtered, sorted and aggregated server-side.

**Scope**

In:
- `packages/views/src/formula/`: lexer, Pratt parser to AST, type checker, TS evaluator, SQL compiler, function library, error model, editor component with autocomplete and inline diagnostics.
- Function coverage from `docs/views/formula-functions.csv` (`tables/feature-parity-audit`): at least 80 functions across text, number, logical, date, array and record categories, with Notion-style aliases (`prop("Name")`, `dateBetween`, `formatDate`, `empty`).
- Dependency graph for computed fields (formula referencing lookup/rollup/formula) with cycle detection.

Out: cell-level spreadsheet formulas, user-defined functions, formulas referencing other datasets except through relation fields.

**Spec**

- Grammar: Airtable-style `IF({Status} = "Done", 1, 0)` with `{Field Name}` references, `&` concatenation, `+ - * / %`, comparisons, `AND/OR/NOT` as functions and `&&/||/!` as operators (Notion style), string escapes, comments `//`. Field references resolve by field id at save time (`{Field}` rewritten to `@fld_123` in stored AST) so renames are safe.
- Types: `text | number | boolean | date | array<T> | null | error`; `checkType(ast, fields) => { resultType, diagnostics }`; implicit coercions only number→text in `&` and text→number in arithmetic when parseable; otherwise diagnostics with positions.
- Functions declared via `defineFunction({ name, aliases, params: [{ name, type, variadic? }], returns, ts: impl, sql?: (args) => SQL, pure: true })`; date functions take the actor timezone from context; `NOW()`/`TODAY()` are marked volatile and excluded from SQL indexes.
- Evaluation: `evaluate(ast, record, ctx)` used for editor previews, form conditional logic and client display; results cached per record version.
- SQL: `compile(ast) => SQL | Unsupported`; supported functions cover text, math, logic and most date functions using Postgres equivalents (`date_trunc`, `age`, `to_char` with a format-token translator); `REGEX_*` map to `regexp_*`; arrays via jsonb functions. Unsupported formulas fall back to a materialised column: a `formula_cache` jsonb column on `record` refreshed by a trigger-free job when dependencies change (`records.update` enqueues affected ids; `p-queue` worker recomputes in batches of 500), so filtering and sorting always work, slightly stale for the unsupported subset.
- Error values render as `#ERROR` with hover detail; division by zero returns error, not Infinity; `IFERROR` supported.
- Editor: CodeMirror 6 with a custom language mode, field and function autocomplete, signature help, live result preview on a sample record, and a function reference drawer generated from `defineFunction` metadata.
- Dependency graph stored per dataset; `convertFieldType` and field deletion consult it and block or warn.

**Definition of done**

- Vitest: parser golden tests (200+ expressions), type checker cases, evaluator vs Airtable-documented examples, SQL compiler parity tests asserting TS and SQL results match on a 1,000-record fixture for every SQL-capable function.
- Fuzz test with `fast-check` for parser crash-freedom.
- Storybook story for the editor tagged `visual`; screenshots at 375, 1024, 1920 in three themes.
- Function reference published to `docs/views/formulas.md` from metadata; coverage row updated in the parity CSV.
- CHANGELOG entry; Linear comment with function coverage count and unsupported-in-SQL list.

**Edge cases**

- Formula referencing a deleted field: field stays, shows `#REF` with a fix-it action.
- Unicode and emoji in `LEN` and `MID`: count code points, matching Airtable.
- Date arithmetic across DST: use timezone-aware functions; test fixtures cover it.
- Deep nesting (500 nested IFs): parser is iterative or depth-limited to 200 with a clear error.
- Formula producing an array (lookup values): aggregations offered are count/unique/join.
- Timezone of `TODAY()` in a shared public view: tenant timezone, not viewer.

**Dependencies**

- `tables/field-types` (formula type, lookup/rollup), `tables/query-compiler` (integration point for `compile`), `tables/feature-parity-audit` (function inventory).

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Reviewer, Edge Case Hunter with adversarial expressions) and Security Auditor on SQL compilation.

**Size**

L: language implementation plus dual execution; two sessions minimum, ship TS evaluator first behind a flag.
