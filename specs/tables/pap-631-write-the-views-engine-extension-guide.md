---
identifier: "PAP-631"
title: "Write the views engine extension guide: adding a field type, a view kind, a filter operator, an aggregate and a dashboard block, with a checklist per contract port"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Docs"
priority: 2
surfaces: ["Developer"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-338", "PAP-483", "PAP-614"]
blocks: ["PAP-489"]
key: "r4/tables/extension-guide-docs"
url: "https://linear.app/paperos/issue/PAP-631/write-the-views-engine-extension-guide-adding-a-field-type-a-view-kind"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:20.253Z"
model: "claude-haiku-4-5"
effort: "low"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-631: Write the views engine extension guide: adding a field type, a view kind, a filter operator, an aggregate and a dashboard block, with a checklist per contract port

**Model / Effort:** Haiku 4.5 (`claude-haiku-4-5-20251001`) / low — Docs S

**Goal**

A cold builder session asked to add a Monday-style "World clock" field or a new view kind must not reverse-engineer six specs. Write the one guide that maps each extension point of `@paperos/contract-tables` to files, registration calls, tests and conformance fixtures, and index the `docs/views/` folder.

**Scope**

In: `docs/views/README.md` (index of every `docs/views/*.md` with one line each); `docs/views/extending.md` with five walkthroughs; `docs/views/checklists.md` (per-port checklist: field type, view kind, filter op, aggregate, block, automation action); templates under `packages/views/templates/{field-type,view-kind}.ts` used by a `pnpm views:new field <name>` generator (plop or a 60-line script).

Out: API reference (typedoc from PAP-445), guideline prose (PAP-76), parity CSV (PAP-162).

**Spec**

* Each walkthrough is executable: file paths, the `defineFieldType` or `registerViewKind` call, the tests to add (parse/format, ops oracle, story, conformance fixture in `packages/contracts/tables/fixtures/`), the docs row to update and the parity CSV row; ends with the commands to run (`pnpm --filter views test`, `pnpm conformance:tables`).
* Checklists are Markdown task lists a PR can paste; each item names the failing check if skipped (for example "missing story → `umbrella.test.ts` fails").
* `pnpm views:new field <name>` scaffolds `fields/<name>.ts`, a story, a test and a fixture from the templates; `pnpm views:new kind <name>` scaffolds `views/<name>/{View,register,options}.tsx`.
* The index lists documents in reading order and marks which contract port each covers, matching the port list in PAP-483.
* Under 1,200 words per page; every code block type-checks via `pnpm docs:check-snippets` (extracts TS blocks and compiles them against the workspace).

**Interface contract**

Provides: `docs/views/README.md`, `docs/views/extending.md`, `docs/views/checklists.md`, generator `pnpm views:new`, snippet check script. Consumes: contract port list (PAP-483), registry API (PAP-614), field framework (PAP-338), conformance fixture layout (PAP-486), docs engine rendering (PAP-128, soft). Consumed by PAP-489 (module page links), PAP-105 page-from-spec skill, every future tables session.

**Definition of done**

* Three docs merged and rendering in the docs engine or Storybook fallback; generator produces a compiling field type and view kind that pass their scaffolded tests.
* Snippet check green in CI; CHANGELOG; Linear comment with links.

**Test plan**

* Unit: generator output compiles and its tests run; snippet extractor handles fenced blocks with `ts` and `tsx`.
* Dry run: a fresh session follows `extending.md` to add a `year` field type in under 30 minutes (timed, recorded in the PR).
* E2E: none (docs).

**Demo**

Reviewer runs `pnpm views:new field year`, follows the checklist, runs the tests and sees the new type in Storybook. Under two minutes.

**Edge cases**

* Guide drifts from code: snippet check fails the PR that changed the API.
* Generator name collides with an existing type: refuses.
* Docs engine not yet live: Storybook MDX fallback under `Guides/`.

**Dependencies**

PAP-483 (hard, port list), PAP-614 (hard), PAP-338 (hard). Soft: PAP-486, PAP-128. Blocks PAP-489 (module page links to the guide).

**Agent**

Builder: Quill (Page Spec Writer) with Nova reviewing accuracy. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/tables/view-renderer-registry-and-host` = PAP-614.
