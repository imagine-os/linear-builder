---
identifier: "PAP-761"
title: "Import census: `pnpm lib census` records which modules and files import each adopted library, refreshes migration-cost estimates and adds a swap-impact column to the registry"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Registry live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-216", "PAP-439"]
blocks: []
key: "r4/libraries/import-census"
url: "https://linear.app/paperos/issue/PAP-761/import-census-pnpm-lib-census-records-which-modules-and-files-import"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:39.515Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-761: Import census: `pnpm lib census` records which modules and files import each adopted library, refreshes migration-cost estimates and adds a swap-impact column to the registry

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

The module system exists so we can swap things. Swapping a library is the same question one level down: who imports `@xyflow/react`, from how many files, through which modules? PAP-216 records `usedBy` at the package level from the lockfile; the dependency map (PAP-439) walks module imports. Join them into a census that makes the registry's `migrationCostHours` a number with evidence.

**Scope**

In: `pnpm lib census` in `tools/libraries/census.ts` walking the import graph PAP-439 already builds (dependency-cruiser JSON) plus a `ts-morph` pass for named imports, writing `docs/.generated/library-census.json` `{ library: { modules[], files, namedImports: { name: count }, deepImports[], firstSeen } }`; registry build merges `census` into each entry and computes `swapImpact: low|medium|high` (files and modules thresholds) and a refreshed `migrationCostHours` estimate (`files * 0.25 + modules * 2`, overridable); registry page column and filter; `docs/libraries/census.md`. Out: performing swaps, the dependency map itself.

**Spec**

* Named-import counts show which API surface we depend on (`useReactFlow: 14, Background: 3`), the input for a swap ADR's 'what we actually use' section and for PAP-757 `Import` sections.
* Deep imports (`lodash/cloneDeep`, `@tiptap/core/dist/x`) are listed separately; more than three deep imports raise `swapImpact` one level and add a note suggestion.
* `firstSeen` from git blame of the first import line, so the census can say a library crept in without a registry entry (fed to PAP-216's check as a warning).
* Runs in `pnpm lib registry build` in under 20 s on the template; committed output drift-checked by the existing `registry-drift` job.
* Module boundary: census only reports; if a library appears in two modules that should share it through a contract, the note is a hint for PAP-439's owners, not an error here.

**Interface contract**

Provides: `library-census.json`, `swapImpact`, refreshed `migrationCostHours`, registry column. Consumes: dependency-cruiser output and module map (PAP-439), registry build (PAP-216), `ts-morph`. Consumed by: PAP-442 swap playbook (impact input), PAP-757, PAP-760, ADRs proposing replacements, PAP-306 re-audit.

**Definition of done**

* Census generated for the template; three known libraries show plausible counts (spot check by reviewer); registry page shows `swapImpact` with a filter; drift job covers the output.
* `docs/libraries/census.md`; CHANGELOG entry; comment on PAP-442.

**Test plan**

* Unit: named import extraction fixtures (default, namespace, type-only, re-export), impact thresholds, cost formula and override.
* Integration: run on the template repo in CI within budget.
* E2E: none.

**Demo**

Run `pnpm lib census`, open the JSON for `@tanstack/react-table`, read the named imports, then open the registry filtered to `swapImpact: high`. Under one minute.

**Edge cases**

* Library imported only in `generated/**`: counted separately as `generated` so a codegen change fixes it, not a migration.
* Dynamic `import()`: counted with the literal specifier; non-literal specifiers listed as `unknown`.
* Type-only imports: counted, flagged `typeOnly` (cheap to swap).

**Dependencies**

Hard: PAP-216, PAP-439. Soft: PAP-442, PAP-306.

**Agent**

Builder: Scout (Library Evaluator). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/libraries/dependency-health-page` = PAP-760, `r4/libraries/library-usage-notes` = PAP-757.
