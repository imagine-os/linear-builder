---
identifier: "PAP-626"
title: "Conditional formatting: row and cell colour rules from FilterTree conditions, select-colour rows and progress bars in cells across grid, kanban, calendar and gallery"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "All view types"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-343", "PAP-617"]
blocks: []
key: "r4/tables/conditional-formatting"
url: "https://linear.app/paperos/issue/PAP-626/conditional-formatting-row-and-cell-colour-rules-from-filtertree"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:19.039Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-626: Conditional formatting: row and cell colour rules from FilterTree conditions, select-colour rows and progress bars in cells across grid, kanban, calendar and gallery

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Airtable record colouring, Smartsheet and Excel conditional formatting, ClickUp status colours and Monday colour columns all answer "which rows need my attention" at a glance. Add rule-based formatting to `ViewSpec` that every kind renders consistently.

**Scope**

In: `ViewSpec.formats: { id, name, when: FilterTree, style: { rowColor?, cellColors?: Record<fieldId, tokenName>, bold?, strike?, icon? }, order }[]` plus `colorBy?: { fieldId }` shortcut; `FormatRulesPanel` in the toolbar; `useRowFormat(record)` hook evaluated client-side with PAP-279's in-memory evaluator; number and percent cell option `showBar`.

Out: formatting in exports (PAP-625 may read `rowColor`), per-user formats, formulas returning colours.

**Spec**

* Rules evaluate top to bottom; the first matching rule sets `rowColor`, later rules may still add `cellColors`; colours are semantic token names (`accent-100`, `warning-100`, `danger-100`, `success-100`, `neutral-100`, `info-100`) so themes and high contrast stay correct; never raw hex.
* `colorBy: { fieldId }` on a select field tints rows with the option colour (Airtable-style); kanban cards, calendar events, gallery card borders and grid rows read the same `useRowFormat` result; timeline and Gantt bars use `rowColor` as the bar colour.
* Evaluation is client-side per visible row (max 200 rules, memoised per record version); rules referencing `currentUser` or relative dates re-evaluate on a 60 s ticker.
* `showBar` on number and percent fields draws a `MiniBar` behind the value scaled to `options.max` or the column max in view (`AggregateFooter` `max`); respects `prefers-reduced-motion` and forced colours (pattern fill).
* Accessibility: colour never alone; a rule may set `icon` (from PAP-68) and the row gets `aria-description` with the rule name; screen reader announces "Overdue" from the rule name.
* Panel: `FilterBuilder` for `when`, colour swatches, preview count via `views.count`, drag reorder (PAP-329); commands `view.format.add`.

**Interface contract**

Provides: `formats` and `colorBy` schema additions (PAP-161 minor bump, `migrateViewSpec` step), `useRowFormat`, `<FormatRulesPanel />`, `MiniBar` usage contract, token-name palette `formatColors`. Consumes: `FilterBuilder` and evaluator (PAP-617, PAP-279), grid row and cell renderers (PAP-343), select option colours (PAP-339), tokens (PAP-66), icons (PAP-68), `views.count` (PAP-337). Consumed by PAP-167, PAP-344, PAP-345, PAP-346, gallery (PAP-619) through the hook.

**Definition of done**

* Schema bump merged with migration test; grid and kanban render formats; stories at 375, 1024, 1920 in light, dark and high contrast (patterns visible); axe clean including `aria-description`.
* `docs/views/conditional-formatting.md`; CHANGELOG; Linear comment with screenshots.

**Test plan**

* Unit: rule ordering and first-match semantics; token-name validation rejects hex; memoisation by record version; `showBar` scaling with negative and null values.
* Integration: 200 rules over 1,000 visible rows evaluate under 16 ms per frame (bench).
* E2E: add "Due before today and Status is not Done → danger" in `/demo/grid`, see rows tint, switch to kanban and calendar and see the same records coloured, toggle high contrast and see patterns.

**Demo**

Reviewer adds an overdue rule and a `colorBy` status shortcut, scrolls the grid, then opens the calendar where the same events are red. Under two minutes.

**Edge cases**

* Rule references a deleted field: greyed with "field deleted", skipped at evaluation.
* Conflicting row colours from two rules: first wins, panel shows the shadowing hint.
* Print route: colours kept, patterns forced.
* Public views: formats apply, rule names hidden if they reference hidden fields.

**Dependencies**

PAP-617 (hard), PAP-343 (hard). Soft: PAP-339, PAP-68, PAP-329. Blocks nothing hard; the time and kanban views adopt the hook when it lands.

**Agent**

Builder: Nova (Views Engineer) with Iris on palette. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/tables/filter-builder-component` = PAP-617, `r4/tables/gallery-and-list-views` = PAP-619, `r4/tables/view-export-csv-xlsx-ics-print` = PAP-625.
