---
identifier: "PAP-382"
title: "Lexer, Pratt parser, AST, type checker and the defineFunction catalogue"
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
blockedBy: ["PAP-162", "PAP-164"]
blocks: ["PAP-383"]
key: "tables/formula/parser-typecheck"
url: "https://linear.app/paperos/issue/PAP-382/lexer-pratt-parser-ast-type-checker-and-the-definefunction-catalogue"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:42.311Z"
---

# PAP-382: Lexer, Pratt parser, AST, type checker and the defineFunction catalogue

**Goal**

Parse Airtable and Notion style formulas into a typed AST with positioned diagnostics and a metadata-driven function catalogue.

**Scope**

In: `formula/{lexer,parser,ast,types,check,functions/index}.ts`; `defineFunction`; catalogue entries (signatures only) for 80+ functions from PAP-162. Out: implementations, editor, SQL (siblings).

**Spec**

* Grammar per the parent; `{Field}` rewritten to `@fld_<id>` at save; iterative parser with depth limit 200.
* Types `text | number | boolean | date | array<T> | null | error`; coercion rules; `checkType(ast, fields)`.
* `defineFunction({ name, aliases, params, returns, pure, volatile? })` with variadic params.

**Interface contract**

Provides: `parse`, `checkType`, `AST` types, `functions` catalogue, `defineFunction`. Consumes: field types (PAP-164), inventory (PAP-162).

**Definition of done**

* 200-expression golden corpus; `fast-check` fuzz for crash-freedom; diagnostics snapshots.

**Test plan**

* Unit: corpus, type errors with positions, alias resolution, depth limit.

**Demo**

Run `pnpm tsx scripts/formula-check.ts 'IF({Amount} > 1, "a", 2)'` and read the type diagnostic.

**Edge cases**

* Unicode field names; unterminated strings; deleted field reference yields `#REF` marker.

**Dependencies**

PAP-164, PAP-162 (hard). Blocks siblings.

**Agent**

Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.
