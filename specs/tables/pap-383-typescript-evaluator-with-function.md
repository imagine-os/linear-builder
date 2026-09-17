---
identifier: "PAP-383"
title: "TypeScript evaluator with function implementations and the CodeMirror formula editor"
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
blockedBy: ["PAP-382"]
blocks: ["PAP-384"]
key: "tables/formula/evaluator-editor"
url: "https://linear.app/paperos/issue/PAP-383/typescript-evaluator-with-function-implementations-and-the-codemirror"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:42.311Z"
---

# PAP-383: TypeScript evaluator with function implementations and the CodeMirror formula editor

**Goal**

Evaluate formulas in TypeScript for previews, forms and client display, and give users an editor with autocomplete, signature help and live results.

**Scope**

In: `formula/{evaluate,functions/*}.ts`, `FormulaEditor` (CodeMirror 6 language mode), function reference drawer. Out: SQL (sibling).

**Spec**

* `evaluate(ast, record, ctx)` with actor timezone, cached per record version; `#ERROR` values with hover detail; `IFERROR`.
* Implementations for all catalogue functions; `LEN` and `MID` count code points.
* Editor: field and function autocomplete, signature help, inline diagnostics, live preview on a sample record, reference drawer generated from metadata.

**Interface contract**

Provides: `evaluate`, `<FormulaEditor field fields sampleRecord />`, `functionDocs()`. Consumes: parser child, editor libraries from the registry (PAP-215).

**Definition of done**

* Evaluator matches Airtable-documented examples; editor story screenshotted at 375, 1024, 1920; axe clean.

**Test plan**

* Unit: every function against documented examples; DST date fixtures.
* E2E: type with autocomplete, see a diagnostic, fix, see the preview.

**Demo**

Write `DATETIME_DIFF({Due}, TODAY(), 'days')` in the editor and watch the preview.

**Edge cases**

* Division by zero is an error; emoji length; `TODAY()` in tenant timezone for public views.

**Dependencies**

Parser child (hard).

**Agent**

Builder: Nova with Iris on the editor. Reviewer: Sentinel.

**Size**

M: function implementations are many but small.
