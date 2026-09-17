---
key: "child/PAP-199/2"
title: "Type inference, mapping wizard UI and run history with per-item drill-down and rollback button"
project: "migration"
parent: "PAP-199"
phase: "P1"
type: "Build"
priority: 2
size: "M"
surfaces: ["Staff", "Developer"]
milestone: "Import framework and CSV"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent5/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6"
status: "pending"
---

# Type inference, mapping wizard UI and run history with per-item drill-down and rollback button

**Goal**

Give staff a wizard that connects a source, proposes a mapping from inferred types with sample values, shows the dry-run report, commits with live progress and lists run history with drill-down and a guarded rollback button, at every breakpoint and keyboard-operable.

**Scope**

In: `src/infer.ts` sampling 1,000 values per field and scoring PAP-164 types (number, currency, date, boolean, email, phone, url, select under 5 percent distinct, multi-select on delimiters, relation on key match) with confidence and warnings; routes `_app/settings/import/` (connect, collections, map fields, dedupe key, relation strategy, report, commit) and `_app/settings/import/runs` grid (PAP-165, list fallback) with item drill-down and rollback confirmation showing counts; JSON mapping export/import.

Out: connector-specific steps (each importer adds a step component via `registerWizardStep`).

**Spec**

* Mapping table is a real `role=grid` with roving focus; inferred type shown as a select with confidence badge; sample values column truncates at 40 characters.
* Progress uses PAP-143 shapes on `import_run.stats`, polling every 2 s as fallback.
* Rollback button disabled while a run is active or when the actor lacks `import.rollback`.

**Interface contract**

Provides: `inferTypes(samples)`, `registerWizardStep(connector, step)`, routes above, components `MappingTable`, `RunReport`, `RunHistory` exported from `packages/import/ui`. Consumes: children 1 and 2, PAP-67 primitives, PAP-71 data display, PAP-165 grid. Importers PAP-200 to PAP-207 plug steps in; PAP-208 renders `RunReport` inside chat cards.

**Definition of done**

* Wizard completes end to end with the fixture connector; history shows the run and rollback works from the UI.
* axe clean on every step; mapping table fully keyboard-operable.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for mapping, report and history.

**Test plan**

* Vitest: inference on 15 fixture columns (dates in 6 formats, currencies, selects, relations), confidence thresholds.
* Playwright: full wizard with a deliberate error, commit, drill-down, rollback; keyboard-only run of the mapping step; visual baselines at the seven widths in both themes.
* axe on each step.

**Demo**

Reviewer opens Settings > Import, picks the fixture connector, accepts inferred types except one they change, reads the dry-run report, commits, opens Run history and clicks Rollback. Under two minutes.

**Edge cases**

* 200 columns: mapping table virtualizes rows; sticky header.
* Inference disagrees with an existing target field type: warning with a transform suggestion.
* Narrow width 320: wizard steps stack, mapping shown as cards.

**Dependencies**

Children 1 and 2 (hard), PAP-67, PAP-71, PAP-165 (soft: list fallback). Blocks PAP-200 to PAP-208 UI steps.

**Agent**

Built by Scout (Import Mapper) with Iris (Component Crafter). Reviewed by Sentinel (Visual Inspector, Code Reviewer).

**Size**

M
