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
children: ["PAP-382", "PAP-383", "PAP-384"]
blockedBy: ["PAP-162", "PAP-164", "PAP-340"]
blocks: []
key: "tables/formula-engine"
url: "https://linear.app/paperos/issue/PAP-171/build-a-formula-engine-compatible-with-common-airtable-and-notion"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:14.275Z"
model: null
effort: null
---

# PAP-171: Build a formula engine compatible with common Airtable and Notion functions

**Goal**

Build the formula engine so `formula` fields compute values users already know how to write: Airtable and Notion compatible syntax, static type checking, a TypeScript evaluator for editors and previews, and SQL compilation for the subset that can run inside PAP-163 so formulas filter, sort and aggregate server-side. Umbrella for three children.

**Scope**

Children (M each, same milestone, Backlog):

* PAP-382 Lexer, Pratt parser, AST, type checker, `defineFunction` metadata and the function catalogue from `formula-functions.csv`.
* PAP-383 TypeScript evaluator with all function implementations, CodeMirror 6 editor with autocomplete, signature help and live preview.
* PAP-384 SQL compiler, `formula_cache` fallback job, dependency graph and cycle detection.

Out: cell-level spreadsheet formulas, user-defined functions, cross-dataset references except through relations.

**Spec**

Decisions binding all children:

* Grammar: `IF({Status} = "Done", 1, 0)`, `{Field}` references, `&`, arithmetic, comparisons, `AND/OR/NOT` and `&&/||/!`, string escapes, `//` comments; references rewritten to `@fld_<id>` at save so renames are safe.
* Types `text | number | boolean | date | array<T> | null | error`; coercions only number to text in `&` and parseable text to number in arithmetic; diagnostics carry positions.
* `defineFunction({ name, aliases, params, returns, ts, sql?, pure, volatile? })`; `NOW()` and `TODAY()` volatile, excluded from indexes; date functions take the actor timezone from context.
* `compile(ast) => SQL | Unsupported`; unsupported formulas materialise into `record.formula_cache jsonb` refreshed in batches of 500 by a PAP-43 job when dependencies change.
* Errors render `#ERROR` with hover detail; division by zero is an error; `IFERROR` supported.

**Interface contract**

Provides: `parse(src) => AST`, `checkType(ast, fields) => { resultType, diagnostics }`, `evaluate(ast, record, ctx)`, `compile(ast) => SQL | Unsupported`, `functions` metadata, `<FormulaEditor field fields sampleRecord />`, `dependencyGraph(dataset)`. Consumes: field types and `formula` storage type (PAP-164), compiler integration point `compiler/ops/formula.ts` (PAP-163), function inventory (PAP-162), jobs (PAP-43), CodeMirror from the libraries registry. Consumed by PAP-169 conditional logic and PAP-174 template expressions (shared expression subset).

**Definition of done**

* All three children Done.
* Function coverage: at least 80 functions; every SQL-capable function has a TS versus SQL parity test on a 1,000-record fixture.
* Storybook editor story; screenshots at 375, 1024, 1920 in three themes.
* `docs/views/formulas.md` generated from metadata; parity CSV row updated; CHANGELOG; Linear comment with coverage count and the unsupported-in-SQL list.

**Test plan**

Umbrella `formula.e2e.test.ts`: 200-expression golden corpus parsed, type-checked and evaluated against Airtable-documented answers; for each SQL-capable function run the formula through `views.query` filter and sort and compare with `evaluate`; edit a formula that depends on a lookup and assert `formula_cache` refresh within one job cycle; `fast-check` fuzz for parser crash-freedom (10k cases); Playwright: type a formula with autocomplete, see a diagnostic, fix it, see the preview.

**Demo**

Reviewer adds a formula field `IF({Amount} > 1000, "Big", "Small") & " deal"` in the editor with autocomplete, sees the live preview on a sample row, saves, and filters the grid by the formula result server-side. Under two minutes.

**Edge cases**

* Deleted field reference: `#REF` with a fix-it action.
* `LEN` and `MID` count code points, matching Airtable.
* Date arithmetic across DST uses timezone-aware functions.
* Nesting depth limited to 200 with a clear error.
* `TODAY()` in a public view uses the tenant timezone.

**Dependencies**

PAP-164 (hard), PAP-163 (hard), PAP-162 (hard, inventory), PAP-43 (cache job). Soft consumer: PAP-174.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Edge Case Hunter with adversarial expressions, Security Auditor on SQL compilation).

**Size**

L, split into three M children; ship the TS evaluator behind a flag first.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [tables](<https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
