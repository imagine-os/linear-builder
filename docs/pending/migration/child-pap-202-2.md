---
key: "child/PAP-202/2"
title: "Airtable view mapping and wizard steps: filterByFormula parsing, kanban, calendar, gallery and form views, side-by-side review"
project: "migration"
parent: "PAP-202"
phase: "P2"
type: "Build"
priority: 2
size: "M"
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent5/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6"
identifier: "PAP-416"
status: "created"
createdAt: "2026-09-17"
---

# Airtable view mapping and wizard steps: filterByFormula parsing, kanban, calendar, gallery and form views, side-by-side review

**Goal**

Recreate an Airtable user's views as PaperOS saved views so the base feels the same on day one: filters, sorts, groups, hidden fields, colouring, kanban stack, calendar date and gallery cover, plus the Airtable-specific wizard steps and a side-by-side review screen.

**Scope**

In: `mapping/airtable-views.ts` to PAP-161 view definitions; `filterByFormula` parser for common patterns (`{Field} = 'x'`, `AND/OR`, `IS_AFTER`, `FIND`, `NOT`), unparsed filters reported; wizard steps `TableSelection` with row counts and `ViewImportToggle`; review screen showing Airtable screenshot (uploaded by the user, optional) beside the PaperOS view.

Out: automations, interfaces, comments.

**Spec**

* View kinds: grid, kanban, calendar, gallery, form (form becomes a PAP-168 form view).
* Unparseable filter keeps the view with a warning badge and the raw formula in the description.
* Hidden fields map to view field visibility; row colouring maps to `colorBy` select field.

**Interface contract**

Provides: `mapAirtableView(view, fields): ViewSpec | Partial`, `parseFilterByFormula(expr): FilterGroup | null`, wizard steps registered via PAP-199 child 3. Consumes: PAP-161 view model, child 2 field map, PAP-168 form view (soft). The filter parser is reusable by PAP-207 templates authored from Airtable bases.

**Definition of done**

* Six demo-base views recreated; two side-by-side screenshot pairs attached.
* 20 `filterByFormula` samples parsed or reported.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for base picker, translation report and resulting kanban.

**Test plan**

* Vitest: 20 filter samples, sort and group mapping, each view kind, hidden fields.
* Playwright: wizard from mocked OAuth to kanban view; visual baselines at seven widths, both themes; axe clean.
* Manual: compare two views with Airtable screenshots (attached).

**Demo**

Reviewer completes the Airtable wizard against the demo base with view import on and opens the recreated kanban grouped by Status with the same cards as Airtable. Under two minutes.

**Edge cases**

* View filter references a snapshotted formula field: filter kept on the snapshot text.
* Gallery cover field is not an attachment: warning, cover unset.
* More than 50 views: import toggles default to grid views only.

**Dependencies**

Children 1 and 2 (hard), PAP-161 (hard), PAP-168 (soft).

**Agent**

Built by Scout (Import Mapper) with Nova (Views Engineer). Reviewed by Sentinel (Visual Inspector, Code Reviewer).

**Size**

M
